.PHONY: setup data run test lint check screenshots clean

setup:
	python3 -m venv .venv
	.venv/bin/pip install -e '.[dev]'

data:
	.venv/bin/python scripts/generate_dataset.py

run:
	.venv/bin/uvicorn app.main:app --reload

test:
	.venv/bin/pytest

lint:
	.venv/bin/ruff check app scripts tests

check: lint test
	.venv/bin/python -m compileall -q app scripts tests

screenshots:
	PYTHON_BIN=.venv/bin/python scripts/capture_screenshots.sh

clean:
	rm -rf artifacts .pytest_cache .ruff_cache
