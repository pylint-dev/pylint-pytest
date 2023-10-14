import pytest


class TestClass:
    @staticmethod
    @pytest.yield_fixture(scope="class", autouse=True)
    def setup_class(request):
        cls = request.cls
        cls.defined_in_setup_class = 123

    def test_foo(self):
        assert self.defined_in_setup_class
