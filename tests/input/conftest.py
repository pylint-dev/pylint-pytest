import pytest


@pytest.fixture
def conftest_fixture_attr():
    return True


@pytest.fixture(scope="function")
def conftest_fixture_func():
    return True
