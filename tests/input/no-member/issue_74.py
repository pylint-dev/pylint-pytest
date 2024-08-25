"""Example https://github.com/pylint-dev/pylint-pytest/issues/74#issuecomment-2219850110"""

import pytest


class TestExample:
    @pytest.fixture(scope="class")
    def setup_teardown_username(self, request: pytest.FixtureRequest):
        print(self.username)
        request.cls.username = "dylan"
        yield True
        print(self.username)
        del request.cls.username
        print(self.username)

    @pytest.fixture(scope="function")
    def setup_teardown_password(self, request: pytest.FixtureRequest, setup_teardown_username):
        assert self.username
        request.cls.password = "*****"
        yield setup_teardown_username, True
        del request.cls.password

    def test_username_and_password(self, setup_teardown_password):
        assert self.username == "dylan"
        assert self.password == "*****"
