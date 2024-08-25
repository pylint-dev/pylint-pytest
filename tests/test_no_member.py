import pytest
from pylint.checkers.typecheck import TypeChecker

from pylint_pytest.checkers.class_attr_loader import ClassAttrLoader

from .base_tester import BasePytestTester


class TestNoMember(BasePytestTester):
    CHECKER_CLASS = ClassAttrLoader
    IMPACTED_CHECKER_CLASSES = [TypeChecker]
    MSG_ID = "no-member"

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_fixture(self, enable_plugin):
        self.run_linter(enable_plugin)
        self.verify_messages(0 if enable_plugin else 1)

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_yield_fixture(self, enable_plugin):
        self.run_linter(enable_plugin)
        self.verify_messages(0 if enable_plugin else 1)

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_not_using_cls(self, enable_plugin):
        self.run_linter(enable_plugin)
        # l.13: ``print(self.klass)`` before ``request.cls.klass = "class"``.
        self.verify_messages(1 + (0 if enable_plugin else 7))

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_inheritance(self, enable_plugin):
        self.run_linter(enable_plugin)
        self.verify_messages(0 if enable_plugin else 1)

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_issue_74(self, enable_plugin):
        self.run_linter(enable_plugin)
        # l.9: ``print(self.username)`` before ``request.cls.username = "dylan"``
        self.verify_messages(1 + (0 if enable_plugin else 5))

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_issue_74_reverse(self, enable_plugin):
        self.run_linter(enable_plugin)
        # l.9: ``print(self.username)`` before ``request.cls.username = "dylan"``
        self.verify_messages(1 + (0 if enable_plugin else 5))

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_from_unpack(self, enable_plugin):
        self.run_linter(enable_plugin)
        self.verify_messages(0 if enable_plugin else 1)

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_assign_attr_of_attr(self, enable_plugin):
        self.run_linter(enable_plugin)
        self.verify_messages(0 if enable_plugin else 1)
