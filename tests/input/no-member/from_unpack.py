import pytest


def meh():
    return True, False


class TestClass:
    @staticmethod
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(request):
        cls = request.cls
        cls.defined_in_setup_class, _ = meh()

    def test_foo(self):
        assert self.defined_in_setup_class
