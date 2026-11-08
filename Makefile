.PHONY: check lint test tasks image results reproduce

check: lint test tasks

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest -q

tasks:
	uv run sdlc-eval check-tasks

image:
	docker build -t sdlc-eval-kit:0.1 docker/

results:
	uv run sdlc-eval errors
	uv run sdlc-eval results

reproduce:
	@echo "Needs the API model and its cost accounting (step 0.7). Local model only for now:" >&2
	@echo "  make image && uv run --extra runner sdlc-eval run --model ollama_chat/qwen3-coder:30b" >&2; exit 1
