import re
from unittest.mock import Mock

import pytest
from astroid import AssignAttr, NodeNG, builder

from pylint_pytest.utils.ast_walker import ASTVisitor, ASTWalker


@pytest.fixture
def root_node():
    return builder.extract_node(
        """
        const = u"foo"
        """
    )


def test_walk_calls_correct_methods(root_node):
    class Visitor(ASTVisitor):
        def visit_default(self, node: NodeNG):
            pass

        def visit_assign(self, node: AssignAttr):
            pass

        def leave_assign(self, node: AssignAttr):
            pass

    visitor = Visitor()
    visitor.visit_default = Mock(wraps=visitor.visit_default)  # type: ignore[method-assign]
    visitor.visit_assign = Mock(wraps=visitor.visit_assign)  # type: ignore[method-assign]
    visitor.leave_assign = Mock(wraps=visitor.leave_assign)  # type: ignore[method-assign]

    ast_walker = ASTWalker()
    ast_walker.add_visitor(visitor)
    ast_walker.walk(root_node)

    assert visitor.visit_default.call_count == 2
    assert visitor.visit_assign.call_count == 1
    assert visitor.leave_assign.call_count == 1


@pytest.mark.parametrize("method", [ASTWalker.VISIT_METH, ASTWalker.LEAVE_METH])
def test_walk_raises_exceptions(capsys, root_node, method):
    ast_visitor = ASTVisitor()

    def meth(*args, **kwargs):  # pylint: disable=unused-argument
        return 1 / 0

    meth.__name__ = f"{method}assign"
    setattr(ast_visitor, meth.__name__, meth)

    ast_walker = ASTWalker()
    ast_walker.add_visitor(ast_visitor)
    with pytest.raises(ZeroDivisionError, match=r"^division by zero$"):
        ast_walker.walk(root_node)

    out, err = capsys.readouterr()
    assert not out
    assert re.search(r"Exception on node <Assign l.2 at 0x[\da-f]+> in file '<\?>'", err)
