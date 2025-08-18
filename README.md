# Legend Guardian Agent

A single intelligent agent that monitors and manages the FINOS Legend platform, providing automated model validation, service generation, and deployment automation.

## 🚀 Features

### Core Capabilities
- **Model Change Monitoring**: Automatically detects and analyzes model changes
- **Impact Assessment**: Determines change impact levels (low, medium, high, critical)
- **Action Planning**: Creates automated action plans based on change analysis
- **Service Validation**: Validates models and services through Legend Engine
- **Memory Management**: Maintains history of all agent interactions and decisions

### Agent Capabilities
- **Model Validation**: Ensures model correctness and completeness
- **Service Generation**: Automates service creation and updates
- **Test Execution**: Runs automated test suites
- **Deployment Automation**: Manages deployment processes
- **Performance Monitoring**: Tracks system performance and health

## 🏗️ Architecture

The system consists of a single Guardian Agent that integrates with the FINOS Legend platform:

```
┌─────────────────────────────────────────────────────────────┐
│                    Legend Guardian Agent                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Event        │  │   Analysis      │  │   Action        │ │
│  │   Handler      │  │   Engine        │  │   Executor      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Memory       │  │   Engine        │  │   SDLC          │ │
│  │   System       │  │   Client        │  │   Client        │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    FINOS Legend Platform                    │
│                        (Azure AKS)                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Legend    │  │   Legend    │  │   Legend    │        │
│  │   Engine    │  │   SDLC      │  │   Studio    │        │
│  │  (Port 6060)│  │  (Port 7070)│  │  (Port 9000)│        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Requirements

- **Python**: 3.8+
- **Memory**: 4GB+ RAM (recommended)
- **Services**: Access to Legend Engine and SDLC services
- **Network**: Internet connection for external integrations

## 🛠️ Installation

### 1. Clone Repository
```bash
git clone https://github.com/atheryon-ai/legend-guardian-workspace.git
cd legend-guardian-workspace
```

### 2. Setup Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment
Create a `.env` file:
```bash
# Legend Platform Configuration
LEGEND_ENGINE_URL=http://52.186.106.13:6060
LEGEND_SDLC_URL=http://52.186.106.13:7070
LEGEND_API_KEY=your-legend-api-key

# API Configuration
LEGEND_API_HOST=0.0.0.0
LEGEND_API_PORT=8000
LEGEND_API_DEBUG=false

# Security
VALID_API_KEYS=key1,key2,key3

# Logging
LEGEND_LOG_LEVEL=INFO
```

## 🚀 Quick Start

### **Local Development (Testing Only)**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### **Azure AKS Deployment (Production)**
```bash
cd azure-deployment
./deploy-guardian-agent.sh
```

The agent will be deployed to Azure AKS and accessible via the configured ingress.

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation.

### Test the Agent
```bash
# Health check
curl http://localhost:8000/health

# Handle a model change
curl -X POST "http://localhost:8000/api/v1/model/change" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "model_modification",
    "model_id": "Person",
    "details": {"field": "name", "change": "type modification"}
  }'
```

## 📚 API Endpoints

### Core Operations
- `POST /api/v1/model/change` - Handle model change events
- `POST /api/v1/model/validate` - Validate specific models
- `GET /api/v1/system/status` - Get system status and agent information

### Memory & History
- `GET /api/v1/memory/events` - Get recent events
- `GET /api/v1/memory/events/{event_type}` - Get events by type

### System
- `GET /health` - Health check
- `GET /` - Service information and endpoint list

## 🔧 Configuration

### Environment Variables
All configuration uses the `LEGEND_` prefix:

```bash
# Legend Platform
LEGEND_ENGINE_URL=http://52.186.106.13:6060
LEGEND_SDLC_URL=http://52.186.106.13:7070
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

## 🧪 Testing

### Run Tests
```bash
pytest tests/ -v
```

### Test Coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

## 🚀 Deployment

### Docker
```bash
# Build and run
docker build -t legend-guardian-agent .
docker run -p 8000:8000 legend-guardian-agent
```

### Docker Compose
```bash
# Start all services
docker-compose up -d
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

## 📊 Monitoring

### Health Checks
- **System Health**: Overall agent status
- **Agent Status**: Individual agent availability and performance
- **Service Dependencies**: Legend Engine and SDLC connectivity
- **Memory Usage**: Event history and storage metrics

### Metrics
- **Performance**: Response times, throughput, error rates
- **Agent**: Task completion rates, execution times
- **System**: Memory usage, uptime, health status

## 🔒 Security

### Authentication
- Bearer token authentication
- API key validation
- Configurable API key management

### Data Protection
- Secure communication with Legend services
- Memory isolation and cleanup
- Audit logging for all operations

## 🏗️ Development

### Project Structure
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

### Adding New Capabilities
1. Extend `AgentCapability` enum in `src/agent/models.py`
2. Add new action handlers in `src/agent/guardian_agent.py`
3. Update API endpoints in `src/api/main.py`
4. Add tests in `tests/`

### Code Standards
- **Formatting**: Black code formatter
- **Style**: PEP 8 guidelines
- **Types**: Full type hints
- **Docs**: Comprehensive docstrings

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Testing
- Add tests for new features
- Maintain test coverage
- Use pytest for testing

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- [API Documentation](http://localhost:8000/docs)
- [Development Guide](docs/README.md)
- [Architecture Guide](docs/architecture.md)

### Issues
- Report bugs via GitHub Issues
- Request features via GitHub Discussions
- Check existing issues for solutions

---

**Note**: This is a Guardian Agent for the FINOS Legend platform. Please ensure you have proper access to Legend services and follow FINOS guidelines for platform integration.