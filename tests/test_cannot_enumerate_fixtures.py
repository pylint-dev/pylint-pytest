import re

import astroid
import pytest
from base_tester import BasePytestTester, get_test_root_path

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

            # `import_corrupted_module.py` is the only file pytest was asked to collect,
            # so it's the only one reported (even though it imports `no_such_package.py`).
            filename_arg = msg.args[0]
            assert len(re.findall(r"\.py", filename_arg)) == 1

            # Asserts that paths are relative (usually to the root of the repository).
            assert not [x for x in filename_arg.split(" ") if x[0] == "/"]

            # Assert `stdout` is non-empty.
            assert msg.args[1]
            # Assert `stderr` is empty (pytest runs stably, even though fixture collection fails).
            assert not msg.args[2]

    def test_collection_error_does_not_leak_into_next_module(self, tmp_path):
        """Regression test for https://github.com/pylint-dev/pylint-pytest/issues/68

        ``FixtureCollector.errors`` used to be a mutable class attribute shared by every
        instance, so a collection failure in one module kept getting reported against
        every unrelated module linted afterward in the same process.
        """
        broken_file = get_test_root_path() / "input" / self.MSG_ID / "no_such_package.py"
        with open(broken_file) as fin:
            broken_module = astroid.parse(fin.read(), module_name="no_such_package")
            broken_module.file = fin.name

        self.enable_plugin = True
        self.walk(broken_module)
        self.msgs = self.linter.release_messages()
        self.verify_messages(1)

        clean_file = tmp_path / "clean.py"
        clean_file.write_text("def test_ok():\n    pass\n")
        clean_module = astroid.parse(clean_file.read_text(), module_name="clean")
        clean_module.file = str(clean_file)

        self.walk(clean_module)
        self.msgs = self.linter.release_messages()
        self.verify_messages(0)
