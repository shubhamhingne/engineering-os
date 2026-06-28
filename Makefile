# Engineering OS — common tasks. `make help` to list.
.DEFAULT_GOAL := help
.PHONY: help dev test lint migrate up down

API := apps/api

help: ## list targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

dev: ## zero-to-running: create the venv, install, and serve the API with reload
	cd $(API) && python -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]" && \
		uvicorn engineering_os.main:app --reload

test: ## lint + run the test suite
	cd $(API) && . .venv/bin/activate && ruff check . && pytest -q

migrate: ## apply database migrations
	cd $(API) && . .venv/bin/activate && alembic upgrade head

up: ## bring the full stack (Postgres + Redis + API) up in containers
	docker compose up --build

down: ## stop the stack
	docker compose down
