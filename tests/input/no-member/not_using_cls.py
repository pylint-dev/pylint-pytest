import pytest


class TestClass:
    @staticmethod
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(request):
        clls = request.cls
        clls.defined_in_setup_class = 123

    def test_foo(self):
        assert self.defined_in_setup_class
