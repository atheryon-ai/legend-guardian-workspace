.PHONY: help dev test lint format typecheck docker-build docker-up docker-down harness openapi clean install

# Variables
PYTHON := python3
PIP := pip3
DOCKER_COMPOSE := docker compose
REGISTRY := legend-guardian
TAG := latest
PORT := 8000

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	$(PIP) install -r requirements.txt
	pre-commit install

dev: ## Run development server with hot reload
	uvicorn src.api.main:app --host 0.0.0.0 --port $(PORT) --reload

test: ## Run test suite
	pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

test-unit: ## Run unit tests only
	pytest tests/ -v -m "not integration" --cov=src

test-integration: ## Run integration tests
	pytest tests/ -v -m integration

lint: ## Run linting checks
	ruff check src/ tests/
	black --check src/ tests/
	isort --check-only src/ tests/
	bandit -r src/
	yamllint deploy/

format: ## Format code
	black src/ tests/
	isort src/ tests/
	ruff check --fix src/ tests/

typecheck: ## Run type checking
	mypy src/ --ignore-missing-imports

docker-build: ## Build Docker image
	docker build -t $(REGISTRY)/legend-guardian:$(TAG) .

docker-up: ## Start services with Docker Compose
	$(DOCKER_COMPOSE) --profile full up -d

docker-down: ## Stop Docker Compose services
	$(DOCKER_COMPOSE) --profile full down

docker-logs: ## View Docker logs
	$(DOCKER_COMPOSE) logs -f agent

harness: ## Run all test harness scripts
	@echo "Running test harness..."
	@mkdir -p artifacts/harness/outputs
	@for script in artifacts/harness/usecase*.sh; do \
		echo "Running $$script..."; \
		bash $$script > artifacts/harness/outputs/$$(basename $$script .sh).log 2>&1; \
		if [ $$? -eq 0 ]; then \
			echo "✓ $$script passed"; \
		else \
			echo "✗ $$script failed"; \
		fi; \
	done
	@echo "Results saved to artifacts/harness/outputs/"

harness-1: ## Run use case 1 test
	bash artifacts/harness/usecase1_ingest_publish.sh

harness-2: ## Run use case 2 test
	bash artifacts/harness/usecase2_safe_rollout.sh

harness-3: ## Run use case 3 test
	bash artifacts/harness/usecase3_model_reuse.sh

harness-4: ## Run use case 4 test
	bash artifacts/harness/usecase4_reverse_etl.sh

harness-5: ## Run use case 5 test
	bash artifacts/harness/usecase5_governance_lineage.sh

harness-6: ## Run use case 6 test
	bash artifacts/harness/usecase6_contract_first.sh

harness-7: ## Run use case 7 test
	bash artifacts/harness/usecase7_bulk_backfill.sh

harness-8: ## Run use case 8 test
	bash artifacts/harness/usecase8_incident_rollback.sh

openapi: ## Generate OpenAPI specification
	@echo "Generating OpenAPI spec..."
	@$(PYTHON) -c "import json; from src.api.main import app; print(json.dumps(app.openapi(), indent=2))" > openapi.json
	@echo "OpenAPI spec saved to openapi.json"

smoke: ## Run smoke tests
	bash scripts/smoke.sh

seed: ## Seed development environment
	bash scripts/seed_env.sh

clean: ## Clean generated files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf artifacts/harness/outputs/*

docs: ## Build documentation
	mkdocs build

docs-serve: ## Serve documentation locally
	mkdocs serve

version: ## Show version information
	@echo "Legend Guardian Agent"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "FastAPI: $$($(PYTHON) -c 'import fastapi; print(fastapi.__version__)')"
	@echo "Git SHA: $$(git rev-parse --short HEAD)"

health: ## Check health of running services
	@echo "Checking service health..."
	@curl -s http://localhost:$(PORT)/health | jq '.' || echo "Agent not running"
	@curl -s http://localhost:6300/api/server/v1/info | jq '.message' || echo "Engine not running"
	@curl -s http://localhost:6100/api/info | jq '.message' || echo "SDLC not running"
	@curl -s http://localhost:6200/api/info | jq '.message' || echo "Depot not running"