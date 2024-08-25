from __future__ import annotations

import sys
import traceback
from collections import defaultdict
from collections.abc import Sequence
from typing import Literal, TypeVar

from astroid import nodes
from pylint.utils.ast_walker import AstCallback


class ASTVisitor:  # pylint: disable=too-few-public-methods
    """
    Thin interface for AST visitors.

    Used only for type-hinting purposes,
    and allow developers to navigate usages.
    """


ASTVisitorT = TypeVar("ASTVisitorT", bound=ASTVisitor)


class ASTWalker:
    """Almost-blatant copy from pylint.utils.ast_walker.ASTWalker."""

    VISIT_METH: Literal["visit_"] = "visit_"
    LEAVE_METH: Literal["leave_"] = "leave_"
    DEFAULT: Literal["default"] = "default"
    VISIT_DEFAULT = VISIT_METH + DEFAULT

    def __init__(self) -> None:
        self.visit_events: defaultdict[str, list[AstCallback]] = defaultdict(list)
        self.leave_events: defaultdict[str, list[AstCallback]] = defaultdict(list)
        self.exception_msg = False

    def add_visitor(self, visitor: ASTVisitorT) -> None:
        """Walk to the visitor's dir and collect the visit and leave methods."""
        vcids: set[str] = set()
        for member in dir(visitor):
            if (cid := member[6:]) == self.DEFAULT:
                continue

            if member.startswith(self.VISIT_METH):
                v_meth = getattr(visitor, member)
                self.visit_events[cid].append(v_meth)
                vcids.add(cid)

            elif member.startswith(self.LEAVE_METH):
                l_meth = getattr(visitor, member)
                self.leave_events[cid].append(l_meth)

        if visit_default := getattr(visitor, self.VISIT_DEFAULT, None):
            for cls in nodes.ALL_NODE_CLASSES:
                if (cid := cls.__name__.lower()) not in vcids:
                    self.visit_events[cid].append(visit_default)
        # For now, we have no "leave_default" method in Pylint

    def walk(self, astroid: nodes.NodeNG) -> None:
        """
        Call visit events of astroid checkers for the given node,
        recurse on its children, then leave events.
        """
        cid = astroid.__class__.__name__.lower()

        # Detect if the node is a new name for a deprecated alias.
        # In this case, favour the methods for the deprecated
        # alias if any,  in order to maintain backwards
        # compatibility.
        visit_events: Sequence[AstCallback] = self.visit_events.get(cid, ())
        leave_events: Sequence[AstCallback] = self.leave_events.get(cid, ())

        try:
            # generate events for this node on each checker
            for callback in visit_events:
                callback(astroid)
            # recurse on children
            for child in astroid.get_children():
                self.walk(child)
            for callback in leave_events:
                callback(astroid)
        except Exception:
            if self.exception_msg is False:
                file = getattr(astroid.root(), "file", None)
                print(
                    f"Exception on node {astroid!r} in file '{file}'",
                    file=sys.stderr,
                )
                traceback.print_exc()
                self.exception_msg = True
            raise
