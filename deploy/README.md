# Deployment Directory Structure

This directory contains all deployment configurations for FINOS Legend platform.

## Directory Structure

```
deploy/
├── docker-config-overrides/  # Docker configuration files
│   ├── engine-config.yml
│   └── sdlc-config.yml
│
├── docker-finos-official/   # Official FINOS Legend Docker setup
│   ├── docker-compose.yml  # Full official setup
│   └── setup.sh           # Official setup script
│
├── docker-local/            # Docker Compose for local development
│   ├── docker-compose.yml   # Simple local setup
│   └── start.sh             # Convenience startup script
│
├── k8s/                     # Kubernetes deployment (consolidated)
│   ├── base/               # Base resources
│   └── services/           # Service deployments
│
├── k8s-overrides/          # Environment-specific K8s customizations
│   └── production/         # Production overrides example
│
└── azure/                  # Azure-specific deployment scripts
    └── build-and-push-images.sh
```

## Quick Start

### Docker Local Development
```bash
cd deploy/docker-local
./start.sh              # Start basic Legend services
./start.sh full         # Include Guardian Agent
```

### Kubernetes
```bash
kubectl apply -k deploy/k8s/
```

### Official FINOS Docker Setup
```bash
cd deploy/docker-finos-official
./setup.sh              # Run official setup
./run-legend.sh studio  # Start Legend Studio
```

## Key Principles

1. **Use Official Images** - All deployments use official FINOS Docker images
2. **No Custom Builds** - No modifications to Legend services
3. **Clear Separation** - Different deployment methods clearly organized
4. **Environment Overrides** - Customizations in separate override directories

## Deployment Methods

- **docker-config-overrides/** - Configuration files for Docker deployments
- **docker-finos-official/** - Official FINOS provided Docker setup (unchanged)
- **docker-local/** - Simplified Docker Compose for quick local development
- **k8s/** - Production-ready Kubernetes manifests
- **k8s-overrides/** - Environment-specific Kubernetes customizations