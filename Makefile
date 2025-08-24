SHELL := /bin/bash
VENV ?= venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: help venv install run uvicorn test coverage lint format clean
.DEFAULT_GOAL := help

help:
	@echo "Common tasks:"
	@echo "  make install   - Create venv and install deps"
	@echo "  make run       - Run API via python main.py"
	@echo "  make uvicorn   - Run API via uvicorn (reload)"
	@echo "  make test      - Run tests with pytest"
	@echo "  make coverage  - Run tests with coverage"
	@echo "  make lint      - Lint with flake8"
	@echo "  make format    - Format with black"
	@echo "  make clean     - Remove venv and caches"

venv:
	@test -d $(VENV) || python -m venv $(VENV)
	@echo "Virtual env ready at $(VENV)"

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run: venv
	$(PY) main.py

uvicorn: venv
	$(VENV)/bin/uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

test: venv
	$(VENV)/bin/pytest tests/ -v

coverage: venv
	$(VENV)/bin/pytest tests/ --cov=src --cov-report=term-missing

lint: venv
	$(VENV)/bin/flake8

format: venv
	$(VENV)/bin/black .

clean:
	rm -rf $(VENV) .pytest_cache .mypy_cache **/__pycache__
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +

