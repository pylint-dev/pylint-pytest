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


@pytest.fixture
def fixture_collections(monkeypatch):
    """The calls to ``pytest.main`` that collect fixtures, so import the linted module."""
    calls = []
    real_main = pytest.main

    def spy_main(args, *other_args, **kwargs):
        if "--fixtures" in args:
            calls.append(args)
        return real_main(args, *other_args, **kwargs)

    monkeypatch.setattr(pytest, "main", spy_main)
    return calls


class TestCollectOnlyPytestModules(BasePytestTester):
    """Fixtures are only collected (by importing the module) where pytest needs them.

    https://github.com/pylint-dev/pylint-pytest/issues/68
    """

    CHECKER_CLASS = FixtureChecker
    IMPACTED_CHECKER_CLASSES = [CustomVariablesChecker]
    MSG_ID = "default-naming"

    def test_import_runs_code(self, fixture_collections, capsys):
        self.run_linter(enable_plugin=True)

        assert not fixture_collections
        assert "banana" not in capsys.readouterr().out
        self.verify_messages(0, msg_id="cannot-enumerate-pytest-fixtures")

    def test_fixture_in_helper_module(self, fixture_collections):
        self.run_linter(enable_plugin=True)

        assert len(fixture_collections) == 1
        # ``fruit_basket(apple)`` is a fixture using a fixture, not a shadowed name.
        self.verify_messages(0, msg_id="redefined-outer-name")


class TestCustomNaming(BasePytestTester):
    """The ``python_files``, ``python_classes`` and ``python_functions`` options of pytest are used.

    ``custom-naming/pytest.ini`` sets them to ``check_*.py``, ``Check`` and ``check_*``.
    """

    CHECKER_CLASS = FixtureChecker
    IMPACTED_CHECKER_CLASSES = [CustomVariablesChecker]
    MSG_ID = "custom-naming"

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_check_fruit(self, enable_plugin, fixture_collections):
        self.run_linter(enable_plugin)

        assert len(fixture_collections) == int(enable_plugin)
        self.verify_messages(0 if enable_plugin else 1, msg_id="unused-argument")

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_fruit_basket(self, enable_plugin, fixture_collections):
        self.run_linter(enable_plugin)

        assert len(fixture_collections) == int(enable_plugin)
        self.verify_messages(0 if enable_plugin else 1, msg_id="unused-argument")

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_fruit_salad(self, enable_plugin, fixture_collections):
        self.run_linter(enable_plugin)

        assert len(fixture_collections) == int(enable_plugin)
        self.verify_messages(0 if enable_plugin else 1, msg_id="unused-argument")

    def test_eat_cherry(self, fixture_collections, capsys):
        self.run_linter(enable_plugin=True)

        assert not fixture_collections
        assert "cherry" not in capsys.readouterr().out
        # ``test_cherry`` is not a test, so ``fruit`` is not a fixture it uses.
        self.verify_messages(1, msg_id="unused-argument")
