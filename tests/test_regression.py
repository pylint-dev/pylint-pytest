import pytest

from pylint_pytest.checkers.fixture import FixtureChecker
from pylint_pytest.checkers.variables import CustomVariablesChecker

from .base_tester import BasePytestTester


class TestRegression(BasePytestTester):
    """Covering some behaviors that shouldn't get impacted by the plugin"""

    CHECKER_CLASS = FixtureChecker
    IMPACTED_CHECKER_CLASSES = [CustomVariablesChecker]
    MSG_ID = "regression"

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_import_twice(self, enable_plugin):
        """catch a coding error when using fixture + if + inline import"""
        self.run_linter(enable_plugin)

        self.verify_messages(2, msg_id="unused-import")
        self.verify_messages(1, msg_id="redefined-outer-name")
