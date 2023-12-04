from pylint.checkers.variables import VariablesChecker
from pylint.lint import PyLinter

from .checkers.class_attr_loader import ClassAttrLoader
from .checkers.fixture import FixtureChecker
from .checkers.variables import CustomVariablesChecker


def register(linter: PyLinter) -> None:
    """Register the checker classes"""
    remove_original_variables_checker(linter)
    linter.register_checker(CustomVariablesChecker(linter))
    linter.register_checker(FixtureChecker(linter))
    linter.register_checker(ClassAttrLoader(linter))


def remove_original_variables_checker(linter: PyLinter) -> None:
    """We need to remove VariablesChecker before registering CustomVariablesChecker"""
    variable_checkers = linter._checkers[VariablesChecker.name]  # pylint: disable=protected-access
    for checker in [x for x in variable_checkers if isinstance(x, VariablesChecker)]:
        variable_checkers.remove(checker)
