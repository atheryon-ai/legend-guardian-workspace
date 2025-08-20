# Legend Platform Deployment

Modular deployment system for the FINOS Legend platform with per-service management and Azure AKS support.

## 🚀 Quick Start

### **Deploy Everything (Recommended)**
```bash
cd deploy

# Interactive menu
./deploy-all.sh

# Or direct deployment
./deploy-all.sh deploy
```

### **Deploy Individual Services**
```bash
cd deploy

# Deploy only MongoDB
./mongodb/deploy.sh deploy

# Deploy only Legend Engine
./legend-engine/deploy.sh deploy

# Deploy only Legend SDLC
./legend-sdlc/deploy.sh deploy

# Deploy only Legend Studio
./legend-studio/deploy.sh deploy

# Deploy Guardian Agent
./legend-guardian/deploy.sh deploy
```

### **Azure AKS Deployment**
```bash
cd deploy/azure

# 1. Setup environment configuration
cp azure-legend.env.example azure-legend.env
# Edit azure-legend.env with your Azure configuration

# 2. Deploy Azure infrastructure
./deploy-azure.bash

# 3. Build and push Docker images
./build-and-push-images.sh

# 4. Process Kubernetes manifests
./process-k8s-manifests.sh

# 5. Deploy Legend services to AKS
cd ..
./deploy-all.sh deploy
```

## 📁 Directory Structure

```
deploy/
├── common.env                  # Shared environment variables
├── deploy-all.sh              # Master deployment orchestrator
├── validate.sh                # Platform-wide validation
├── README.md                  # This documentation file
├── README 2.md                # Additional deployment notes
├── config/                    # Global configuration files
│   ├── engine-config.yml      # Legend Engine configuration
│   └── sdlc-config.yml        # Legend SDLC configuration
├── k8s/                       # Shared Kubernetes resources
│   ├── namespace.yaml         # Namespace and configmap
│   └── secrets.yaml           # Shared secrets
├── legend-engine/             # Legend Engine Service
│   ├── engine.env            # Engine-specific variables
│   ├── deploy.sh             # Engine deployment script
│   ├── config/               # Engine configuration
│   │   └── engine-config.yml # Engine config file
│   └── k8s/                  # Engine Kubernetes manifests
│       └── engine.yaml
├── legend-sdlc/               # Legend SDLC Service
│   ├── sdlc.env              # SDLC-specific variables
│   ├── deploy.sh             # SDLC deployment script
│   └── k8s/                  # SDLC Kubernetes manifests
│       └── sdlc.yaml
├── legend-studio/             # Legend Studio Service
│   ├── studio.env            # Studio-specific variables
│   └── k8s/                  # Studio Kubernetes manifests
│       └── studio.yaml
├── legend-guardian/           # Guardian Agent Service
│   ├── guardian.env          # Guardian-specific variables
│   └── k8s/                  # Guardian Kubernetes manifests
│       └── guardian.yaml
├── mongodb/                   # MongoDB Service
│   ├── mongodb.env           # MongoDB-specific variables
│   └── k8s/                  # MongoDB Kubernetes manifests
│       └── mongodb.yaml
├── azure/                     # Azure-specific deployments
│   ├── azure-legend.env      # Azure environment config
│   ├── azure-legend.env.example # Azure environment template
│   ├── azure-resources.bicep # Azure infrastructure template
│   ├── deploy.sh             # Azure deployment script
│   ├── deploy-azure.bash     # Azure infrastructure deployment
│   ├── build-and-push-images.sh # Docker image management
│   ├── process-k8s-manifests.sh # Manifest processing
│   └── generate-api-keys.sh  # API key generation
├── local/                     # Local development
│   ├── docker-compose.yml    # Local stack
│   ├── start.sh              # Local startup script
│   ├── README.md             # Local development guide
│   └── config/               # Local configuration
│       ├── engine-config.yml # Local engine config
│       └── sdlc-config.yml   # Local SDLC config
└── docker/                    # Docker images
    ├── Dockerfile.engine     # Engine Dockerfile
    ├── Dockerfile.sdlc       # SDLC Dockerfile
    └── Dockerfile.studio     # Studio Dockerfile
```

## 🔧 Configuration

### **Secrets Management**

Before deploying, you need to configure your secrets:

```bash
# Run the secrets setup script
./setup-secrets.sh

# Or manually create secrets.env from template
cp secrets.example secrets.env
# Edit secrets.env with your real values
```

**Important:** Never commit your `secrets.env` file to git!

### **Configuration Files Hierarchy**

1. **`common.env`** - Shared across all services
   - Azure infrastructure settings
   - Kubernetes configuration
   - GitLab OAuth credentials
   - MongoDB connection
   - Legend versions

2. **`config/`** - Global configuration files
   - `engine-config.yml` - Legend Engine configuration
   - `sdlc-config.yml` - Legend SDLC configuration

3. **Service-specific .env files** - Override/extend common variables
   - `legend-engine/engine.env`
   - `legend-sdlc/sdlc.env`
   - `legend-studio/studio.env`
   - `legend-guardian/guardian.env`
   - `mongodb/mongodb.env`

4. **Service-specific config files** - Service configurations
   - `legend-engine/config/engine-config.yml`
   - `local/config/engine-config.yml` (local development)
   - `local/config/sdlc-config.yml` (local development)

### **Environment Variables and Secrets**

The deployment system automatically loads secrets in this order:
1. **`secrets.env`** - Your real production secrets (git-ignored)
2. **`.env.local`** - Alternative secrets file (git-ignored)
3. **`common.env`** - Safe placeholder values (committed to git)

