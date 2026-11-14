import re
from collections.abc import Sequence

import astroid
import pytest

from pylint_pytest.checkers.fixture import FixtureChecker

from .base_tester import BasePytestTester


class TestCannotEnumerateFixtures(BasePytestTester):
    CHECKER_CLASS = FixtureChecker
    MSG_ID = "cannot-enumerate-pytest-fixtures"

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_no_such_package(self, enable_plugin):
        self.run_linter(enable_plugin)
        self.verify_messages(1 if enable_plugin else 0)

        if enable_plugin:
            msg = self.msgs[0]

            assert isinstance(msg.args, Sequence)
            assert len(msg.args) == 3

            # Asserts/Fixes duplicate filenames in output:
            # https://github.com/reverbc/pylint-pytest/pull/22/files#r698204470
            filename_arg = msg.args[0]
            assert len(re.findall(r"\.py", filename_arg)) == 1

            # Asserts that path is relative (usually to the root of the repository).
            assert filename_arg[0] != "/"

            # Assert `stdout` is non-empty.
            assert msg.args[1]
            # Assert `stderr` is empty (pytest runs stably, even if the fixture collection fails).
            assert not msg.args[2]

    @pytest.mark.parametrize("enable_plugin", [True, False])
    def test_import_corrupted_module(self, enable_plugin):
        self.run_linter(enable_plugin)
        self.verify_messages(1 if enable_plugin else 0)

        if enable_plugin:
            msg = self.msgs[0]

            assert isinstance(msg.args, Sequence)
            assert len(msg.args) == 3

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

    def test_pytest_raises(self, tmp_path):
        """pytest raises instead of returning an exit code: report it, don't crash.

        pytest < 9 raises here, pytest >= 9 returns an exit code. The file is also
        outside the current directory, which must not crash either.

        https://github.com/pylint-dev/pylint-pytest/issues/126
        https://github.com/pylint-dev/pylint-pytest/issues/130
        """
        conftest = tmp_path / "conftest.py"
        conftest.write_text('pytest_plugins = ["no_such_banana_plugin"]\n')
        # Not named ``conftest``: astroid would cache it under that name, and resolve
        # the ``from conftest import ...`` of the tests that follow to it.
        module = astroid.parse(conftest.read_text(), module_name="banana_conftest")
        module.file = str(conftest)

        self.walk(module)
        self.msgs = self.linter.release_messages()

        self.verify_messages(1)
        msg = self.msgs[0]
        assert isinstance(msg.args, Sequence)
        # The error pytest raised or printed goes in the `stderr` part of the message.
        assert "no_such_banana_plugin" in msg.args[2]
