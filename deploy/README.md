# Legend Platform Deployment

Modular deployment system for the FINOS Legend platform with per-service management and Azure AKS support.

## 🚀 Quick Start

### **Deploy Everything (Recommended)**
```bash
cd deploy

# Master deployment script (interactive)
./deploy.sh

# Or deploy to specific endpoints:

# Kubernetes deployment
cd kubernetes
./deploy-all.sh

# Docker deployment
cd docker
docker-compose up -d

# Or build from source (advanced)
./build-legend-local.sh

# Azure deployment
cd azure
./deploy-azure.bash
```

### **Deploy Individual Services**
```bash
cd deploy

# Deploy only MongoDB
./kubernetes/components/mongodb/deploy.sh deploy

# Deploy only Legend Engine
./kubernetes/components/legend-engine/deploy.sh deploy

# Deploy only Legend SDLC
./kubernetes/components/legend-sdlc/deploy.sh deploy

# Deploy only Legend Studio
./kubernetes/components/legend-studio/deploy.sh deploy

# Deploy Guardian Agent
./kubernetes/components/legend-guardian/deploy.sh deploy
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
├── shared/                    # Shared across all endpoints
│   ├── base.env              # Base configuration (shared by all environments)
│   ├── common.env            # Common environment variables
│   └── lib/                  # Shared bash functions library
├── azure/                    # Azure endpoint
│   ├── azure-legend.env      # Azure environment config
│   ├── azure-legend.env.example # Azure environment template
│   ├── azure-resources.bicep # Azure infrastructure template
│   ├── deploy.sh             # Azure deployment script
│   ├── deploy-azure.bash     # Azure infrastructure deployment
│   ├── build-and-push-images.sh # Docker image management
│   └── process-k8s-manifests.sh # Manifest processing
├── docker/                    # Docker endpoint
│   ├── components/            # All components for Docker
│   │   ├── engine/           # Legend Engine
│   │   │   └── Dockerfile.engine
│   │   ├── sdlc/             # Legend SDLC
│   │   │   └── Dockerfile.sdlc
│   │   ├── studio/           # Legend Studio
│   │   │   └── Dockerfile.studio
│   │   └── guardian/         # Guardian Agent
│   │       └── Dockerfile
│   ├── docker-compose.yml    # Development environment
│   ├── docker-compose.prod.yml # Production environment
│   ├── .dockerignore         # Docker build optimization
│   └── README_DOCKER.md      # Docker documentation
├── kubernetes/                # Kubernetes endpoint
│   ├── components/            # All components for K8s
│   │   ├── legend-engine/    # Legend Engine Service
│   │   │   ├── engine.env    # Engine-specific variables
│   │   │   ├── deploy.sh     # Engine deployment script
│   │   │   ├── config/       # Engine configuration
│   │   │   │   └── engine-config.yml
│   │   │   └── k8s/          # Engine Kubernetes manifests
│   │   │       └── engine.yaml
│   │   ├── legend-sdlc/      # Legend SDLC Service
│   │   │   ├── sdlc.env      # SDLC-specific variables
│   │   │   ├── deploy.sh     # SDLC deployment script
│   │   │   └── k8s/          # SDLC Kubernetes manifests
│   │   │       └── sdlc.yaml
│   │   ├── legend-studio/    # Legend Studio Service
│   │   │   ├── studio.env    # Studio-specific variables
│   │   │   └── k8s/          # Studio Kubernetes manifests
│   │   │       └── studio.yaml
│   │   ├── legend-guardian/  # Guardian Agent Service
│   │   │   ├── guardian.env  # Guardian-specific variables
│   │   │   └── k8s/          # Guardian Kubernetes manifests
│   │   │       └── guardian.yaml
│   │   └── mongodb/          # MongoDB Service
│   │       ├── mongodb.env   # MongoDB-specific variables
│   │       └── k8s/          # MongoDB Kubernetes manifests
│   │           └── mongodb.yaml
│   ├── shared/               # Shared Kubernetes resources
│   │   ├── namespace.yaml    # Namespace and configmap
│   │   └── secrets.yaml      # Shared secrets
│   └── config/               # Global configuration files
│       ├── engine-config.yml # Legend Engine configuration
│       └── sdlc-config.yml   # Legend SDLC configuration
├── kubernetes/
│   ├── deploy-all.sh         # Kubernetes deployment orchestrator
├── validate.sh                # Platform-wide validation
├── validate-config.sh         # Configuration validation
├── setup-secrets.sh           # Secrets setup script
└── README.md                  # This documentation file
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

1. **`shared/base.env`** - Base configuration (shared by all environments)
   - Legend versions
   - Default ports and hosts
   - Common settings

2. **`shared/common.env`** - Common environment variables
   - Azure infrastructure settings
   - Kubernetes configuration
   - GitLab OAuth credentials
   - MongoDB connection

3. **`kubernetes/config/`** - Global configuration files
   - `engine-config.yml` - Legend Engine configuration
   - `sdlc-config.yml` - Legend SDLC configuration

4. **Service-specific .env files** - Override/extend common variables
   - `kubernetes/components/legend-engine/engine.env`
   - `kubernetes/components/legend-sdlc/sdlc.env`
   - `kubernetes/components/legend-studio/studio.env`
   - `kubernetes/components/legend-guardian/guardian.env`
   - `kubernetes/components/mongodb/mongodb.env`

5. **Service-specific config files** - Service configurations
   - `kubernetes/components/legend-engine/config/engine-config.yml`
   - `local/config/engine-config.yml` (local development)
   - `local/config/sdlc-config.yml` (local development)

### **Environment Variables and Secrets**

The deployment system automatically loads secrets in this order:
1. **`secrets.env`** - Your real production secrets (git-ignored)
2. **`.env.local`** - Alternative secrets file (git-ignored)
3. **`common.env`** - Safe placeholder values (committed to git)

This means:
- **Development**: Use `secrets.env` with real values
- **CI/CD**:. Use environment variables or secure secret management
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

## 🔍 Troubleshooting

### **Check Deployment Status**
```bash
# All services status
cd deploy
./deploy-all.sh status

# Individual service status
./kubernetes/components/legend-engine/deploy.sh status
./kubernetes/components/mongodb/deploy.sh status
```

### **Validate Deployments**
```bash
# Platform-wide validation
./validate.sh

# Service-specific validation
./kubernetes/components/legend-engine/deploy.sh validate
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
