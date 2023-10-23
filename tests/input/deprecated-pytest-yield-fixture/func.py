import pytest


@pytest.yield_fixture()
def yield_fixture():
    yield


@pytest.yield_fixture(scope="session")
def yield_fixture_session():
    yield
