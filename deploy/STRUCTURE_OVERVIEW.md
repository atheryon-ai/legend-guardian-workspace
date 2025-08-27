# Deployment Structure Overview

## 🏗️ Restructured Organization

The deployment directory has been reorganized to follow a consistent **endpoint → component** convention for better maintainability and clarity.

## 📁 New Directory Structure

```
deploy/
├── shared/                    # Shared across all endpoints
│   ├── base.env              # Base configuration (shared by all environments)
│   ├── common.env            # Common environment variables
│   └── lib/                  # Shared bash functions library
│       └── common-functions.sh
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
│   ├── config/               # Global configuration files
│   │   ├── engine-config.yml # Legend Engine configuration
│   │   └── sdlc-config.yml   # Legend SDLC configuration
│   └── deploy-all.sh         # Kubernetes deployment orchestrator
├── deploy.sh                  # Master deployment script (endpoint selector)
├── validate.sh                # Platform-wide validation
├── validate-config.sh         # Configuration validation
├── setup-secrets.sh           # Secrets setup script
└── README.md                  # Main deployment documentation
```

## 🔄 Migration Summary

### What Was Moved

| From | To | Reason |
|------|----|---------|
| `legend-engine/` | `kubernetes/components/legend-engine/` | Component under K8s endpoint |
| `legend-sdlc/` | `kubernetes/components/legend-sdlc/` | Component under K8s endpoint |
| `legend-studio/` | `kubernetes/components/legend-studio/` | Component under K8s endpoint |
| `legend-guardian/` | `kubernetes/components/legend-guardian/` | Component under K8s endpoint |
| `mongodb/` | `kubernetes/components/mongodb/` | Component under K8s endpoint |
| `k8s/` | `kubernetes/shared/` | Shared K8s resources |
| `config/` | `kubernetes/config/` | K8s-specific configs |
| `lib/` | `shared/lib/` | Shared across all endpoints |
| `base.env` | `shared/base.env` | Shared across all endpoints |
| `common.env` | `shared/common.env` | Shared across all endpoints |

### What Was Restructured

| Docker Files | New Location | Reason |
|--------------|--------------|---------|
| `Dockerfile.engine` | `docker/components/engine/` | Component organization |
| `Dockerfile.sdlc` | `docker/components/sdlc/` | Component organization |
| `Dockerfile.studio` | `docker/components/studio/` | Component organization |
| `Dockerfile` | `docker/components/guardian/` | Component organization |

## 🎯 Benefits of New Structure

### 1. **Clear Separation of Concerns**
- **Endpoints**: Different deployment targets (Azure, Docker, Kubernetes)
- **Components**: Reusable services across endpoints
- **Shared**: Common configuration and functions

### 2. **Easier Maintenance**
- All Azure-specific files in one place
- All Docker-specific files in one place
- All Kubernetes-specific files in one place

### 3. **Better Scalability**
- Easy to add new endpoints (e.g., `aws/`, `gcp/`)
- Easy to add new components (e.g., `monitoring/`, `logging/`)
- Consistent structure across all endpoints

### 4. **Improved Developer Experience**
- Clear where to find specific functionality
- Consistent naming conventions
- Logical grouping of related files

## 🚀 Usage Examples

### Deploy to Kubernetes
```bash
cd deploy
./deploy-all.sh deploy
```

### Deploy Individual K8s Component
```bash
cd deploy
./kubernetes/components/legend-engine/deploy.sh deploy
```

### Run Docker Environment
```bash
cd deploy/docker
docker-compose up -d
```

### Deploy to Azure
```bash
cd deploy/azure
./deploy-azure.bash
```

## 📝 Updated File References

### Configuration Loading
- **Base config**: `shared/base.env`
- **Common config**: `shared/common.env`
- **Functions**: `shared/lib/common-functions.sh`

### Service Deployment
- **Engine**: `kubernetes/components/legend-engine/deploy.sh`
- **SDLC**: `kubernetes/components/legend-sdlc/deploy.sh`
- **Studio**: `kubernetes/components/legend-studio/deploy.sh`
- **Guardian**: `kubernetes/components/legend-guardian/deploy.sh`
- **MongoDB**: `kubernetes/components/mongodb/deploy.sh`

### Docker Builds
- **Guardian**: `deploy/docker/components/guardian/Dockerfile`
- **Engine**: `deploy/docker/components/engine/Dockerfile.engine`
- **SDLC**: `deploy/docker/components/sdlc/Dockerfile.sdlc`
- **Studio**: `deploy/docker/components/studio/Dockerfile.studio`

## 🔧 Script Updates Required

The following scripts have been updated to use the new paths:

- ✅ `deploy/deploy-all.sh` - Updated source paths
- ✅ `deploy/kubernetes/components/*/deploy.sh` - Updated source paths
- ✅ `Makefile` - Updated Docker build paths
- ✅ `deploy/docker/docker-compose*.yml` - Updated Dockerfile paths

## 📚 Related Documentation

- [Main Deployment Guide](README.md)
- [Docker Setup](docker/README_DOCKER.md)
- [Azure Deployment](azure/README.md)
- [Configuration Validation](validate-config.sh)
