import pylint
from pylint.checkers import BaseChecker


class BasePytestChecker(BaseChecker):
    if int(pylint.version.split(".")[0]) < 3:
        # Since https://github.com/pylint-dev/pylint/pull/8404, pylint does not need this
        # __implements__ pattern. keeping it for retro compatibility with pylint==2.x
        from pylint.interfaces import IAstroidChecker  # pylint: disable=import-outside-toplevel

        __implements__ = IAstroidChecker

    name = "pylint-pytest"
