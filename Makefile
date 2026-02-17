PYTHON ?= /opt/homebrew/bin/python3.11
VENV_DIR ?= .venv
VENV_PYTHON := $(VENV_DIR)/bin/python

.PHONY: venv install init check check-update test clean

venv:
	$(PYTHON) -m venv $(VENV_DIR)

install: venv
	$(VENV_PYTHON) -m pip install -r requirements.txt

init:
	$(VENV_PYTHON) main.py init

check:
	$(VENV_PYTHON) main.py check

check-update:
	$(VENV_PYTHON) main.py check --update-baseline

test:
	$(VENV_PYTHON) -m pytest -q

clean:
	rm -rf $(VENV_DIR) .pytest_cache
