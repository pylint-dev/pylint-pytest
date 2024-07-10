from pylint.checkers import BaseChecker

from pylint_pytest.utils import PYLINT_VERSION_MAJOR


class BasePytestChecker(BaseChecker):
    if PYLINT_VERSION_MAJOR < 3:
        # todo(maybe-remove): if we only support pylint>=3
        # Since https://github.com/pylint-dev/pylint/pull/8404, pylint does not need this
        # __implements__ pattern. keeping it for retro compatibility with pylint==2.x
        # pylint: disable=import-outside-toplevel,no-name-in-module
        from pylint.interfaces import (  # type: ignore[attr-defined] # It is defined in pylint~=2
            IAstroidChecker,
        )

        __implements__ = IAstroidChecker

    name = "pylint-pytest"
