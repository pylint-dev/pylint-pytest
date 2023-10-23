import pytest


class TestClass:
    @staticmethod
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(request):
        cls = request.cls
        cls.defined_in_setup_class = object()
        cls.defined_in_setup_class.attr_of_attr = None

    def test_foo(self):
        assert self.defined_in_setup_class
