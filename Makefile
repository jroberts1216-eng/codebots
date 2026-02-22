PY=python

.PHONY: install test lint format typecheck verify

install:
	pip install -e ".[dev]"

test:
	pytest -q

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy src

verify:
	$(PY) -m compileall -q .
	ruff check .
	ruff format --check .
	pytest -q
