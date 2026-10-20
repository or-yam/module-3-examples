.PHONY: setup dev lint test

# Use this project's environment even if another virtualenv is active.
UV := env -u VIRTUAL_ENV uv

setup:
	$(UV) sync
	@test -f .env || cp .env.example .env

dev:
	$(UV) run langgraph dev

lint:
	$(UV) run ruff check lessons/ tests/

test:
	$(UV) run python -m unittest discover -s tests -v
