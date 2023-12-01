import pytest
from base_tester import BasePytestTester
from pylint.checkers.variables import VariablesChecker

from pylint_pytest.checkers.fixture import FixtureChecker
from pylint_pytest.utils import PYLINT_VERSION_MAJOR


class TestRegression(BasePytestTester):
    """Covering some behaviors that shouldn't get impacted by the plugin"""

    CHECKER_CLASS = FixtureChecker
    IMPACTED_CHECKER_CLASSES = [VariablesChecker]
    MSG_ID = "regression"

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_import_twice(self, enable_plugin):
        """catch a coding error when using fixture + if + inline import"""
        self.run_linter(enable_plugin)

        if PYLINT_VERSION_MAJOR < 2:  # todo(maybe-remove): if we only support pylint>=2
            # for some reason pylint 1.9.5 does not raise unused-import for inline import
            self.verify_messages(1, msg_id="unused-import")
        else:
            self.verify_messages(2, msg_id="unused-import")
        self.verify_messages(1, msg_id="redefined-outer-name")
