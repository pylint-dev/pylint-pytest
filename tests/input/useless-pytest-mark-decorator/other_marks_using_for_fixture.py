import os

import pytest


@pytest.mark.trylast
@pytest.fixture
def fixture():
    return "Not ok"


@pytest.mark.parametrize("id", range(2))
@pytest.fixture
def fixture_with_params(id):
    return f"{id} not OK"


@pytest.mark.custom_mark
@pytest.fixture
def fixture_with_custom_mark():
    return "NOT OK"


@pytest.mark.skipif(os.getenv("xXx"))
@pytest.fixture
def fixture_with_conditional_mark():
    return "NOK"
