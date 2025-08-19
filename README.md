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
│  │  (Port 6300)│  │  (Port 6100)│  │  (Port 9000)│        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### **Deployment Architecture**

The platform supports multiple deployment patterns:

#### **Local Development Stack**
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Studio    │────▶│    Engine    │────▶│    SDLC     │
│  (Port 9000)│     │ (Port 6300)  │     │ (Port 6100) │
└─────────────┘     └──────────────┘     └─────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │   MongoDB    │
                    │ (Port 27017) │
                    └──────────────┘
```

#### **Production Azure AKS Stack**
```
┌─────────────────────────────────────────────────────────────┐
│                    Azure AKS Cluster                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Legend    │  │   Legend    │  │   Legend    │        │
│  │   Engine    │  │   SDLC      │  │   Studio    │        │
│  │  (Port 6300)│  │  (Port 6100)│  │  (Port 9000)│        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   MongoDB   │  │   Guardian  │  │   Ingress   │        │
│  │   Database  │  │    Agent    │  │ Controller  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

#### **Service Dependencies**
```
MongoDB (Required by all)
    ↑
Legend Engine (Core service)
    ↑
Legend SDLC (Depends on Engine)
    ↑
Legend Studio (Depends on Engine & SDLC)
    ↑
Guardian Agent (Monitors all above)
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

# 1. Setup environment configuration
cp azure-legend.env.example azure-legend.env
# Edit azure-legend.env with your Azure and Legend configuration

# 2. Deploy Azure infrastructure
./deploy-azure.bash

# 3. Build and push Legend images
./build-and-push-images.sh

# 4. Deploy Legend platform
./deploy-legend.sh
```

The agent will be deployed to Azure AKS and accessible via the configured ingress.

**Note**: All configuration is now centralized in `azure-legend.env` - see [Azure Deployment README](azure-deployment/README.md) for complete details.

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

### **Deployment Configuration**

#### **Environment Variables Hierarchy**
The new modular system uses a hierarchical configuration approach:

1. **`deploy/common.env`** - Shared across all services
   - Azure infrastructure settings
   - Kubernetes configuration
   - GitLab OAuth credentials
   - MongoDB connection
   - Legend versions

2. **Service-specific .env files** - Override/extend common variables
   - `deploy/legend-engine/engine.env`
   - `deploy/legend-sdlc/sdlc.env`
   - `deploy/legend-studio/studio.env`
   - `deploy/legend-guardian/guardian.env`
   - `deploy/mongodb/mongodb.env`

#### **Azure Deployment Configuration**
For Azure deployments, all configuration is centralized in `deploy/azure/azure-legend.env`:

```bash
# Azure Infrastructure
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group-name
AZURE_AKS_CLUSTER=your-aks-cluster-name

# Legend Services
LEGEND_ENGINE_URL=https://legend-engine.your-domain.com
LEGEND_ENGINE_PORT=6300
LEGEND_ENGINE_VERSION=4.40.3

# MongoDB
MONGODB_URI=mongodb://admin:[PASSWORD]@mongo-legend-[UNIQUE_SUFFIX].mongo.cosmos.azure.com:10255/legend?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@mongo-legend-[UNIQUE_SUFFIX]@

# GitLab OAuth
GITLAB_APP_ID=your-gitlab-app-id
GITLAB_APP_SECRET=your-gitlab-app-secret
```

#### **Customizing Deployments**

**Change Resource Limits:**
```bash
# Edit deploy/legend-engine/engine.env
ENGINE_MEMORY_REQUEST=1Gi
ENGINE_MEMORY_LIMIT=4Gi
ENGINE_CPU_REQUEST=1000m
ENGINE_CPU_LIMIT=2000m
```

**Scale Replicas:**
```bash
# Edit deploy/legend-engine/engine.env
ENGINE_REPLICAS=3
```

