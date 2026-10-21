CONFIG=config.txt
DEBUGGER= -m pdb

VIRTUALENV= PacEnv
PYTHON=$(VIRTUALENV)/bin/python3
PIP=$(VIRTUALENV)/bin/pip

DEPENDENCIES=requirements.txt
MAZEPROGRAM=mazegenerator-2.1.0-py3-none-any.whl

MAIN= -m src

TOCLEAN=.mypy_cache

MYPYFLAGS=--warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

all: run

install: $(VIRTUALENV)
	$(PIP) install -r $(DEPENDENCIES)

run: install
	$(PYTHON) $(MAIN)

debug: $(VIRTUALENV)
	$(PYTHON) $(DEBUGGER) $(MAIN) </dev/tty

$(VIRTUALENV):
	python3 -m venv $(VIRTUALENV)

install-module:
	$(PIP) install ./src/$(MAZEPROGRAM)

clean:
	py3clean .
	rm -rf $(TOCLEAN)

lint:
	flake8
	mypy $(MYPYFLAGS)

lint-strict:
	flake8
	mypy --strict --ignore-missing-imports

SILENT: all install run debug build install clean lint lint-strict