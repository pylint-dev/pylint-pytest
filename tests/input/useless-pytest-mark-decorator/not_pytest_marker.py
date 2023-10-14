import functools
from types import SimpleNamespace


def noop(func):
    @functools.wraps(func)
    def wrapper_noop(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper_noop


PYTEST = SimpleNamespace(MARK=SimpleNamespace(noop=noop))


@noop
def test_non_pytest_marker():
    pass


@PYTEST.MARK.noop
def test_non_pytest_marker_attr():
    pass
