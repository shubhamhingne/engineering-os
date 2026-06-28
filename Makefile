# Engineering OS — common tasks. `make help` to list.
.DEFAULT_GOAL := help
.PHONY: help setup dev example test lint migrate lock up down

API := apps/api

help: ## list targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

setup: ## create the venv and install the API (editable) — first step for contributors
	cd $(API) && python -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"

dev: setup ## run the API locally with reload
	cd $(API) && . .venv/bin/activate && PYTHONPATH=src uvicorn engineering_os.main:app --reload

example: ## run the end-to-end example (in-process, no server/keys)
	cd $(API) && . .venv/bin/activate && PYTHONPATH=src python ../../examples/seed.py

test: ## lint + run the test suite
	cd $(API) && . .venv/bin/activate && ruff check . && pytest -q

lint: ## lint only
	cd $(API) && . .venv/bin/activate && ruff check .

migrate: ## apply database migrations
	cd $(API) && . .venv/bin/activate && alembic upgrade head

lock: ## regenerate the pinned lockfile (run on Python 3.12)
	cd $(API) && . .venv/bin/activate && pip install pip-tools && \
		pip-compile --quiet --output-file=requirements.lock pyproject.toml

up: ## bring the full stack (Postgres + Redis + API) up in containers
	docker compose up --build

down: ## stop the stack
	docker compose down