This means:
- **Development**: Use `secrets.env` with real values
- **CI/CD**: Use environment variables or secure secret management
- **Team sharing**: Share `secrets.example` template

### **Customizing Deployments**

#### **Change Resource Limits**
Edit service-specific env file:
```bash
# legend-engine/engine.env
ENGINE_MEMORY_REQUEST=1Gi
ENGINE_MEMORY_LIMIT=4Gi
ENGINE_CPU_REQUEST=1000m
ENGINE_CPU_LIMIT=2000m
```

#### **Scale Replicas**
```bash
# legend-engine/engine.env
ENGINE_REPLICAS=3
```

#### **Change Versions**
```bash
# common.env
LEGEND_ENGINE_VERSION=4.40.3
LEGEND_SDLC_VERSION=0.195.0
LEGEND_STUDIO_VERSION=13.113.0
```

#### **Modify Service Configuration**
Edit service-specific config files:
```bash
# legend-engine/config/engine-config.yml
# Modify engine behavior, ports, logging, etc.

# legend-sdlc/config/sdlc-config.yml
# Modify SDLC behavior, GitLab integration, etc.
```

## 🧪 Testing

### **Local Testing**
```bash
cd deploy/local
./start.sh

# Or start specific services
./start.sh core      # Core services only
./start.sh all       # All services including Guardian
./start.sh guardian  # Guardian Agent only
```

### **Local Configuration**
The local development environment uses its own configuration files in `local/config/`:
- `local/config/engine-config.yml` - Local engine settings
- `local/config/sdlc-config.yml` - Local SDLC settings

### **Port Forwarding (Azure/K8s)**
```bash
# Forward all services
kubectl port-forward -n legend svc/legend-engine 6300:6300 &
kubectl port-forward -n legend svc/legend-sdlc 6100:6100 &
kubectl port-forward -n legend svc/legend-studio 9000:9000 &

# Access at:
# Engine: http://localhost:6300
# SDLC: http://localhost:6100
# Studio: http://localhost:9000
```

## 📊 Service Dependencies

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

## 🔍 Code Quality

Ensure code quality before deployment:

```bash
# Run comprehensive code quality checks
./deploy/check-code-quality.sh

# Or use Makefile
make code-quality
make quality

# Quick flake8 linting
make lint
```

The code quality check includes:
- **Python Code**: flake8 linting with `.flake8` configuration
- **Shell Scripts**: shellcheck validation (if available)
- **Configuration**: Auto-creates `.flake8` if missing
- **Integration**: Runs automatically during deployment validation

## 🔍 Troubleshooting

### **Check Deployment Status**
```bash
# All services status
cd deploy
./deploy-all.sh status

# Individual service status
./legend-engine/deploy.sh status
./mongodb/deploy.sh status
```

### **Validate Deployments**
```bash
# Platform-wide validation
./validate.sh

# Service-specific validation
./legend-engine/deploy.sh validate
```

### **Check Logs**
```bash
# All pods in namespace
kubectl logs -n legend-system -l app=legend-engine

# Specific pod
kubectl logs -n legend-system legend-engine-xyz

# Follow logs
kubectl logs -n legend-system -l app=legend-engine -f
```

### **Common Issues**

#### **Pod Not Starting**
```bash
# Check events
kubectl describe pod -n legend-system legend-engine-xyz

# Check resource limits
kubectl top pods -n legend-system
```

#### **Service Not Accessible**
```bash
# Check service endpoints
kubectl get endpoints -n legend-system

# Test connectivity
kubectl exec -n legend-system legend-studio-xyz -- curl http://legend-engine:6300/api/server/v1/info
```

#### **Database Connection Issues**
```bash
# Test MongoDB connection
kubectl exec -n legend-system mongodb-xyz -- mongosh --eval "db.adminCommand('ping')"
```

## 🚢 Production Deployment

### **Prerequisites**
1. Configure production values in `common.env`
2. Set up TLS certificates
3. Configure external MongoDB (optional)
4. Set up monitoring

### **Deploy to Production**
```bash
# Set production environment
export ENVIRONMENT=production

# Deploy with production configs
./deploy-all.sh deploy

# Validate deployment
./validate.sh
```

## 🔐 Security Considerations

1. **Secrets Management**
   - Never commit `.env` files with real credentials
   - Use Kubernetes secrets for sensitive data
   - Rotate credentials regularly

2. **Network Security**
   - Use NetworkPolicies to restrict traffic
   - Enable TLS for all external endpoints
   - Use private endpoints for internal services

3. **Access Control**
   - Configure RBAC for Kubernetes access
   - Use GitLab OAuth for Legend SDLC
   - Implement API keys for Guardian Agent

## 📈 Monitoring

### **Health Checks**
- Engine: http://service:6300/api/server/v1/info
- SDLC: http://service:6100/api/info
- Studio: http://service:9000/
- Guardian: http://service:8000/health

### **Metrics**
- Enable Prometheus metrics collection
- Use Grafana dashboards for visualization
- Set up alerts for critical issues

## 🤝 Contributing

When adding new services:
1. Create service folder with standard structure
2. Add service-specific `.env` file
3. Create `deploy.sh` with standard functions
4. Update `deploy-all.sh` to include new service
5. Document in this README

## 📚 Additional Resources

- [Azure Bicep Documentation](https://docs.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
- [AKS Best Practices](https://docs.microsoft.com/en-us/azure/aks/best-practices)
- [FINOS Legend Documentation](https://legend.finos.org/)
- [Kubernetes Manifest Reference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.28/)

---

**Note**: This deployment system provides modular, service-by-service deployment with support for both local development and production Azure AKS environments. For additional deployment notes, see `README 2.md`.
