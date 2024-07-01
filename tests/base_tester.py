from __future__ import annotations

import logging
import os
from abc import ABC
from pathlib import Path
from pprint import pprint

import astroid
import pytest
from pylint.checkers import BaseChecker
from pylint.testutils import MessageTest, UnittestLinter
from pylint.utils import ASTWalker

import pylint_pytest.checkers.fixture

# XXX: allow all file names
pylint_pytest.checkers.fixture.FILE_NAME_PATTERNS = ("*",)


def get_test_root_path() -> Path:
    """Assumes ``base_tester.py`` is at ``<root>/tests``."""
    return Path(__file__).parent


class BasePytestTester(ABC):
    CHECKER_CLASS = BaseChecker
    IMPACTED_CHECKER_CLASSES: list[type[BaseChecker]] = []
    MSG_ID: str
    msgs: list[MessageTest] = []

    # Set by ``test_name_fixture``
    test_name: str = ""

    @pytest.fixture(autouse=True)
    def test_name_fixture(self, request):
        self.test_name = request.node.originalname.replace("test_", "", 1)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "MSG_ID") or not isinstance(cls.MSG_ID, str) or not cls.MSG_ID:
            raise TypeError("Subclasses must define a non-empty MSG_ID of type str")

    enable_plugin = True

    @pytest.fixture(autouse=True)
    def with_no_warnings(self, caplog):  # pylint: disable=no-self-use
        with caplog.at_level(logging.WARNING):
            yield

        records = caplog.get_records("call")
        assert not records, records

    def run_linter(self, enable_plugin):
        self.enable_plugin = enable_plugin

        file_path = os.path.join(
            get_test_root_path(),
            "input",
            self.MSG_ID,
            self.test_name + ".py",
        )

        with open(file_path) as fin:
            content = fin.read()
            module = astroid.parse(content, module_name=self.test_name)
            module.file = fin.name

        self.walk(module)  # run all checkers
        self.msgs = self.linter.release_messages()

    def verify_messages(self, msg_count, msg_id=None):
        msg_id = msg_id or self.MSG_ID

        matched_count = 0
        for message in self.msgs:
            # only care about ID and count, not the content
            if message.msg_id == msg_id:
                matched_count += 1

        pprint(self.msgs)
        assert matched_count == msg_count, f"expecting {msg_count}, actual {matched_count}"

    def setup_method(self):
        self.linter = UnittestLinter()
        self.checker = self.CHECKER_CLASS(self.linter)
        self.impacted_checkers = []

        self.checker.open()

        for checker_class in self.IMPACTED_CHECKER_CLASSES:
            checker = checker_class(self.linter)
            checker.open()
            self.impacted_checkers.append(checker)

    def teardown_method(self):
        self.checker.close()
        for checker in self.impacted_checkers:
            checker.close()

    def walk(self, node):
        """recursive walk on the given node"""
        walker = ASTWalker(self.linter)
        if self.enable_plugin:
            walker.add_checker(self.checker)
        for checker in self.impacted_checkers:
            walker.add_checker(checker)
        walker.walk(node)
