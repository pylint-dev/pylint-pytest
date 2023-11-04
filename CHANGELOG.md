# Changelog

## [Unreleased]

### Added

- Support for Python 3.12 (#24)
- Support for Pylint 3 (#24)

### Removed

- Support for Python 3.6 & 3.7 (#23)

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
