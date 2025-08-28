# Atheryon FINOS Legend Documentation

This project provides a clean, focused deployment of the FINOS Legend platform using official Docker images.

## 📚 Documentation Overview

- [Architecture](architecture.md) - System architecture and design
- [Docker Deployment](../deploy/docker-finos-official/README_DOCKER.md) - Official FINOS Docker deployment
- [Deployment Guide](../deploy/DEPLOYMENT_GUIDE.md) - Overview of all deployment methods
- [Secrets Management](../deploy/secrets/README.md) - GitLab OAuth and secrets configuration

## 🎯 Project Focus

This project uses **100% official FINOS Legend components**:
- **Legend Engine** (port 6300) - Model execution engine
- **Legend SDLC** (port 6100) - Source control and lifecycle management
- **Legend Studio** (port 9000) - Web-based modeling interface
- **Legend Depot** (port 6200) - Model repository and sharing
- **Legend Query** (port 9001) - Data exploration interface
- **MongoDB** (port 27017) - Primary database backend
- **PostgreSQL** (port 5432) - Additional database support

## 🚀 Quick Start

```bash
# 1. Configure secrets (GitLab OAuth required)
./deploy/secrets/setup.sh --env local --interactive

# 2. Run one-time setup
cd deploy/docker-finos-official
./run-legend.sh setup up

# 3. Launch Legend Studio stack
./run-legend.sh studio up -d

# 4. Access Legend Studio
open http://localhost:9000/studio
```

## 🐳 Deployment Options

### Docker Compose (Recommended for Development)
- **Location**: `deploy/docker-finos-official/`
- **Script**: `run-legend.sh` - Main deployment script
- **Profiles**: setup, engine, sdlc, studio, depot, query, postgres
- **Documentation**: [Docker README](../deploy/docker-finos-official/README_DOCKER.md)

### Kubernetes/Azure
- **Location**: `deploy/k8s-azure/`
- **Script**: `deploy.sh` - Azure AKS deployment
- **Documentation**: [Kubernetes README](../deploy/k8s/README.md)

## 📖 Additional Resources

- [FINOS Legend](https://github.com/finos/legend) - Official Legend platform
- [Legend Documentation](https://legend.finos.org/) - Official documentation
- [Official Docker Compose](https://github.com/finos/legend/tree/master/installers/docker-compose) - FINOS reference implementation
