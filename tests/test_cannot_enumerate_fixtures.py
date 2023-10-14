import pytest
from base_tester import BasePytestTester
from pylint.checkers.variables import VariablesChecker

from pylint_pytest.checkers.fixture import FixtureChecker


class TestCannotEnumerateFixtures(BasePytestTester):
    CHECKER_CLASS = FixtureChecker
    MSG_ID = "cannot-enumerate-pytest-fixtures"

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_no_such_package(self, enable_plugin):
        self.run_linter(enable_plugin)
        self.verify_messages(1 if enable_plugin else 0)

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_import_corrupted_module(self, enable_plugin):
        self.run_linter(enable_plugin)
        self.verify_messages(1 if enable_plugin else 0)
