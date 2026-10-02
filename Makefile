# Use python executables inside venv
export PATH := .venv/bin:$(PATH)
export PYTHONPATH= `pwd`

# creates the venv
.venv/bin/python3.11:
	python3.11 -m venv .venv

# makes sures the venv contains a given version of pip and pip-tools
.venv: .venv/bin/python3.11
	pip install --quiet --upgrade 'pip==26.2.1' 'pip-tools==7.6.1'

# generates a lock file with pinned version of all dependencies to be used by the CI and local devs
requirements/dev.txt: .venv requirements/dev.in
	pip-compile \
		--quiet --generate-hashes --max-rounds=20 --strip-extras \
		--no-emit-index-url --no-emit-trusted-host \
		--resolver=backtracking \
		--output-file requirements/dev.txt \
		 pyproject.toml \
		 requirements/dev.in

# upgrades the dependencies to their latest/matching version
.PHONY: upgrade
upgrade: .venv
	pip-compile \
		--quiet --generate-hashes --max-rounds=20 --strip-extras \
		--no-emit-index-url --no-emit-trusted-host \
		--upgrade \
		--resolver=backtracking \
		--output-file requirements/dev.txt \
		pyproject.toml \
		requirements/dev.in

# creates the venv if not present then install the dependencies, the package and pre-commit
.PHONY: install
install: .venv requirements/dev.txt
	pip-sync requirements/dev.txt
	# install pylint_pytest (deps are already handled by the line before)
	pip install --no-deps -e .
	# install pre-commit hooks
	pre-commit install
