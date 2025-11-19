# system python interpreter. used only to create virtual environment
PY = python3
VENV = .venv
BIN=$(VENV)/bin

# make it work on windows too
ifeq ($(OS), Windows_NT)
	BIN=$(VENV)/Scripts
	PY=python
endif


all: lint test

venv: $(VENV)

$(VENV): pyproject.toml
	$(PY) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -e .[dev]
	touch $(VENV)
	echo "Remember to source $(VENV)/bin/activate"

.PHONY: test
test: $(VENV)
	$(PY) -m unittest

.PHONY: lint
lint: $(VENV)
	$(BIN)/black -l 79 src
	$(BIN)/flake8 --per-file-ignores="__init__.py:F401" src
	$(BIN)/pylint --py-version 3.5 src

.PHONY: build
build: $(VENV)
	$(BIN)/flit build

.PHONY: clean
clean:
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete
	rm -rf dist

.PHONY: completelyclean
completelyclean: clean
	rm -rf $(VENV)

