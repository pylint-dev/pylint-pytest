from setuptools import find_packages, setup

setup(
    packages=find_packages(exclude=["tests*", "sandbox"]),
    tests_require=["pytest", "pytest-cov", "pylint"],
)
