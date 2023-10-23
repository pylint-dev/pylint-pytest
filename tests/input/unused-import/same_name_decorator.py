import pytest

# an actual unused import, just happened to have the same name as fixture
from _same_name_module import conftest_fixture_attr


@pytest.mark.usefixtures("conftest_fixture_attr")
def test_conftest_fixture_attr():
    assert True
