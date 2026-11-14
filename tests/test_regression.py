import pytest

import pylint_pytest.checkers.fixture
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


class TestCollectOnlyPytestModules(BasePytestTester):
    """Fixtures are only collected (by importing the module) where pytest needs them.

    https://github.com/pylint-dev/pylint-pytest/issues/68
    """

    CHECKER_CLASS = FixtureChecker
    IMPACTED_CHECKER_CLASSES = [CustomVariablesChecker]
    MSG_ID = "regression"

    @pytest.fixture(autouse=True)
    def pytest_main_calls(self, monkeypatch):  # pylint: disable=no-self-use
        # ``base_tester`` makes every input a test file: restore the real patterns.
        monkeypatch.setattr(
            pylint_pytest.checkers.fixture, "FILE_NAME_PATTERNS", ("test_*.py", "*_test.py")
        )
        calls = []
        real_main = pytest.main

        def spy_main(*args, **kwargs):
            calls.append(args)
            return real_main(*args, **kwargs)

        monkeypatch.setattr(pytest, "main", spy_main)
        return calls

    def test_import_runs_code(self, pytest_main_calls, capsys):
        self.run_linter(enable_plugin=True)

        assert not pytest_main_calls
        assert "banana" not in capsys.readouterr().out
        self.verify_messages(0, msg_id="cannot-enumerate-pytest-fixtures")

    def test_fixture_in_helper_module(self, pytest_main_calls):
        self.run_linter(enable_plugin=True)

        assert len(pytest_main_calls) == 1
        # ``fruit_basket(apple)`` is a fixture using a fixture, not a shadowed name.
        self.verify_messages(0, msg_id="redefined-outer-name")
