from __future__ import annotations

from typing import cast

from astroid import Assign, AssignAttr, Attribute, ClassDef, FunctionDef, Name, NodeNG

from pylint_pytest.checkers import BasePytestChecker
from pylint_pytest.utils.ast_walker import ASTVisitor, ASTWalker
from pylint_pytest.utils.pytest_logic import (
    AssignPair,
    FixtureProperties,
    FixtureScopes,
    FixturesStructure,
    _get_fixture_kwarg,
    _is_fixture_function,
    _is_test_function,
    fixtures_and_deps_in_topo_order,
)

CLASS_CONVENTIONAL_NAME = "cls"
REQUEST_FIXTURE_NAME = "request"


def _is_request_cls(attr_node: NodeNG) -> bool:
    """Is node exactly ``request.cls.*``?"""

    return (
        isinstance(attr_node, Attribute)
        and attr_node.attrname == CLASS_CONVENTIONAL_NAME
        and isinstance(attr_node.expr, Name)
        and attr_node.expr.name == REQUEST_FIXTURE_NAME
    )


class ClassAttrLoader(BasePytestChecker):
    """
    This checker is responsible for pre-processing any class-defined fixtures,
    and ensure that test classes' ``self`` see the attributes defined in the fixtures.

    The algorithm is as follows:

    #. When visiting a testing file, from top to bottom
    #. When visiting a testing class
        #. Collect all fixtures, their properties
        #. Calculate the dependencies between fixtures
        #. Evaluate auto fixtures in scope-order.
            #. Use ``nx.DiGraph`` to topologically sort the fixtures.
            #. Evaluate the fixtures in order
            #. Use a thin ``FixtureVisitor`` to evaluate the fixtures.
        #. Resume the class visitation
    #. When visiting a fixture or a test function
        #. Evaluate any reference-by-name fixture requested.
        #. For fixtures:
            #. Mark a fixture as AST-evaluated.
            #. Apply any hacks, as-visited
        #. When leaving, revert any hacks applied in this scope.
    """

    msgs = {"E6400": ("", "pytest-class-attr-loader", "")}

    class_node: ClassDef | None = None
    fixtures: FixturesStructure = {}

    curr_fixture: FunctionDef | None = None
    request_cls_aliases: set[str] = set()

    ooo_applied_assigns: set[AssignPair] = set()

    def visit_classdef(self, node: ClassDef):
        if not (node.name.lower().startswith("test") or "unittest.TestCase" in node.basenames):
            return

        self.class_node = node

        for fn_node in node.nodes_of_class(FunctionDef):
            if not _is_fixture_function(fn_node):
                continue

            self.fixtures[fn_node] = FixtureProperties(
                name=repr(fn_node),
                autouse=_get_fixture_kwarg(fn_node, "autouse", False),
                scope=FixtureScopes.from_str(
                    _get_fixture_kwarg(fn_node, "scope", str(FixtureScopes.FUNCTION))
                ),
            )

        for fixture_fn, fixture_data in self.fixtures.items():
            for param in fixture_fn.args.args:
                for other_fn, _ in self.fixtures.items():
                    if param.name is other_fn.name:
                        fixture_data.deps.add(other_fn)

        self.evaluate_auto_fixtures()

    def leave_classdef(self, _node: ClassDef):
        self.fixtures.clear()
        self.class_node = None

    def evaluate_auto_fixtures(self):
        for scope in FixtureScopes:
            filtered_fixtures = {f: d for f, d in self.fixtures.items() if d.scope == scope}
            order = fixtures_and_deps_in_topo_order(filtered_fixtures)

            for fixture_fn in order:
                if not self.fixtures[fixture_fn].autouse:
                    continue

                if self.fixtures[fixture_fn].pre_evaluated:
                    continue

                self.walk_fixture(fixture_fn)

    def walk_fixture(self, fixture_fn: FunctionDef):
        walker = ASTWalker()
        walker.add_visitor(FixtureVisitor(fixture_fn, self))
        walker.walk(fixture_fn)
        self.fixtures[fixture_fn].pre_evaluated = True
        self.curr_fixture = None
        self.request_cls_aliases.clear()

    def __add_to_locals(self, dest_node: AssignAttr, value_node: Assign):
        self.class_node = cast(ClassDef, self.class_node)  # XXX: Cannot fight anymore
        self.class_node.locals[dest_node.attrname] = [value_node.value]

    def visit_functiondef(self, fn_node: FunctionDef):
        if not self.class_node or (not _is_test_function(fn_node) and fn_node not in self.fixtures):
            return

        self.__ooo_apply_fixtures(fn_node)
        if _is_test_function(fn_node):
            return

        if not self.fixtures[fn_node].pre_evaluated:
            self.walk_fixture(fn_node)

        self.curr_fixture = fn_node
        self.fixtures[fn_node].ast_evaluating = True

    def __ooo_apply_fixtures(self, fn_node: FunctionDef):
        """
        Apply all relevant fixtures to the current function's class' namespace.
        """
        sort_fixtures: FixturesStructure = {}

        # Detect any referenced fixtures in function arguments
        for arg in fn_node.args.args:
            for fixture_fn, fixture_data in self.fixtures.items():
                if arg.name != fixture_fn.name:
                    continue

                sort_fixtures[fixture_fn] = fixture_data

        # Add all autouse fixtures
        sort_fixtures.update(
            {f: d for f, d in self.fixtures.items() if d.autouse and f is not fn_node}
        )

        sorted_fixtures = fixtures_and_deps_in_topo_order(sort_fixtures)

        for fixture_fn in sorted_fixtures:
            fixture_data = self.fixtures[fixture_fn]

            if not fixture_data.pre_evaluated:
                # Not pre-evaluated, so that means
                # we have no ``fixture_data.assign_attrs``.
                self.walk_fixture(fixture_fn)

            for pair in fixture_data.assign_attrs:
                self.__add_to_locals(pair.attr, pair.assign)
                self.ooo_applied_assigns.add(pair)

    def leave_functiondef(self, fn_node: FunctionDef):
        if not self.class_node:
            return

        for pair in self.ooo_applied_assigns:
            del self.class_node.locals[pair.attr.attrname]

        self.ooo_applied_assigns.clear()

        if fn_node in self.fixtures:
            self.curr_fixture = None
            self.request_cls_aliases.clear()

    def visit_assign(self, node: Assign):
        if not self.curr_fixture or not _is_request_cls(node.value):
            return

        self.request_cls_aliases = set(t.name for t in node.targets)

    def visit_assignattr(self, node: AssignAttr):
        # "Intra"-apply any `request.cls.X` assign "also" to `self.X`.
        # "External" apply is handled in ``self.__ooo_apply_fixtures``.
        self.class_node = cast(ClassDef, self.class_node)  # XXX: Cannot fight anymore
        if not self.eligible_for_assignattr_visit(node) or node.attrname in self.class_node.locals:
            return

        # We did all the heavy lifting in the FixtureVisitor; now, to hack:
        for pair in self.fixtures[self.curr_fixture].assign_attrs:
            if pair.attr is node:
                self.__add_to_locals(pair.attr, pair.assign)
                return

    def eligible_for_assignattr_visit(self, node: AssignAttr) -> bool:
        return (
            self.class_node is not None
            and self.curr_fixture is not None
            and (self.is_node_request_cls_alias(node) or _is_request_cls(node.expr))
        )

    def is_node_request_cls_alias(self, node: AssignAttr) -> bool:
        """Is node a ``var``, where ``var = request.cls``?"""
        return isinstance(node.expr, Name) and node.expr.name in self.request_cls_aliases


class FixtureVisitor(ASTVisitor):
    def __init__(self, fixture: FunctionDef, checker: ClassAttrLoader):
        self.checker = checker
        self.checker.curr_fixture = fixture

    def visit_assign(self, node: Assign):
        self.checker.visit_assign(node)

    def visit_assignattr(self, node: AssignAttr):
        if not self.checker.eligible_for_assignattr_visit(node):
            return

        try:
            # Find the ``Assign`` node, which contains the source "value"
            assign_node = node
            while not isinstance(assign_node, Assign):
                assign_node = assign_node.parent

            # When the time comes, we will hack the class locals
            self.checker.fixtures[self.checker.curr_fixture].assign_attrs.add(
                AssignPair(node, assign_node)
            )
        except Exception:  # pylint: disable=broad-except
            # Cannot find a valid assign expr, skipping the entire attribute
            pass
