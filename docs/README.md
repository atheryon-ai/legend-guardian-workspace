# Legend Guardian Agent Documentation

## Overview

The Legend Guardian Agent is a single intelligent agent that monitors and manages the FINOS Legend platform. It provides automated model validation, service generation, and deployment automation.

## Architecture

```
src/
├── agent/                    # Core agent functionality
│   ├── guardian_agent.py    # Main Guardian Agent class
│   ├── memory.py            # Agent memory system
│   ├── models.py            # Data models and structures
│   └── clients/             # External service clients
│       ├── legend_engine.py # Legend Engine client
│       └── legend_sdlc.py   # Legend SDLC client
├── api/                     # FastAPI web service
│   ├── main.py             # Main API application
│   └── models.py           # API request/response models
└── config/                  # Configuration management
    └── settings.py          # Application settings
```

## Key Components

### 1. Guardian Agent (`src/agent/guardian_agent.py`)
- **Purpose**: Main agent that handles model change events
- **Workflow**: Event → Analysis → Planning → Execution → Memory Storage
- **Capabilities**: Model validation, service validation, test execution, deployment automation

### 2. Memory System (`src/agent/memory.py`)
- **Purpose**: Stores all agent interactions and decisions
- **Features**: Event history, analysis results, action plans, execution results
- **Management**: Automatic cleanup to prevent memory bloat

### 3. External Clients (`src/agent/clients/`)
- **Legend Engine Client**: Integrates with Legend Engine service (port 6300)
- **Legend SDLC Client**: Integrates with Legend SDLC service (port 6100)

### 4. API Service (`src/api/main.py`)
- **Framework**: FastAPI with OpenAPI documentation
- **Endpoints**: Model change handling, validation, system status, memory queries
- **Security**: Bearer token authentication

## Usage Examples

### Starting the Service
```bash
python main.py
```

### Handling Model Changes
```python
from src.agent import LegendGuardianAgent, ModelChangeEvent
from datetime import datetime

# Initialize agent
agent = LegendGuardianAgent(
    legend_engine_url="http://localhost:6300",
    legend_sdlc_url="http://localhost:6100"
)

# Create model change event
event = ModelChangeEvent(
    event_type="model_modification",
    model_id="Person",
    timestamp=datetime.now(),
    details={"field": "name", "change": "type modification"}
)

# Handle the event
result = await agent.handle_model_change(event)
print(f"Success: {result.success}, Time: {result.execution_time}s")
```

### API Usage
```bash
# Health check
curl http://localhost:8000/health

# Handle model change
curl -X POST "http://localhost:8000/api/v1/model/change" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "model_modification",
    "model_id": "Person",
    "details": {"field": "name", "change": "type modification"}
  }'
```

## Configuration

### Environment Variables
```bash
# Legend Platform
LEGEND_ENGINE_URL=http://localhost:6300
LEGEND_SDLC_URL=http://localhost:6100
LEGEND_API_KEY=your-key

# API Settings
LEGEND_API_HOST=0.0.0.0
LEGEND_API_PORT=8000
LEGEND_API_DEBUG=false

# Security
VALID_API_KEYS=key1,key2,key3

# Logging
LEGEND_LOG_LEVEL=INFO
```

## Testing

### Run Tests
```bash
pytest tests/ -v
```

### Test Coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

## Deployment

### Docker
```bash
docker build -t legend-guardian-agent .
docker run -p 8000:8000 legend-guardian-agent
```

### Docker Compose
```bash
docker-compose up -d
```

## Monitoring

### Health Endpoints
- `/health` - Basic health check
- `/api/v1/system/status` - Detailed system status

### Memory Queries
- `/api/v1/memory/events` - Recent events
- `/api/v1/memory/events/{event_type}` - Events by type

## Development

### Code Structure
- **Modular Design**: Clear separation of concerns
- **Type Hints**: Full type annotation support
- **Async Support**: Non-blocking I/O operations
- **Error Handling**: Comprehensive error management

### Adding New Capabilities
1. Extend `AgentCapability` enum in `models.py`
2. Add new action handlers in `guardian_agent.py`
3. Update API endpoints in `main.py`
4. Add tests in `tests/`

### Best Practices
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Add tests for new functionality
- Update documentation for changes
