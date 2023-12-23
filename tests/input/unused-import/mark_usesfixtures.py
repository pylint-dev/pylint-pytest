import pytest

from other_fixture import other_fixture_not_in_conftest


@pytest.mark.usefixtures("other_fixture_not_in_conftest")
def uses_imported_fixture_with_decorator():
    assert True
