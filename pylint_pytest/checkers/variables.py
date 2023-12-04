from typing import Any, Optional

from astroid import Arguments, Module
from astroid.nodes.node_ng import NodeNG
from pylint.checkers.variables import VariablesChecker
from pylint.interfaces import Confidence

from pylint_pytest.utils import _can_use_fixture, _is_same_module

from .fixture import FixtureChecker


class CustomVariablesChecker(VariablesChecker):
    """Overrides the default VariablesChecker of pylint to discard unwanted warning messages"""

    def add_message(
        self,
        msgid: str,
        line: Optional[int] = None,
        node: Optional[NodeNG] = None,
        args: Any = None,
        confidence: Confidence = None,
        col_offset: Optional[int] = None,
        end_lineno: Optional[int] = None,
        end_col_offset: Optional[int] = None,
    ) -> None:
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
                node
                and isinstance(node.parent, Module)
                and node.parent.name.split(".")[-1] == "conftest"
                and fixture_name in FixtureChecker.pytest_fixtures
            ):
                return

            # imported fixture is referenced in test/fixture func
            elif (
                fixture_name in FixtureChecker.invoked_with_func_args
                and fixture_name in FixtureChecker.pytest_fixtures
            ):
                if _is_same_module(
                    fixtures=FixtureChecker.pytest_fixtures,
                    import_node=node,
                    fixture_name=fixture_name,
                ):
                    return

            # fixture is referenced in @pytest.mark.usefixtures
            elif (
                fixture_name in FixtureChecker.invoked_with_usefixtures
                and fixture_name in FixtureChecker.pytest_fixtures
            ):
                if _is_same_module(
                    fixtures=FixtureChecker.pytest_fixtures,
                    import_node=node,
                    fixture_name=fixture_name,
                ):
                    return

        # check W0613 unused-argument
        if (
            msgid == "unused-argument"
            and node
            and _can_use_fixture(node.parent.parent)
            and isinstance(node.parent, Arguments)
        ):
            if node.name in FixtureChecker.pytest_fixtures:
                # argument is used as a fixture
                return

            fixnames = (
                arg.name for arg in node.parent.args if arg.name in FixtureChecker.pytest_fixtures
            )
            for fixname in fixnames:
                if node.name in FixtureChecker.pytest_fixtures[fixname][0].argnames:
                    # argument is used by a fixture
                    return

        # check W0621 redefined-outer-name
        if (
            msgid == "redefined-outer-name"
            and node
            and _can_use_fixture(node.parent.parent)
            and isinstance(node.parent, Arguments)
            and node.name in FixtureChecker.pytest_fixtures
        ):
            return

        super().add_message(msgid, line, node, args, confidence, col_offset)
