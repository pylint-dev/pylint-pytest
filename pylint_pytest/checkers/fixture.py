import fnmatch
import io
import sys
from pathlib import Path
from typing import Set, Tuple

import astroid
import pytest
from pylint.checkers.variables import VariablesChecker

from ..utils import (
    _can_use_fixture,
    _is_pytest_fixture,
    _is_pytest_mark,
    _is_pytest_mark_usefixtures,
    _is_same_module,
)
from . import BasePytestChecker
from .types import FixtureDict, replacement_add_message

# TODO: support pytest python_files configuration
FILE_NAME_PATTERNS: Tuple[str, ...] = ("test_*.py", "*_test.py")
ARGUMENT_ARE_KEYWORD_ONLY = (
    "https://docs.pytest.org/en/stable/deprecations.html#pytest-fixture-arguments-are-keyword-only"
)


class FixtureCollector:
    # Same as ``_pytest.fixtures.FixtureManager._arg2fixturedefs``.
    fixtures: FixtureDict = {}
    errors: Set[pytest.CollectReport] = set()

    def pytest_sessionfinish(self, session):
        # pylint: disable=protected-access
        self.fixtures = session._fixturemanager._arg2fixturedefs

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
    _invoked_with_func_args: Set[str] = set()
    # Stores all invoked fixtures through @pytest.mark.usefixture(...)
    _invoked_with_usefixtures: Set[str] = set()
    _original_add_message = replacement_add_message

    def open(self):
        # patch VariablesChecker.add_message
        FixtureChecker._original_add_message = VariablesChecker.add_message
        VariablesChecker.add_message = FixtureChecker.patch_add_message

    def close(self):
        """restore & reset class attr for testing"""
        # restore add_message
        VariablesChecker.add_message = FixtureChecker._original_add_message
        FixtureChecker._original_add_message = replacement_add_message

        # reset fixture info storage
        FixtureChecker._pytest_fixtures = {}
        FixtureChecker._invoked_with_func_args = set()
        FixtureChecker._invoked_with_usefixtures = set()

    def visit_module(self, node):
        """
        - only run once per module
        - invoke pytest session to collect available fixtures
        - create containers for the module to store args and fixtures
        """
        FixtureChecker._pytest_fixtures = {}
        FixtureChecker._invoked_with_func_args = set()
        FixtureChecker._invoked_with_usefixtures = set()

        is_test_module = False
        for pattern in FILE_NAME_PATTERNS:
            if fnmatch.fnmatch(Path(node.file).name, pattern):
                is_test_module = True
                break

        stdout, stderr = sys.stdout, sys.stderr
        try:
            with io.StringIO() as captured_stdout, io.StringIO() as captured_stderr:
                # suppress any future output from pytest
                sys.stderr = captured_stderr
                sys.stdout = captured_stdout

                # run pytest session with customized plugin to collect fixtures
                fixture_collector = FixtureCollector()

                # save and restore sys.path to prevent pytest.main from altering it
                sys_path = sys.path.copy()

                ret = pytest.main(
                    [
                        node.file,
                        "--fixtures",
                        "--collect-only",
                        "--pythonwarnings=ignore:Module already imported:pytest.PytestWarning",
                    ],
                    plugins=[fixture_collector],
                )

                # restore sys.path
                sys.path = sys_path

                FixtureChecker._pytest_fixtures = fixture_collector.fixtures

                legitimate_failure_paths = set(
                    collection_report.nodeid
                    for collection_report in fixture_collector.errors
                    if any(
                        fnmatch.fnmatch(
                            Path(collection_report.nodeid).name,
                            pattern,
                        )
                        for pattern in FILE_NAME_PATTERNS
                    )
                )
                if (ret != pytest.ExitCode.OK or legitimate_failure_paths) and is_test_module:
                    files_to_report = {
                        str(Path(x).absolute().relative_to(Path.cwd()))
                        for x in legitimate_failure_paths | {node.file}
                    }

                    self.add_message(
                        "cannot-enumerate-pytest-fixtures",
                        args=(
                            " ".join(files_to_report),
                            captured_stdout.getvalue(),
                            captured_stderr.getvalue(),
                        ),
                        node=node,
                    )
        finally:
            # restore output devices
            sys.stdout, sys.stderr = stdout, stderr

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
        if _can_use_fixture(node):
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

    # pylint: disable=bad-staticmethod-argument,too-many-branches # The function itself is an if-return logic.
    @staticmethod
    def patch_add_message(
        self, msgid, line=None, node=None, args=None, confidence=None, col_offset=None
    ):
        """
        - intercept and discard unwanted warning messages
        """
        # check W0611 unused-import
        if msgid == "unused-import":
            # actual attribute name is not passed as arg so...dirty hack
            # message is usually in the form of '%s imported from %s (as %)'
            message_tokens = args.split()
            fixture_name = message_tokens[0]

            # ignoring 'import %s' message
            if message_tokens[0] == "import" and len(message_tokens) == 2:
                pass

            # fixture is defined in other modules and being imported to
            # conftest for pytest magic
            elif (
                isinstance(node.parent, astroid.Module)
                and node.parent.name.split(".")[-1] == "conftest"
                and fixture_name in FixtureChecker._pytest_fixtures
            ):
                return

            # imported fixture is referenced in test/fixture func
            elif (
                fixture_name in FixtureChecker._invoked_with_func_args
                and fixture_name in FixtureChecker._pytest_fixtures
            ):
                if _is_same_module(
                    fixtures=FixtureChecker._pytest_fixtures,
                    import_node=node,
                    fixture_name=fixture_name,
                ):
                    return

            # fixture is referenced in @pytest.mark.usefixtures
            elif (
                fixture_name in FixtureChecker._invoked_with_usefixtures
                and fixture_name in FixtureChecker._pytest_fixtures
            ):
                if _is_same_module(
                    fixtures=FixtureChecker._pytest_fixtures,
                    import_node=node,
                    fixture_name=fixture_name,
                ):
                    return

        # check W0613 unused-argument
        if (
            msgid == "unused-argument"
            and _can_use_fixture(node.parent.parent)
            and isinstance(node.parent, astroid.Arguments)
        ):
            if node.name in FixtureChecker._pytest_fixtures:
                # argument is used as a fixture
                return

            fixnames = (
                arg.name for arg in node.parent.args if arg.name in FixtureChecker._pytest_fixtures
            )
            for fixname in fixnames:
                if node.name in FixtureChecker._pytest_fixtures[fixname][0].argnames:
                    # argument is used by a fixture
                    return

        # check W0621 redefined-outer-name
        if (
            msgid == "redefined-outer-name"
            and _can_use_fixture(node.parent.parent)
            and isinstance(node.parent, astroid.Arguments)
            and node.name in FixtureChecker._pytest_fixtures
        ):
            return

        FixtureChecker._original_add_message(self, msgid, line, node, args, confidence, col_offset)
