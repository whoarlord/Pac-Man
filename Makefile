CONFIG=config.json
DEBUGGER= -m pdb

VIRTUALENV= PacEnv
PYTHON=$(VIRTUALENV)/bin/python3
PIP=$(VIRTUALENV)/bin/pip

FLAKE8=$(VIRTUALENV)/bin/flake8
MYPY=$(VIRTUALENV)/bin/mypy

DEPENDENCIES=requirements.txt
MAZEPROGRAM=mazegenerator-2.1.0-py3-none-any.whl

MAIN= pac-man.py

TOCLEAN=.mypy_cache

MYPYFLAGS=--warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

.PHONY: all install install-module run debug clean lint lint-strict

.SILENT: all install install-module run debug clean lint lint-strict

all: run

install: $(VIRTUALENV)
	$(PIP) install -r $(DEPENDENCIES)
	$(PIP) install ./src/$(MAZEPROGRAM)

install-module: $(VIRTUALENV)
	$(PIP) install --force-reinstall ./src/$(MAZEPROGRAM)

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) $(DEBUGGER) $(MAIN) $(CONFIG) </dev/tty

$(VIRTUALENV):
	python3 -m venv $(VIRTUALENV)

clean:
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
	rm -rf $(TOCLEAN)

lint:
	$(FLAKE8) .
	$(MYPY) . $(MYPYFLAGS)

lint-strict:
	$(FLAKE8) .
	$(MYPY) . --strict --ignore-missing-imports
