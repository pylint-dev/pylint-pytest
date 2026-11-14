"""A helper module (loaded with ``pytest_plugins``) that only holds fixtures."""

import pytest


@pytest.fixture
def apple():
    return "apple"


@pytest.fixture
def fruit_basket(apple):
    return [apple]
