import re

import pytest
from base_tester import BasePytestTester

from pylint_pytest.checkers.fixture import FixtureChecker


class TestCannotEnumerateFixtures(BasePytestTester):
    CHECKER_CLASS = FixtureChecker
    MSG_ID = "cannot-enumerate-pytest-fixtures"

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_no_such_package(self, enable_plugin):
        self.run_linter(enable_plugin)
        self.verify_messages(1 if enable_plugin else 0)

        if enable_plugin:
            msg = self.msgs[0]

            # Asserts/Fixes duplicate filenames in output:
            # https://github.com/reverbc/pylint-pytest/pull/22/files#r698204470
            filename_arg = msg.args[0]
            assert len(re.findall(r"\.py", filename_arg)) == 1

            # Asserts that path is relative (usually to the root of the repository).
            assert filename_arg[0] != "/"

            # Assert `stdout` is non-empty.
            assert msg.args[1]
            # Assert `stderr` is empty (pytest runs stably, even though fixture collection fails).
            assert not msg.args[2]

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_import_corrupted_module(self, enable_plugin):
        self.run_linter(enable_plugin)
        self.verify_messages(1 if enable_plugin else 0)

        if enable_plugin:
            msg = self.msgs[0]

            # ... somehow, since `import_corrupted_module.py` imports `no_such_package.py`
            # both of their names are returned in the message.
            filename_arg = msg.args[0]
            assert len(re.findall(r"\.py", filename_arg)) == 2

            # Asserts that paths are relative (usually to the root of the repository).
            assert not [x for x in filename_arg.split(" ") if x[0] == "/"]

            # Assert `stdout` is non-empty.
            assert msg.args[1]
            # Assert `stderr` is empty (pytest runs stably, even though fixture collection fails).
            assert not msg.args[2]
