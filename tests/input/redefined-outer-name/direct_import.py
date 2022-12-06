from pytest import fixture


@fixture
def simple_decorator():
    """the fixture using the decorator without executing it"""


def test_simple_fixture(simple_decorator):
    assert True


@fixture()
def un_configured_decorated():
    """the decorated is called without argument, like scope"""


def test_un_configured_decorated(un_configured_decorated):
    assert True


@fixture(scope="function")
def configured_decorated():
    """the decorated is called with argument, like scope"""


def test_un_configured_decorated(configured_decorated):
    assert True
