"""
The tests in this file shall detect any error related to actual execution of pylint, while the
other test are more unit tests that focuses on the checkers behaviour.

Notes:
    Tests here are voluntarily minimalistic, the goal is not to test pylint, it is only checking
    that pylint_pytest integrates just fine
"""
import subprocess


def test_simple_process():
    result = subprocess.run(
        ["pylint", "--load-plugins", "pylint_pytest", "tests"],
        capture_output=True,
        check=False,
    )
    # then no error
    assert not result.stderr


def test_multi_process():
    result = subprocess.run(
        ["pylint", "--load-plugins", "pylint_pytest", "-j", "2", "tests"],
        capture_output=True,
        check=False,
    )
    # then no error
    assert not result.stderr
