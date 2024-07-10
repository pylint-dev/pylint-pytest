from pylint_pytest.checkers.fixture import FixtureChecker

from .base_tester import BasePytestTester


class TestPytestMarkUsefixtures(BasePytestTester):
    CHECKER_CLASS = FixtureChecker
    MSG_ID = "useless-pytest-mark-decorator"

    def test_mark_usefixture_using_for_test(self):
        self.run_linter(enable_plugin=True)
        self.verify_messages(0)

    def test_mark_usefixture_using_for_class(self):
        self.run_linter(enable_plugin=True)
        self.verify_messages(0)

    def test_mark_usefixture_using_for_fixture_attribute(self):
        self.run_linter(enable_plugin=True)
        self.verify_messages(2)

    def test_mark_usefixture_using_for_fixture_function(self):
        self.run_linter(enable_plugin=True)
        self.verify_messages(2)

    def test_other_marks_using_for_fixture(self):
        self.run_linter(enable_plugin=True)
        self.verify_messages(4)

    def test_not_pytest_marker(self):
        self.run_linter(enable_plugin=True)
        self.verify_messages(0)
