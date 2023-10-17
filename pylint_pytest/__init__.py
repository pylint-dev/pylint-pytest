import glob
import importlib
import inspect
import os

from .checkers import BasePytestChecker


def register(linter):
    """auto discover pylint checker classes"""
    dirname = os.path.dirname(__file__)
    for module in glob.glob(os.path.join(dirname, "checkers", "*.py")):
        # trim file extension
        module = os.path.splitext(module)[0]

        # use relative path only
        module = module.replace(dirname, "", 1)

        # translate file path into module import path
        module = module.replace(os.sep, ".")

        checker = importlib.import_module(module, package=os.path.basename(dirname))
        for attr_name in dir(checker):
            attr_val = getattr(checker, attr_name)
            if (
                attr_val != BasePytestChecker
                and inspect.isclass(attr_val)
                and issubclass(attr_val, BasePytestChecker)
            ):
                linter.register_checker(attr_val(linter))
