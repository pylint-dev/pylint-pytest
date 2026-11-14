from __future__ import annotations

import io
import sys
from pathlib import Path

import astroid
import pytest
from astroid import nodes

from ..utils import (
    DEFAULT_NAMING,
    PytestNaming,
    _can_use_fixture,
    _is_pytest_fixture,
    _is_pytest_mark,
    _is_pytest_mark_usefixtures,
)
from . import BasePytestChecker
from .types import FixtureDict

ARGUMENT_ARE_KEYWORD_ONLY = (
    "https://docs.pytest.org/en/stable/deprecations.html#pytest-fixture-arguments-are-keyword-only"
)
PYTEST_ARGS = (
    "--collect-only",
    "--quiet",
    "-p",
    "no:unraisableexception",
    "--pythonwarnings=ignore:Module already imported:pytest.PytestWarning",
)


def _may_hold_pytest_code(module: nodes.Module, naming: PytestNaming) -> bool:
    """Whether pytest could need ``module`` to know its fixtures.

    True for ``conftest.py``, a module declaring ``pytest_plugins``, and a
    module defining fixtures or tests.
    """
    if Path(module.file).name == "conftest.py" or "pytest_plugins" in module.locals:
        return True
    for child in module.body:
        if isinstance(child, nodes.ClassDef) and naming.is_test_class(child.name):
            return True
    for function in module.nodes_of_class(nodes.FunctionDef):
        if naming.is_test_function(function.name):
            return True
        if function.decorators and any(
            _is_pytest_fixture(decorator) for decorator in function.decorators.nodes
        ):
            return True
    return False


class NamingCollector:
    """Read the naming options of pytest, without collecting (so importing) anything."""

    naming: PytestNaming = DEFAULT_NAMING

    def pytest_configure(self, config):
        self.naming = PytestNaming(
            files=tuple(config.getini("python_files")),
            classes=tuple(config.getini("python_classes")),
            functions=tuple(config.getini("python_functions")),
        )

    @pytest.hookimpl(tryfirst=True)
    def pytest_collection(self, session):  # pylint: disable=no-self-use,unused-argument
        return True


class FixtureCollector:
    # Same as ``_pytest.fixtures.FixtureManager._arg2fixturedefs`` (pytest < 9.2).
    fixtures: FixtureDict = {}
    errors: set[pytest.CollectReport] = set()

    rootpath: Path = Path.cwd()

    def __init__(self) -> None:
        # Per run: a class-level set would keep the errors of every module linted before
        self.errors = set()

    def pytest_sessionfinish(self, session):
        config = session.config
        self.rootpath = getattr(config, "rootpath", None) or Path(str(config.rootdir))
        # pylint: disable=protected-access
        fixturemanager = session._fixturemanager
        if hasattr(fixturemanager, "_arg2fixturedefs"):
            self.fixtures = fixturemanager._arg2fixturedefs
            return
        # pytest 9.2 files the FixtureDefs of each name under the node that
        # registers them; group them by name, as `pytest --fixtures` lists them.
        fixtures: FixtureDict = {}
        for fixturedef in fixturemanager._get_all_fixture_defs():
            fixtures.setdefault(fixturedef.argname, []).append(fixturedef)
        self.fixtures = fixtures

    def pytest_collectreport(self, report):
        if report.failed:
            self.errors.add(report)


