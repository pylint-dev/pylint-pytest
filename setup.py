#!/usr/bin/env python

from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md")) as fin:
    long_description = fin.read()


setup(
    name="pylint-pytest",
    version="1.1.3",
    author="Stavros Ntentos",
    author_email="133706+stdedos@users.noreply.github.com",
    license="MIT",
    url="https://github.com/pylint-dev/pylint-pytest",
    project_urls={
        "Changelog": "https://github.com/pylint-dev/pylint-pytest/blob/master/CHANGELOG.md",
        "Documentation": "https://github.com/pylint-dev/pylint-pytest#readme",
        "Say Thanks!": "https://saythanks.io/to/stdedos",
        "Source": "https://github.com/pylint-dev/pylint-pytest",
        "Tracker": "https://github.com/pylint-dev/pylint-pytest/issues",
    },
    description="A Pylint plugin to suppress pytest-related false positives.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests*", "sandbox"]),
    install_requires=[
        "pylint<4",
        "pytest>=4.6",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    tests_require=["pytest", "pytest-cov", "pylint"],
    keywords=["pylint", "pytest", "plugin"],
)
