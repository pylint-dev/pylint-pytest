import pytest
import this_is_invalid  # makes pytest fail


@pytest.fixture
def fixture():
    pass


def test_something(fixture):
    pass
