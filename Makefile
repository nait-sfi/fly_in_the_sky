install: uv sync

run: uv run main.py

debug: uv run -m pdb main.py 

clean: rm -rf  __pycache__ .my .mypy_cache

lint: flake8 . && mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict: flake8 . & mypy . --strict
