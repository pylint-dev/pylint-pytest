import pytest

from pylint_pytest.checkers.fixture import FixtureChecker
from pylint_pytest.checkers.variables import CustomVariablesChecker

from .base_tester import BasePytestTester


class TestUnusedImport(BasePytestTester):
    CHECKER_CLASS = FixtureChecker
    IMPACTED_CHECKER_CLASSES = [CustomVariablesChecker]
    MSG_ID = "unused-import"

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_smoke(self, enable_plugin):
        self.run_linter(enable_plugin)
        self.verify_messages(0 if enable_plugin else 1)

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_caller_yield_fixture(self, enable_plugin):
        self.run_linter(enable_plugin)
        self.verify_messages(0 if enable_plugin else 1)

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_same_name_arg(self, enable_plugin):
        """an unused import (not a fixture) just happened to have the same
        name as fixture - should still raise unused-import warning"""
        self.run_linter(enable_plugin)
        self.verify_messages(1)

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_same_name_decorator(self, enable_plugin):
        """an unused import (not a fixture) just happened to have the same
        name as fixture - should still raise unused-import warning"""
        self.run_linter(enable_plugin)
        self.verify_messages(1)

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_conftest(self, enable_plugin):
        """fixtures are defined in different modules and imported to conftest
        for pytest to do its magic"""
        self.run_linter(enable_plugin)
        self.verify_messages(0 if enable_plugin else 1)

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_module(self, enable_plugin):
        """an unused module import shall still be an error"""
        self.run_linter(enable_plugin)
        self.verify_messages(1)

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_mark_usesfixtures(self, enable_plugin):
        """an unused module import shall still be an error"""
        self.run_linter(enable_plugin)
        self.verify_messages(0 if enable_plugin else 1)
