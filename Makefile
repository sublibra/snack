.PHONY: help install dev test lint format clean run docker-up docker-down

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	uv venv
	uv pip install -e .

dev: ## Install development dependencies (safe)
	./scripts/install-dev.sh
	
dev-unsafe: ## Setup development environment (unsafe - force local install despite python checks)
	SKIP_PY_CHECK=1 ./scripts/install-dev.sh

test: ## Run tests
	uv run pytest

lint: ## Run linting
	uv run ruff check app tests
	uv run mypy app

format: ## Format code
	uv run ruff format app tests

clean: ## Clean up cache and temporary files
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf dist
	rm -rf *.egg-info

run: ## Run the development server
	./scripts/dev-server.sh

db-init: ## Initialize database
	./scripts/db.sh init

db-migrate: ## Create new migration
	./scripts/db.sh migrate

db-upgrade: ## Apply migrations
	./scripts/db.sh upgrade

docker-up: ## Start with Docker Compose
	docker-compose up -d

docker-down: ## Stop Docker Compose
	docker-compose down

db-up: ## Start only the Postgres DB container (useful for running the backend on host)
	# Start the db service only so the host process can connect to localhost:5432
	docker-compose up -d db

db-down: ## Stop only the Postgres DB container
	docker-compose stop db || true
	docker-compose rm -f db || true

docker-logs: ## View Docker logs
	docker-compose logs -f backend