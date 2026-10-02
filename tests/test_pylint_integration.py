"""
The tests in this file shall detect any error related to actual execution of pylint, while the
other test are more unit tests that focuses on the checkers behaviour.

Notes:
    Tests here are voluntarily minimalistic, the goal is not to test pylint, it is only checking
    that pylint_pytest integrates just fine
"""

import re
import subprocess

from pylint_pytest.utils import PYLINT_VERSION_MAJOR

# astroid 2.x (pylint 2.x) sometimes prints this when a generator is garbage collected.
# It is harmless, unrelated to pylint_pytest, and will not be fixed upstream anymore.
ASTROID_2_GENERATOR_NOISE = re.compile(
    rb"Exception ignored in: <generator object \w+ at 0x[0-9a-fA-F]+>\r?\n"
    rb"Traceback \(most recent call last\):\r?\n"
    rb"(?:  .*\r?\n)*"
    rb"ValueError: generator already executing\r?\n"
)


def _errors(stderr: bytes) -> bytes:
    if PYLINT_VERSION_MAJOR == 2:
        return ASTROID_2_GENERATOR_NOISE.sub(b"", stderr)
    return stderr


def test_simple_process():
    result = subprocess.run(
        ["pylint", "--load-plugins", "pylint_pytest", "tests"],
        capture_output=True,
        check=False,
    )
    # then no error
    assert not _errors(result.stderr)


def test_multi_process():
    result = subprocess.run(
        ["pylint", "--load-plugins", "pylint_pytest", "-j", "2", "tests"],
        capture_output=True,
        check=False,
    )
    # then no error
    assert not _errors(result.stderr)
