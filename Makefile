.PHONY: check lint test tasks results reproduce

check: lint test tasks

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest -q

tasks:
	uv run sdlc-eval check-tasks

results:
	uv run sdlc-eval errors
	uv run sdlc-eval results

reproduce:
	@echo "The agent runner is not built yet (next step). Nothing to reproduce." >&2; exit 1
