import inspect

import astroid


def _is_pytest_mark_usefixtures(decorator):
    # expecting @pytest.mark.usefixture(...)
    try:
        if (
            isinstance(decorator, astroid.Call)
            and decorator.func.attrname == "usefixtures"
            and decorator.func.expr.attrname == "mark"
            and decorator.func.expr.expr.name == "pytest"
        ):
            return True
    except AttributeError:
        pass
    return False


def _is_pytest_mark(decorator):
    try:
        deco = decorator  # as attribute `@pytest.mark.trylast`
        if isinstance(decorator, astroid.Call):
            deco = decorator.func  # as function `@pytest.mark.skipif(...)`
        if deco.expr.attrname == "mark" and deco.expr.expr.name == "pytest":
            return True
    except AttributeError:
        pass
    return False


def _is_pytest_fixture(decorator, fixture=True, yield_fixture=True):
    to_check = set()

    if fixture:
        to_check.add("fixture")

    if yield_fixture:
        to_check.add("yield_fixture")

    def _check_attribute(attr):
        """
        handle astroid.Attribute, i.e., when the fixture function is
        used by importing the pytest module
        """
        return attr.attrname in to_check and attr.expr.name == "pytest"

    def _check_name(name_):
        """
        handle astroid.Name, i.e., when the fixture function is
        directly imported
        """
        function_name = name_.name
        module = decorator.root().globals.get(function_name, [None])[0]
        module_name = module.modname if module else None
        return function_name in to_check and module_name == "pytest"

    try:
        if isinstance(decorator, astroid.Name):
            # expecting @fixture
            return _check_name(decorator)
        if isinstance(decorator, astroid.Attribute):
            # expecting @pytest.fixture
            return _check_attribute(decorator)
        if isinstance(decorator, astroid.Call):
            func = decorator.func
            if isinstance(func, astroid.Name):
                # expecting @fixture(scope=...)
                return _check_name(func)
            # expecting @pytest.fixture(scope=...)
            return _check_attribute(func)

    except AttributeError:
        pass

    return False


def _is_class_autouse_fixture(function):
    try:
        for decorator in function.decorators.nodes:
            if isinstance(decorator, astroid.Call):
                func = decorator.func

                if (
                    func
                    and func.attrname in ("fixture", "yield_fixture")
                    and func.expr.name == "pytest"
                ):
                    is_class = is_autouse = False

                    for kwarg in decorator.keywords or []:
                        if kwarg.arg == "scope" and kwarg.value.value == "class":
                            is_class = True
                        if kwarg.arg == "autouse" and kwarg.value.value is True:
                            is_autouse = True

                    if is_class and is_autouse:
                        return True
    except AttributeError:
        pass

    return False


def _can_use_fixture(function):
    if isinstance(function, astroid.FunctionDef):
        # test_*, *_test
        if function.name.startswith("test_") or function.name.endswith("_test"):
            return True

        if function.decorators:
            for decorator in function.decorators.nodes:
                # usefixture
                if _is_pytest_mark_usefixtures(decorator):
                    return True

                # fixture
                if _is_pytest_fixture(decorator):
                    return True

    return False


def _is_same_module(fixtures, import_node, fixture_name):
    """Comparing pytest fixture node with astroid.ImportFrom"""
    try:
        for fixture in fixtures[fixture_name]:
            for import_from in import_node.root().globals[fixture_name]:
                module = inspect.getmodule(fixture.func)
                parent_import = import_from.parent.import_module(
                    import_from.modname, False, import_from.level
                )
                if module is not None and module.__file__ == parent_import.file:
                    return True
    except Exception:  # pylint: disable=broad-except
        pass
    return False
