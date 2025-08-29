.PHONY: dev lint test docker-build docker-up harness openapi

dev:
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

lint:
	@echo "Linting not yet implemented"

test:
	@echo "Testing not yet implemented"

docker-build:
	@echo "Docker build not yet implemented"

docker-up:
	@echo "Docker up not yet implemented"

harness:
	@echo "Harness not yet implemented"

openapi:
	@echo "OpenAPI export not yet implemented"