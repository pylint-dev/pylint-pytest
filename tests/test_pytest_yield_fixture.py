from base_tester import BasePytestTester

from pylint_pytest.checkers.fixture import FixtureChecker


class TestDeprecatedPytestYieldFixture(BasePytestTester):
    CHECKER_CLASS = FixtureChecker
    IMPACTED_CHECKER_CLASSES = []
    MSG_ID = "deprecated-pytest-yield-fixture"

    def test_smoke(self):
        self.run_linter(enable_plugin=True)
        self.verify_messages(1)

    def test_func(self):
        self.run_linter(enable_plugin=True)
        self.verify_messages(2)
