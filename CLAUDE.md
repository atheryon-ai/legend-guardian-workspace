# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Legend Guardian Agent - A single intelligent agent that monitors and manages the FINOS Legend platform, providing automated model validation, service generation, and deployment automation.

## Development Commands

### Setup and Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (create .env file with required variables)
cp .env.example .env  # If example exists, otherwise create manually
```

### Running the Application
```bash
# Local development
python main.py

# Docker
docker build -t legend-guardian-agent .
docker run -p 8000:8000 legend-guardian-agent

# Docker Compose (includes Legend services for development)
docker-compose up -d
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_agent.py -v
```

### Code Quality
```bash
# Format code with Black
black src/ tests/

# Check code style
flake8 src/ tests/
```

### Deployment
```bash
# Azure AKS deployment
cd azure-deployment
./deploy-guardian-agent.sh

# Kubernetes deployment
kubectl apply -f k8s/
```

## Architecture Overview

The system follows a layered microservice architecture with a central Guardian Agent:

### Core Flow
1. **Event Reception**: FastAPI endpoint receives model change events
2. **Analysis**: Guardian Agent analyzes the change and determines impact level (low/medium/high/critical)
3. **Action Planning**: Creates automated action plans based on change analysis
4. **Execution**: Executes plans through Legend Engine/SDLC clients
5. **Memory Storage**: Stores all interactions for audit and learning

### Key Components

**Guardian Agent** (`src/agent/guardian_agent.py`)
- Central orchestrator handling the 4-step process (analyze → plan → execute → store)
- Integrates with Legend platform services
- Maintains decision history in memory system

**API Layer** (`src/api/main.py`)
- FastAPI application exposing REST endpoints
- Bearer token authentication with configurable API keys
- Main endpoints: `/api/v1/model/change`, `/api/v1/model/validate`, `/api/v1/system/status`

**Legend Clients** (`src/agent/clients/`)
- `legend_engine.py`: Interfaces with Legend Engine (port 6060)
- `legend_sdlc.py`: Interfaces with Legend SDLC (port 7070)
- Both use aiohttp for async HTTP communication

**Memory System** (`src/agent/memory.py`)
- Stores analyses, plans, and results
- Automatic cleanup (keeps last 1000 entries)
- Provides history retrieval by event type

**Configuration** (`src/config/settings.py`)
- Pydantic BaseSettings with environment variable loading
- All config uses `LEGEND_` prefix
- Supports .env files for local development

## Environment Configuration

Required environment variables:
```bash
# Legend Platform (Azure AKS endpoints)
LEGEND_ENGINE_URL=http://52.186.106.13:6060
LEGEND_SDLC_URL=http://52.186.106.13:7070
LEGEND_API_KEY=your-legend-api-key

# API Configuration
LEGEND_API_HOST=0.0.0.0
LEGEND_API_PORT=8000
LEGEND_API_DEBUG=false

# Security
VALID_API_KEYS=key1,key2,key3  # Comma-separated list

# Logging
LEGEND_LOG_LEVEL=INFO
```

## Testing Strategy

- Unit tests in `tests/` directory using pytest
- Test models, memory system, and core functionality
- No integration tests currently - Legend services must be mocked
- Tests use pytest-asyncio for async functionality

## Deployment Targets

**Local Development**: Run directly with Python or use Docker Compose
**Production**: Azure AKS with Kubernetes manifests in `k8s/` directory
- Resource limits: 512Mi-1Gi RAM, 250m-500m CPU
- Uses Azure Container Registry (ACR)
- Resource group: `rs-finos-legend`

## API Authentication

All API endpoints (except `/health` and `/`) require Bearer token authentication:
```bash
curl -H "Authorization: Bearer your-api-key" http://localhost:8000/api/v1/model/change
```

## Important Patterns

1. **Async Operations**: Legend clients use aiohttp for non-blocking I/O
2. **Error Handling**: Comprehensive try-catch blocks with structured logging
3. **Memory Management**: Automatic cleanup prevents unbounded growth
4. **Configuration**: Environment-based with Pydantic validation
5. **Security**: Non-root Docker user, API key authentication, no hardcoded secrets

## Common Development Tasks

### Adding New Agent Capabilities
1. Extend `AgentCapability` enum in `src/agent/models.py`
2. Add handler method in `GuardianAgent` class
3. Update API endpoint if needed
4. Add corresponding tests

### Modifying Legend Integration
- Legend Engine client: `src/agent/clients/legend_engine.py`
- Legend SDLC client: `src/agent/clients/legend_sdlc.py`
- Both follow similar async patterns with error handling

### Updating API Endpoints
1. Add route in `src/api/main.py`
2. Create request/response models in `src/api/models.py`
3. Implement business logic in Guardian Agent
4. Add authentication via `Depends(get_current_user)`

### Commit and Pull Request Guidelines

#### Commit Messages
- Use concise, imperative mood (e.g., "Add validation", "Fix memory leak", "Update dependencies")
- Include scope in subject when relevant: "feat: Add model validation endpoint"
- Keep subject line under 50 characters
- Add body for complex changes explaining the "why"

#### Pull Requests
- Include clear description of changes
- Link related issues with "Fixes #123" or "Relates to #456"
- Include test results and coverage
- Update documentation and diagrams when UI/API changes
- Run quality checks before opening PR:
  ```bash
  black src/ tests/
  flake8 src/ tests/
  pytest tests/ -v
  ```