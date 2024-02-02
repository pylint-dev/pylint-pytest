# Changelog

## [Unreleased]

## [2.0.0a0] - 2024-02-02

### Added

* Increased reproducibility of the project, by using `pip-compile` for the development dependencies
  (https://github.com/pylint-dev/pylint-pytest/pull/28, small bugfix in https://github.com/pylint-dev/pylint-pytest/pull/39)
* Introduced @dependabot (part of https://github.com/pylint-dev/pylint-pytest/pull/28)

### Removed

* Support for Python 3.6 & 3.7 (https://github.com/pylint-dev/pylint-pytest/pull/23)

### Improved

* Migrate setup.py to pyproject.toml (https://github.com/pylint-dev/pylint-pytest/pull/8)
* Support for Python 3.12 (https://github.com/pylint-dev/pylint-pytest/issues/3,
  "side effect" of https://github.com/pylint-dev/pylint-pytest/pull/8)
* Improved reliability of the `FixtureChecker` class (https://github.com/pylint-dev/pylint-pytest/pull/29)
* Minor CI + License updates (in 29f0c33, e0e529a, 8f56d1c)

## [1.1.7] - 2023-12-04

This is a small release to support additionally Pylint v3.
It should be noted, however, that for linting, Pylint must be v3 or newer (due to backwards-incompatible changes).

### Fixed

* Support pylint v3 and drop v1 (https://github.com/pylint-dev/pylint-pytest/pull/27)

## [1.1.6] - 2023-11-20

This is a small bugfix release.

This will probably be the last bugfix release in the v1 series.
We MAY support Python 3.12 in the v1 series if support appears to be trivial.

### Fixed

* 🐛 Ignore collection failures in non-tests (https://github.com/pylint-dev/pylint-pytest/pull/15)
* Minor `.github/ISSUE_TEMPLATE/bug_report.md` improvement (https://github.com/pylint-dev/pylint-pytest/commit/22650f9912bcdc6a1bc4b3166f70bba7339aba7c)

## [1.1.5] - 2023-11-13

This is a small bugfix release.

### Fixed

* removes more false positives for unused-argument (https://github.com/pylint-dev/pylint-pytest/pull/21)
* A collection of minor improvements to tests (https://github.com/pylint-dev/pylint-pytest/pull/26)
* Windows Artifacts have incorrect Slugification (https://github.com/pylint-dev/pylint-pytest/pull/25)

## [1.1.4] - 2023-11-06

This is a small bugfix release.

### Fixed

* `anis-campos/fix_is_pytest_fixture` (https://github.com/pylint-dev/pylint-pytest/pull/2)
  Astroid has different semantics when using `import pytest` or `from pytest import ...`,
  which affects the detection of pytest fixtures.

### Improved

* `pre-commit`: (https://github.com/pylint-dev/pylint-pytest/pull/20)
  * Added more checks to the `pre-commit` hook.
    ```yaml
    repos:
      - repo: https://github.com/pre-commit/pre-commit-hooks
        hooks:
        - id: check-yaml
        - id: check-toml
        - id: check-vcs-permalinks
        - id: check-shebang-scripts-are-executable
        - id: name-tests-test
      - repo: https://github.com/jumanjihouse/pre-commit-hook-yamlfmt
          - id: yamlfmt
      - repo: local
        hooks:
          - id: python-no-log-fatal
            name: avoid logger.fatal(
    ```
  * Unified formatting (always expanded arrays; not covered by linters, sadly)

## [1.1.3] - 2023-10-23

This is the first release after maintenance was assumed by https://github.com/stdedos.

The focus of this release was to improve automation:
* Fix the continuous integration,
* Run tests as part of branches and PRs,
* Use `.pre-commit-config.yaml` file to upkeep the code quality, and
* Automate the release process

There should be no functional changes in this release, although there are changes in the source code.

A heartfelt thank you to https://github.com/Pierre-Sassoulas for his invaluable contributions to the continued maintenance of this project!

### Fixed

- The continuous integration was fixed, as a new maintenance team was assembled.

### Added

- Added an extensive `.pre-commit-config.yaml` file to upkeep the code quality.
  It includes, among others, `black`, `mypy` (in non-strict mode yet), `ruff`, and `pylint`.
- Added an automated release process

### Changed

- Redirected all repository URLs to the https://github.com/pylint-dev/pylint-pytest.

## [1.1.2] - 2021-04-19
### Fixed
- Fix #18 plugin crash when test case is marked with a non-pytest.mark decorator

## [1.1.1] - 2021-04-12
### Fixed
- Fix pytest fixture collection error on non-test modules

## [1.1.0] - 2021-04-11
### Added
- W6402 `useless-pytest-mark-decorator`: add warning for [using pytest.mark on fixtures](https://docs.pytest.org/en/stable/reference.html#marks) (thanks to @DKorytkin)
- W6403 `deprecated-positional-argument-for-pytest-fixture`: add warning for [positional arguments to pytest.fixture()](https://docs.pytest.org/en/stable/deprecations.html#pytest-fixture-arguments-are-keyword-only) (thanks to @DKorytkin)
- F6401 `cannot-enumerate-pytest-fixtures`: add fatal error when the plugin cannot enumerate and collect pytest fixtures for analysis (#27)

## [1.0.3] - 2021-03-13
### Fixed
- Fix #13 regression caused by mangling `sys.modules`

## [1.0.2] - 2021-03-10
### Fixed
- Fix pytest **Module already imported so cannot be rewritten** warning when the package being linted was used by pytest/conftest already (#10)
- Fix missing Python version constraint (#11)

## [1.0.1] - 2021-03-03
### Added
- Suppressing FP `unused-import` when fixtures defined elsewhere are imported into `conftest.py` but not directly used (#2)

## [1.0.0] - 2021-03-02
### Added
- Python 3.9 support

### Removed
- Python 2.7 & 3.5 support

### Fixed
- Fix not able to work with `pytest-xdist` plugin when `--dist loadfile` is set in configuration file (#5)

## [0.3.0] - 2020-08-10
### Added
- W6401 `deprecated-pytest-yield-fixture`: add warning for [yield_fixture functions](https://docs.pytest.org/en/latest/yieldfixture.html)

### Fixed
- Fix incorrect path separator for Windows (#1)

## [0.2.0] - 2020-05-25
### Added
- Suppressing FP `no-member` from [using workaround of accessing cls in setup fixture](https://github.com/pytest-dev/pytest/issues/3778#issuecomment-411899446)

### Changed
- Refactor plugin to group patches and augmentations

## [0.1.2] - 2020-05-22
### Fixed
- Fix fixtures defined with `@pytest.yield_fixture` decorator still showing FP
- Fix crashes when using fixture + if + inline import
- Fix crashes when relatively importing fixtures (`from ..conftest import fixture`)

## [0.1.1] - 2020-05-19
### Fixed
- Fix crashes when `*args` or `**kwargs` is used in FuncDef

## [0.1] - 2020-05-18
### Added
- Suppressing FP `unused-import` with tests
- Suppressing FP `unused-argument` with tests
- Suppressing FP `redefined-outer-scope` with tests
- Add CI/CD configuration with Travis CI
