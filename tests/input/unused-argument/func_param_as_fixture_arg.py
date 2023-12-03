"""
This module illustrates a situation in which unused-argument should be
suppressed, but is not.
"""

import pytest


@pytest.fixture
def myfix(arg):
    """A fixture that requests a function param"""
    print("arg is ", arg)
    return True


@pytest.mark.parametrize("arg", [1, 2, 3])
def test_myfix(myfix, arg):
    """A test function that uses the param through a fixture"""
    assert myfix


@pytest.mark.parametrize("narg", [4, 5, 6])
def test_nyfix(narg):  # unused-argument
    """A test function that does not use its param"""
    assert True


@pytest.mark.parametrize("arg", [1, 2, 3])
def test_narg_is_used_nowhere(myfix, narg):
    """
    A test function that does not use its param (``narg``):
    Not itself, nor through a fixture (``myfix``).
    """
    assert myfix
