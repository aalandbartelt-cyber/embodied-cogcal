PYTHON ?= python

.PHONY: help check test docs lab freeze

help:
	@echo "make check   verify cogcal env, package versions and document hashes"
	@echo "make test    run project tests"
	@echo "make docs    list archived documents"
	@echo "make lab     start Jupyter Lab on port 8891"
	@echo "make freeze  write exact package versions to requirements-lock.txt"

check:
	$(PYTHON) scripts/check_env.py

test:
	$(PYTHON) -m pytest

docs:
	@ls -lh docs docs/reference

lab:
	$(PYTHON) -m jupyter lab --no-browser --ip=0.0.0.0 --port=8891

freeze:
	$(PYTHON) -m pip freeze | grep -v "^-e " > requirements-lock.txt
