# Atheryon FINOS Legend Deployment Makefile

.PHONY: help install docker-build docker-compose docker-compose-down docker-compose-logs clean

help: ## Show this help message
	@echo "Atheryon FINOS Legend Deployment"
	@echo "================================"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies (not needed for Docker deployment)
	@echo "No dependencies to install for Docker deployment"
	@echo "Use 'make docker-compose' to deploy Legend platform"

docker-build: ## Build Legend platform Docker images
	cd deploy/docker && docker-compose build

docker-compose: ## Deploy Legend platform with Docker Compose
	cd deploy/docker && docker-compose up -d

docker-compose-down: ## Stop Legend platform services
	cd deploy/docker && docker-compose down

docker-compose-logs: ## View Legend platform logs
	cd deploy/docker && docker-compose logs -f

clean: ## Clean up Docker resources
	cd deploy/docker && docker-compose down -v
	docker system prune -f

