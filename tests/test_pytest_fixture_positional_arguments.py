from base_tester import BasePytestTester

from pylint_pytest.checkers.fixture import FixtureChecker


class TestDeprecatedPytestFixtureScopeAsPositionalParam(BasePytestTester):
    CHECKER_CLASS = FixtureChecker
    MSG_ID = "deprecated-positional-argument-for-pytest-fixture"

    def test_with_args_scope(self):
        self.run_linter(enable_plugin=True)
        self.verify_messages(1)

    def test_with_kwargs_scope(self):
        self.run_linter(enable_plugin=True)
        self.verify_messages(0)

    def test_without_scope(self):
        self.run_linter(enable_plugin=True)
        self.verify_messages(0)
