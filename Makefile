# Use python executables inside venv
export PATH := .venv/bin:$(PATH)
export PYTHONPATH=.

# creates the venv
.venv/bin/python3.11:
	python3.11 -m venv .venv

# makes sures the venv contains a given version of pip and pip-tools
.venv: .venv/bin/python3.11
	pip install --quiet --upgrade 'pip==23.3.1' 'pip-tools==7.3'

# generates a lock file with pinned version of all dependencies to be used by the CI and local devs
requirements/dev.txt: .venv requirements/dev.in pyproject.toml
	pip-compile \
		--quiet --generate-hashes --max-rounds=20 --strip-extras \
		--resolver=backtracking \
		--output-file requirements/dev.txt \
		 requirements/dev.in pyproject.toml

# upgrades the dependencies to their latest/matching version
upgrade: .venv
	pip-compile \
		--quiet --generate-hashes --max-rounds=20 --strip-extras \
		--upgrade \
		--resolver=backtracking \
		--output-file requirements/dev.txt \
		requirements/dev.in pyproject.toml


# creates the venv if not present then install the dependencies, the package and pre-commit
.PHONY: install
install: .venv
	pip-sync requirements/dev.txt
	# install pylint_pytest (deps are already handled by the line before)
	pip install --no-deps -e .
	# install pre-commit hooks
	pre-commit install
