from __future__ import annotations

import inspect
from collections.abc import Iterator
from enum import IntEnum
from typing import Any, Dict, List, NamedTuple, TypeVar

import astroid
import attrs
import networkx as nx
import pylint
from _pytest.fixtures import FixtureDef

PYLINT_VERSION_MAJOR = int(pylint.__version__.split(".")[0])


class AssignPair(NamedTuple):
    """A pair of an AssignAttr node and its Assign."""

    attr: astroid.AssignAttr
    assign: astroid.Assign


class FixtureScopes(IntEnum):
    """pytest fixture scopes."""

    SESSION = 1
    PACKAGE = 2
    MODULE = 3
    CLASS = 4
    FUNCTION = 5

    @classmethod
    def from_str(cls, scope: str) -> FixtureScopes:
        return cls[scope.upper()]

    def __str__(self) -> str:
        return self.name.lower()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"


@attrs.define
class FixtureProperties:
    """
    Properties of a pytest fixture.

    Some of them are our metadata, some are the actual fixture's properties.
    """

    autouse: bool = False
    scope: FixtureScopes = FixtureScopes.FUNCTION
    deps: set[astroid.FunctionDef] = attrs.field(factory=set)
    assign_attrs: set[AssignPair] = attrs.field(factory=set)
    pre_evaluated: bool = False
    """fixture has been evaluated via ``evaluate_auto_fixtures``."""
    ast_evaluating: bool = False
    """fixture has started evaluation via pylint's AST walk."""
    name: str = ""
    """For debugging-complete purposes only."""


FixtureDict = Dict[str, List[FixtureDef[Any]]]
FixturesStructure = Dict[astroid.FunctionDef, FixtureProperties]
DefaultT = TypeVar("DefaultT")


def _is_pytest_mark_usefixtures(decorator):
    # expecting @pytest.mark.usefixture(...)
    try:
        if (
            isinstance(decorator, astroid.Call)
            and decorator.func.attrname == "usefixtures"
            and decorator.func.expr.attrname == "mark"
            and decorator.func.expr.expr.name == "pytest"
        ):
            return True
    except AttributeError:
        pass
    return False


def _is_pytest_mark(decorator):
    try:
        deco = decorator  # as attribute `@pytest.mark.trylast`
        if isinstance(decorator, astroid.Call):
            deco = decorator.func  # as function `@pytest.mark.skipif(...)`
        if deco.expr.attrname == "mark" and deco.expr.expr.name == "pytest":
            return True
    except AttributeError:
        pass
    return False


def _is_pytest_fixture(decorator, fixture=True, yield_fixture=True):
    to_check = set()

    if fixture:
        to_check.add("fixture")

    if yield_fixture:
        to_check.add("yield_fixture")

    def _check_attribute(attr):
        """
        handle astroid.Attribute, i.e., when the fixture function is
        used by importing the pytest module
        """
        return attr.attrname in to_check and attr.expr.name == "pytest"

    def _check_name(name_):
        """
        handle astroid.Name, i.e., when the fixture function is
        directly imported
        """
        function_name = name_.name
        module = decorator.root().globals.get(function_name, [None])[0]
        module_name = module.modname if module else None
        return function_name in to_check and module_name == "pytest"

    try:
        if isinstance(decorator, astroid.Name):
            # expecting @fixture
            return _check_name(decorator)
        if isinstance(decorator, astroid.Attribute):
            # expecting @pytest.fixture
            return _check_attribute(decorator)
        if isinstance(decorator, astroid.Call):
            func = decorator.func
            if isinstance(func, astroid.Name):
                # expecting @fixture(scope=...)
                return _check_name(func)
            # expecting @pytest.fixture(scope=...)
            return _check_attribute(func)

    except AttributeError:
        pass

    return False


def _is_fixture_function(node: astroid.FunctionDef) -> bool:
    """Is the function a pytest fixture?"""
    if node.decorators is None:
        return False

    return any(_is_pytest_fixture(decorator) for decorator in node.decorators.nodes)


def _get_fixture_kwarg(
    fn: astroid.FunctionDef, kwarg: str, default: DefaultT | None = None
) -> Any | DefaultT:
    try:
        for decorator in fn.decorators.nodes:
            if not isinstance(decorator, astroid.Call):
                continue

            for keyword in decorator.keywords or []:
                if keyword.arg == kwarg:
                    return keyword.value.value
    except AttributeError:
        pass

    return default


def _can_use_fixture(function):
    if isinstance(function, astroid.FunctionDef):
        if _is_test_function(function):
            return True

        if function.decorators:
            for decorator in function.decorators.nodes:
                # usefixture
                if _is_pytest_mark_usefixtures(decorator):
                    return True

                # fixture
                if _is_pytest_fixture(decorator):
                    return True

    return False


def _is_test_function(fn: astroid.FunctionDef):
    """If function name is like ``test_*`` or ``*_test``."""
    # ToDo: Read pytest configuration?
    #  https://doc.pytest.org/en/latest/reference/reference.html#confval-python_functions
    return fn.name.startswith("test_") or fn.name.endswith("_test")


def _is_same_module(fixtures, import_node, fixture_name):
    """Comparing pytest fixture node with astroid.ImportFrom"""
    try:
        for fixture in fixtures[fixture_name]:
            for import_from in import_node.root().globals[fixture_name]:
                module = inspect.getmodule(fixture.func)
                parent_import = import_from.parent.import_module(
                    import_from.modname, False, import_from.level
                )
                if module is not None and module.__file__ == parent_import.file:
                    return True
    except Exception:  # pylint: disable=broad-except
        pass
    return False


def fixtures_and_deps_in_topo_order(
    fixtures: FixturesStructure,
) -> Iterator[astroid.FunctionDef]:
    """
    Topologically sort fixtures and their dependencies.

    The function orders only the given fixtures.
    As such, if the user wants to order by scope,
    multiple "disjoint" fixtures, or any other criteria,
    make sure the input fixtures are already filtered accordingly.
    """
    dag: nx.DiGraph[astroid.FunctionDef] = nx.DiGraph()

    for fixture_fn, fixture_data in fixtures.items():
        dag.add_node(fixture_fn)

        for dep_fn in fixture_data.deps:
            dag.add_edge(dep_fn, fixture_fn)

    return nx.topological_sort(dag)
