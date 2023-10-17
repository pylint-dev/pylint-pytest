from __future__ import annotations

from astroid import Assign, Attribute, ClassDef, Name
from pylint.interfaces import IAstroidChecker

from ..utils import _can_use_fixture, _is_class_autouse_fixture
from . import BasePytestChecker


class ClassAttrLoader(BasePytestChecker):
    __implements__ = IAstroidChecker
    msgs = {"E6400": ("", "pytest-class-attr-loader", "")}

    in_setup = False
    request_cls: set[str] = set()
    class_node: ClassDef | None = None

    def visit_functiondef(self, node):
        """determine if a method is a class setup method"""
        self.in_setup = False
        self.request_cls = set()
        self.class_node = None

        if _can_use_fixture(node) and _is_class_autouse_fixture(node):
            self.in_setup = True
            self.class_node = node.parent

    def visit_assign(self, node: Assign):
        """store the aliases for `cls`"""
        if (
            self.in_setup
            and isinstance(node.value, Attribute)
            and node.value.attrname == "cls"
            and isinstance(node.value.expr, Name)
            and node.value.expr.name == "request"
        ):
            # storing the aliases for cls from request.cls
            self.request_cls = set(t.name for t in node.targets)

    def visit_assignattr(self, node):
        if (
            self.in_setup
            and isinstance(node.expr, Name)
            and node.expr.name in self.request_cls
            and self.class_node is not None
            and node.attrname not in self.class_node.locals
        ):
            try:
                # find Assign node which contains the source "value"
                assign_node = node
                while not isinstance(assign_node, Assign):
                    assign_node = assign_node.parent

                # hack class locals
                self.class_node.locals[node.attrname] = [assign_node.value]
            except Exception:  # pylint: disable=broad-except
                # cannot find valid assign expr, skipping the entire attribute
                pass
