.PHONY: install run debug clean lint lint-strict

install:
	uv sync --all-groups

run:
	uv run python main.py

debug:
	uv run python -m pdb main.py

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache

lint:
	uv run flake8 .
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 .
	uv run mypy . --strict