**Change Versions:**
```bash
# Edit deploy/common.env
LEGEND_ENGINE_VERSION=4.40.3
LEGEND_SDLC_VERSION=0.195.0
LEGEND_STUDIO_VERSION=13.113.0
```

**See [Deployment README](deploy/README.md) for complete configuration details.**

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

The Legend platform can be deployed using multiple approaches, from local development to production Azure AKS clusters.

### **Local Development (Docker Compose)**
```bash
# Start all services locally
cd deploy/local
docker-compose up -d

# Check status
docker ps

# Access services
# Legend Engine: http://localhost:6300
# Legend SDLC: http://localhost:6100
# Legend Studio: http://localhost:9000
# MongoDB: localhost:27017
```

### **Modular Deployment System**
The new modular deployment system allows you to deploy services individually or all at once:

```bash
cd deploy

# Deploy everything (interactive menu)
./deploy-all.sh

# Deploy individual services
./mongodb/deploy.sh deploy
./legend-engine/deploy.sh deploy
./legend-sdlc/deploy.sh deploy
./legend-studio/deploy.sh deploy
./legend-guardian/deploy.sh deploy

# Check status
./deploy-all.sh status

# Validate deployments
./validate.sh

# Clean up
./deploy-all.sh clean
```

### **Azure AKS Deployment (Production)**
```bash
cd deploy/azure

# 1. Setup environment configuration
cp azure-legend.env.example azure-legend.env
# Edit azure-legend.env with your Azure and Legend configuration

# 2. Deploy to Azure AKS
./deploy.sh

# 3. Check status
./deploy.sh status

# 4. Port forward for access
kubectl port-forward -n legend-system svc/legend-studio 9000:80
kubectl port-forward -n legend-system svc/legend-engine 6060:6060
kubectl port-forward -n legend-system svc/legend-sdlc 7070:7070
```

### **Docker Images**
```bash
# Build and run individual services
docker build -t legend-guardian-agent .
docker run -p 8000:8000 legend-guardian-agent

# Or use the modular system
cd deploy/docker
docker build -f Dockerfile.engine -t legend-engine .
docker build -f Dockerfile.sdlc -t legend-sdlc .
docker build -f Dockerfile.studio -t legend-studio .
```

### **Kubernetes (Direct)**
```bash
# Apply all manifests
kubectl apply -f deploy/azure/

# Or apply individual services
kubectl apply -f deploy/legend-engine/k8s/
kubectl apply -f deploy/legend-sdlc/k8s/
kubectl apply -f deploy/legend-studio/k8s/
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

### **Service Health Endpoints**
- Engine: http://service:6300/api/server/v1/info
- SDLC: http://service:6100/api/info
- Studio: http://service:9000/
- Guardian: http://service:8000/health

### **Production Monitoring**
- Enable Prometheus metrics collection
- Use Grafana dashboards for visualization
- Set up alerts for critical issues

## 🔍 Troubleshooting

### **Deployment Issues**

#### **Check Deployment Status**
```bash
# All services status
cd deploy
./deploy-all.sh status

# Individual service status
./legend-engine/deploy.sh status
./mongodb/deploy.sh status
```

#### **Validate Deployments**
```bash
# Platform-wide validation
./validate.sh

# Service-specific validation
./legend-engine/deploy.sh validate
```

### **Kubernetes Issues**

#### **Check Logs**
```bash
# All pods in namespace
kubectl logs -n legend-system -l app=legend-engine

# Specific pod
kubectl logs -n legend-system legend-engine-xyz

# Follow logs
kubectl logs -n legend-system -l app=legend-engine -f
```

#### **Common Issues**

**Pod Not Starting:**
```bash
# Check events
kubectl describe pod -n legend-system legend-engine-xyz

# Check resource limits
kubectl top pods -n legend-system
```

**Service Not Accessible:**
```bash
# Check service endpoints
kubectl get endpoints -n legend-system

