.PHONY: fmt lint type test verify

fmt:
	python -m ruff format .

lint:
	python -m ruff check .

type:
	python -m mypy codebots

test:
	python -m pytest -q

verify: fmt lint type test
