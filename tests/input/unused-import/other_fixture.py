import pytest


@pytest.fixture
def other_fixture_not_in_conftest():
    return True
