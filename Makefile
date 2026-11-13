PYTHON ?= python

.PHONY: help check test test-sim docs lab freeze

help:
	@echo "make check   verify cogcal env, package versions and document hashes"
	@echo "make test    run project tests"
	@echo "make test-sim run SO-101 integration checks (requires requirements-sim.txt and assets)"
	@echo "make docs    list archived documents"
	@echo "make lab     start Jupyter Lab on port 8891"
	@echo "make freeze  write exact package versions to requirements-lock.txt"

check:
	$(PYTHON) scripts/check_env.py

test:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 $(PYTHON) -m pytest

test-sim:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 $(PYTHON) -m pytest tests/test_so101_scene.py tests/test_rollout_script.py

docs:
	@ls -lh docs docs/reference

lab:
	$(PYTHON) -m jupyter lab --no-browser --ip=0.0.0.0 --port=8891

freeze:
	$(PYTHON) -m pip freeze | grep -v "^-e " > requirements-lock.txt
