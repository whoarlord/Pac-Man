CONFIG=config.json
DEBUGGER=-m pdb

PACKAGE_DIR=dist/pac-man

RUN=uv run
PYTHON=$(RUN) python

MAZEPROGRAM=mazegenerator-2.1.0-py3-none-any.whl

MAIN=pac-man.py

TOCLEAN=.mypy_cache

MYPYFLAGS=--warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

.DEFAULT_GOAL := all

.PHONY: all install install-module run debug clean lint lint-strict package

.SILENT: all install install-module run debug clean lint lint-strict package

all: run

package: install
	uv run --with pyinstaller pyinstaller --noconfirm --clean --name pac-man \
		--add-data "src/img:src/img" pac-man.py
	cp config.json $(PACKAGE_DIR)/
	cp packaging/launch.sh packaging/README.txt $(PACKAGE_DIR)/
	cd dist && zip -r pac-man-linux.zip pac-man

install:
	uv sync

install-module:
	uv add --reinstall-package mazegenerator ./src/$(MAZEPROGRAM)

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) $(DEBUGGER) $(MAIN) $(CONFIG) </dev/tty

clean:
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
	rm -rf $(TOCLEAN)

lint:
	$(RUN) flake8 .
	$(RUN) mypy . $(MYPYFLAGS)

lint-strict:
	$(RUN) flake8 .
	$(RUN) mypy . --strict --ignore-missing-imports