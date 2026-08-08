.PHONY: install test lint format type-check build publish clean dev

install:
	poetry install

test:
	poetry run pytest tests/ -v --cov=src/autoheal

lint:
	poetry run ruff check src/ tests/
	poetry run ruff format --check src/ tests/

format:
	poetry run ruff format src/ tests/

type-check:
	poetry run mypy src/autoheal/

build:
	poetry build

publish:
	poetry publish

clean:
	rm -rf dist/ build/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

dev:
	poetry run autoheal --help