# Test connectivity
kubectl exec -n legend-system legend-studio-xyz -- curl http://legend-engine:6300/api/server/v1/info
```

**Database Connection Issues:**
```bash
# Test MongoDB connection
kubectl exec -n legend-system mongodb-xyz -- mongosh --eval "db.adminCommand('ping')"
```

### **Local Development Issues**

#### **Docker Compose Problems**
```bash
# Check service status
cd deploy/local
docker-compose ps

# View logs
docker-compose logs legend-engine
docker-compose logs legend-sdlc
docker-compose logs legend-studio

# Restart services
docker-compose restart
```

#### **Port Conflicts**
```bash
# Check what's using ports
lsof -i :6300  # Legend Engine
lsof -i :6100  # Legend SDLC
lsof -i :9000  # Legend Studio
lsof -i :27017 # MongoDB
```

### **Azure AKS Issues**

#### **Image Pull Errors**
```bash
# Create ACR secret
kubectl create secret docker-registry acr-secret \
  --docker-server=legendacr.azurecr.io \
  --docker-username=$(az acr credential show --name legendacr --query username -o tsv) \
  --docker-password=$(az acr credential show --name legendacr --query passwords[0].value -o tsv) \
  -n legend-system

# Patch deployments
kubectl patch deployment legend-studio -n legend-system \
  -p '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"acr-secret"}]}}}}'
```

#### **Port Forwarding (Azure)**
```bash
kubectl port-forward -n legend-system svc/legend-studio 9000:80
kubectl port-forward -n legend-system svc/legend-engine 6060:6060
kubectl port-forward -n legend-system svc/legend-sdlc 7070:7070
```

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

deploy/                      # 🆕 Deployment configurations
├── common.env               # Shared environment variables
├── deploy-all.sh            # Master deployment orchestrator
├── validate.sh              # Platform-wide validation
├── legend-engine/           # Legend Engine Service
│   ├── engine.env          # Engine-specific variables
│   ├── deploy.sh           # Engine deployment script
│   ├── config/             # Engine configuration files
│   └── k8s/                # Engine Kubernetes manifests
├── legend-sdlc/             # Legend SDLC Service
│   ├── sdlc.env            # SDLC-specific variables
│   ├── deploy.sh           # SDLC deployment script
│   ├── config/             # SDLC configuration files
│   └── k8s/                # SDLC Kubernetes manifests
├── legend-studio/           # Legend Studio Service
│   ├── studio.env          # Studio-specific variables
│   ├── deploy.sh           # Studio deployment script
│   └── k8s/                # Studio Kubernetes manifests
├── legend-guardian/         # Guardian Agent Service
│   ├── guardian.env        # Guardian-specific variables
│   ├── deploy.sh           # Guardian deployment script
│   └── k8s/                # Guardian Kubernetes manifests
├── mongodb/                 # MongoDB Service
│   ├── mongodb.env         # MongoDB-specific variables
│   ├── deploy.sh           # MongoDB deployment script
│   └── k8s/                # MongoDB Kubernetes manifests
├── azure/                   # Azure-specific deployments
│   ├── azure-legend.env    # Azure environment config
│   ├── deploy.sh           # Azure deployment script
│   └── ...                 # Other Azure resources
├── local/                   # Local development
│   ├── docker-compose.yml  # Local stack
│   └── start.sh            # Local startup script
└── docker/                  # Docker images
    ├── Dockerfile.engine
    ├── Dockerfile.sdlc
    └── Dockerfile.studio
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

## 🆕 **New Modular Deployment System**

The platform now includes a comprehensive modular deployment system in the `deploy/` directory that provides:

- **Service-by-service deployment** with individual configuration
- **Environment-specific configurations** for dev/staging/prod
- **Centralized orchestration** with `deploy-all.sh`
- **Built-in validation** and health checks
- **Local development** with Docker Compose
- **Production deployment** to Azure AKS

**See [Deployment README](deploy/README.md) for complete details on the new system.**