class FixtureChecker(BasePytestChecker):
    msgs = {
        "W6401": (
            "Using a deprecated @pytest.yield_fixture decorator",
            "deprecated-pytest-yield-fixture",
            "Used when using a deprecated pytest decorator that has been deprecated in pytest-3.0",
        ),
        "W6402": (
            "Using useless `@pytest.mark.*` decorator for fixtures",
            "useless-pytest-mark-decorator",
            (
                "@pytest.mark.* decorators can't by applied to fixtures. "
                "Take a look at: https://docs.pytest.org/en/stable/reference.html#marks"
            ),
        ),
        "W6403": (
            "Using a deprecated positional arguments for fixture",
            "deprecated-positional-argument-for-pytest-fixture",
            (
                "Pass scope as a kwarg, not positional arg, which is deprecated in future pytest. "
                f"Take a look at: {ARGUMENT_ARE_KEYWORD_ONLY}"
            ),
        ),
        "F6401": (
            (
                "pylint-pytest plugin cannot enumerate and collect pytest fixtures. "
                "Please run `pytest --fixtures --collect-only %s` and resolve "
                "any potential syntax error or package dependency issues. stdout: %s. stderr: %s."
            ),
            "cannot-enumerate-pytest-fixtures",
            "Used when pylint-pytest has been unable to enumerate and collect pytest fixtures.",
        ),
    }

    # Store all fixtures discovered by pytest session
    _pytest_fixtures: FixtureDict = {}
    # Stores all used function arguments
    _invoked_with_func_args: set[str] = set()
    # Stores all invoked fixtures through @pytest.mark.usefixture(...)
    _invoked_with_usefixtures: set[str] = set()
    # The naming options of pytest for the module being linted
    _pytest_naming: PytestNaming = DEFAULT_NAMING
    # The naming options of pytest, by directory of the linted module
    _naming_by_directory: dict[Path, PytestNaming] = {}

    def close(self):
        """restore & reset class attr for testing"""
        # reset fixture info storage
        FixtureChecker._pytest_fixtures = {}
        FixtureChecker._invoked_with_func_args = set()
        FixtureChecker._invoked_with_usefixtures = set()
        FixtureChecker._pytest_naming = DEFAULT_NAMING
        FixtureChecker._naming_by_directory = {}

    @staticmethod
    def _run_pytest(args, plugin):
        """Run pytest in-process, keeping its output and its changes to ``sys.path`` out."""
        stdout, stderr = sys.stdout, sys.stderr
        sys_path = sys.path.copy()
        with io.StringIO() as captured_stdout, io.StringIO() as captured_stderr:
            sys.stdout, sys.stderr = captured_stdout, captured_stderr
            try:
                ret = pytest.main(args, plugins=[plugin])
            finally:
                sys.stdout, sys.stderr = stdout, stderr
                sys.path = sys_path
            return ret, captured_stdout.getvalue(), captured_stderr.getvalue()

    def _naming_for(self, file_path: str) -> PytestNaming:
        """The naming options of pytest for ``file_path``, read once per directory."""
        directory = Path(file_path).resolve().parent
        if directory not in FixtureChecker._naming_by_directory:
            naming_collector = NamingCollector()
            self._run_pytest([file_path, *PYTEST_ARGS], naming_collector)
            FixtureChecker._naming_by_directory[directory] = naming_collector.naming
        return FixtureChecker._naming_by_directory[directory]

    def visit_module(self, node):
        """
        - only run once per module
        - invoke pytest session to collect available fixtures
        - create containers for the module to store args and fixtures
        """
        FixtureChecker._pytest_fixtures = {}
        FixtureChecker._invoked_with_func_args = set()
        FixtureChecker._invoked_with_usefixtures = set()

        naming = FixtureChecker._pytest_naming = self._naming_for(node.file)
        is_test_module = naming.is_test_file(node.file)
        if not is_test_module and not _may_hold_pytest_code(node, naming):
            # Collecting fixtures imports the module, which runs its top-level
            # code (``__main__.py``, ``setup.py``...). Pylint should not run
            # code that pytest itself would never collect.
            return

        # run pytest session with customized plugin to collect fixtures
        fixture_collector = FixtureCollector()
        ret, stdout, stderr = self._run_pytest(
            [node.file, "--fixtures", *PYTEST_ARGS], fixture_collector
        )
        FixtureChecker._pytest_fixtures = fixture_collector.fixtures

        # Node ids are relative to the rootdir of pytest, not to the working directory
        failed_paths = {
            fixture_collector.rootpath / collection_report.nodeid
            for collection_report in fixture_collector.errors
        }
        legitimate_failure_paths = {path for path in failed_paths if naming.is_test_file(path)}
        if (ret != pytest.ExitCode.OK or legitimate_failure_paths) and is_test_module:
            files_to_report = {
                str(Path(x).absolute().relative_to(Path.cwd()))
                for x in legitimate_failure_paths | {Path(node.file)}
            }

            self.add_message(
                "cannot-enumerate-pytest-fixtures",
                args=(" ".join(files_to_report), stdout, stderr),
                node=node,
            )

    def visit_decorators(self, node):
        """
        Walk through all decorators on functions.
        Tries to find cases:
            When uses `@pytest.fixture` with `scope` as positional argument (deprecated)
            https://docs.pytest.org/en/stable/deprecations.html#pytest-fixture-arguments-are-keyword-only
                >>> @pytest.fixture("module")
                >>> def awesome_fixture(): ...
                Instead
                >>> @pytest.fixture(scope="module")
                >>> def awesome_fixture(): ...
            When uses `@pytest.mark.usefixtures` for fixture (useless because didn't work)
            https://docs.pytest.org/en/stable/reference.html#marks
                >>> @pytest.mark.usefixtures("another_fixture")
                >>> @pytest.fixture
                >>> def awesome_fixture(): ...
        Parameters
        ----------
        node : astroid.scoped_nodes.Decorators
        """
        uses_fixture_deco, uses_mark_deco = False, False
        for decorator in node.nodes:
            try:
                if (
                    _is_pytest_fixture(decorator)
                    and isinstance(decorator, astroid.Call)
                    and decorator.args
                ):
                    self.add_message(
                        "deprecated-positional-argument-for-pytest-fixture",
                        node=decorator,
                    )
                uses_fixture_deco |= _is_pytest_fixture(decorator)
                uses_mark_deco |= _is_pytest_mark(decorator)
            except AttributeError:
                # ignore any parse exceptions
                pass
        if uses_mark_deco and uses_fixture_deco:
            self.add_message("useless-pytest-mark-decorator", node=node)

    def visit_functiondef(self, node):
        """
        - save invoked fixtures for later use
        - save used function arguments for later use
        """
        if _can_use_fixture(node, self._pytest_naming):
            if node.decorators:
                # check all decorators
                for decorator in node.decorators.nodes:
                    if _is_pytest_mark_usefixtures(decorator):
                        # save all visited fixtures
                        for arg in decorator.args:
                            self._invoked_with_usefixtures.add(arg.value)
                    if int(pytest.__version__.split(".")[0]) >= 3 and _is_pytest_fixture(
                        decorator, fixture=False
                    ):
                        # raise deprecated warning for @pytest.yield_fixture
                        self.add_message("deprecated-pytest-yield-fixture", node=node)
            for arg in node.args.args:
                self._invoked_with_func_args.add(arg.name)
