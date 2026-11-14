import os

import pytest

from pylint_pytest.utils import PytestNaming


@pytest.mark.parametrize(
    ("pattern", "path", "expected"),
    [
        ("test_*.py", "fruits/test_apple.py", True),
        ("test_*.py", "fruits/apple.py", False),
        ("fruits/*.py", "basket/fruits/apple.py", True),
        ("fruits/*.py", "basket/vegetables/carrot.py", False),
        (f"{os.sep}basket{os.sep}*.py", f"{os.sep}basket{os.sep}apple.py", True),
    ],
)
def test_is_test_file(pattern, path, expected):
    assert PytestNaming(files=(pattern,)).is_test_file(path) is expected


@pytest.mark.parametrize(
    ("option", "name", "expected"),
    [
        ("Check", "CheckBanana", True),
        ("Check", "Banana", False),
        ("*Suite", "BananaSuite", True),
        ("*Suite", "BananaSuites", False),
    ],
)
def test_is_test_class(option, name, expected):
    assert PytestNaming(classes=(option,)).is_test_class(name) is expected
