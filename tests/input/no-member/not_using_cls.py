import pytest


class TestClass:
    @staticmethod
    @pytest.fixture(scope="class", autouse=True)
    def setup_class_orig(request):
        clls = request.cls
        clls.defined_in_setup_class = 123

    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self, request: pytest.FixtureRequest):
        #     vvvvvvvvvv Cannot access ``self.klass`` before it is defined!
        print(self.klass)
        request.cls.klass = "class"
        print(self.klass)

    @pytest.fixture(scope="function", autouse=True)
    def setup_function(self, request: pytest.FixtureRequest):
        request.cls.function = "function"
        print(self.function)

    def test_foo(self):
        assert self.defined_in_setup_class
        assert self.temp1
        assert self.klass == "class"
        assert self.function == "function"

    # Ordering MATTERS! astroid traverses the file from top to bottom.
    # We should be able to cover that case as well, as nothing enforces a specific order.
    @pytest.fixture(autouse=True)
    def setup_teardown_environment(self, request: pytest.FixtureRequest):
        print(request.cls.temp1)  # ToDo: Cannot access ``request.cls.temp1`` before it is defined!
        request.cls.temp1 = 54321
        print(self.temp1)
