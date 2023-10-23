import pytest


@pytest.fixture("function")
def some_fixture():
    return "ok"
