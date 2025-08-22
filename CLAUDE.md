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
cp deploy/base.env .env  # Start with base configuration
# Edit .env with your specific values
```

### Running the Application
```bash
# Local development with hot reload
python main.py

# Docker standalone
docker build -t legend-guardian-agent .
docker run -p 8000:8000 --env-file .env legend-guardian-agent

# Full platform with Docker Compose (includes all Legend services)
cd deploy/local
./start.sh
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_agent.py -v

# Run specific test
pytest tests/test_agent.py::TestGuardianAgent::test_analyze -v
```

### Code Quality
```bash
# Format code with Black
black src/ tests/

# Check code style  
flake8 src/ tests/

# Run both formatting and linting
black src/ tests/ && flake8 src/ tests/
```

### Deployment
```bash
# Deploy entire Legend platform (K8s)
cd deploy
./deploy-all.sh deploy

# Deploy only Guardian Agent
cd deploy/legend-guardian
./deploy.sh deploy

# Azure deployment with ACR
cd deploy/azure
./build-and-push-images.sh
./deploy.sh

# Validate deployment
cd deploy
./deploy-all.sh validate
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

Configuration is managed through modular environment files in `deploy/`:
- `base.env`: Core configuration shared across all environments
- `deploy/local/local.env`: Local development overrides
- `deploy/azure/azure.env`: Azure-specific configuration

Required environment variables:
```bash
# Legend Platform endpoints
LEGEND_ENGINE_URL=http://legend-engine:6060  # K8s service name or external URL
LEGEND_SDLC_URL=http://legend-sdlc:7070
LEGEND_STUDIO_URL=http://legend-studio:9000
LEGEND_API_KEY=your-legend-api-key

# API Configuration
LEGEND_API_HOST=0.0.0.0
LEGEND_API_PORT=8000
LEGEND_API_DEBUG=false

# Security
VALID_API_KEYS=key1,key2,key3  # Comma-separated list

# Database
MONGODB_URI=mongodb://mongodb:27017
MONGODB_DATABASE=legend

# Logging
LEGEND_LOG_LEVEL=INFO
```

## Testing Strategy

- Unit tests in `tests/` directory using pytest
- Test models, memory system, and core functionality
- No integration tests currently - Legend services must be mocked
- Tests use pytest-asyncio for async functionality

## Deployment Architecture

The deployment system uses a modular architecture in `deploy/`:

```
deploy/
├── deploy-all.sh          # Master deployment orchestrator
├── validate-config.sh     # Configuration validation
├── lib/
│   └── common-functions.sh # Shared deployment functions
├── legend-engine/         # Engine service deployment
├── legend-sdlc/           # SDLC service deployment  
├── legend-studio/         # Studio UI deployment
├── legend-guardian/       # Guardian agent deployment
├── mongodb/               # Database deployment
├── local/                 # Local Docker Compose setup
├── azure/                 # Azure AKS deployment scripts
└── k8s/                   # Base Kubernetes manifests
```

### Deployment Targets

**Local Development**: Docker Compose with all services
- Run: `cd deploy/local && ./start.sh`
- Services available on localhost ports

**Kubernetes (Production)**: Modular service deployment
- Full platform: `./deploy-all.sh deploy`
- Individual service: `./legend-guardian/deploy.sh deploy`
- Resource limits: 512Mi-1Gi RAM, 250m-500m CPU

**Azure AKS**: Production deployment with ACR
- Resource group: `rs-finos-legend`
- Uses Azure Container Registry for images
- Automated via GitHub Actions (when configured)

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

## Key Development Patterns

### Adding New Agent Capabilities
1. Extend `AgentCapability` enum in `src/agent/models.py`
2. Add handler method in `GuardianAgent` class (`src/agent/guardian_agent.py`)
3. Update API endpoint if needed in `src/api/main.py`
4. Add corresponding tests in `tests/`
5. Run tests to verify: `pytest tests/ -v`

### Modifying Legend Integration
- Legend Engine client: `src/agent/clients/legend_engine.py`
- Legend SDLC client: `src/agent/clients/legend_sdlc.py`
- Both use aiohttp for async HTTP communication
- Follow existing error handling patterns with try-catch blocks

### Updating API Endpoints
1. Add route in `src/api/main.py`
2. Create request/response models in `src/api/models.py`
3. Implement business logic in Guardian Agent
4. Add authentication via `Depends(get_current_user)`
5. Update OpenAPI docs will auto-generate at `/docs`

### Deployment Configuration Updates
1. Modify base configuration in `deploy/base.env`
2. Add environment-specific overrides in respective directories
3. Validate configuration: `./deploy/validate-config.sh`
4. Test locally first: `cd deploy/local && ./start.sh`

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