import pytest


@pytest.fixture(scope="function")
def some_fixture():
    return "ok"
