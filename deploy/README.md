# Deployment Directory Structure

This directory contains all deployment configurations for the FINOS Legend platform, with a focus on a standardized Kubernetes deployment strategy using Kustomize.

## Kubernetes Deployment Strategy: Kustomize

The primary method for managing Kubernetes deployments is **Kustomize**. This approach allows for a clean separation between base configuration and environment-specific overrides, eliminating duplication and improving maintainability.

*   **Base (`deploy/k8s/`):** Contains the standard, environment-agnostic Kubernetes manifests for all Legend services.
*   **Overlays (`deploy/k8s-overrides/`):** Contains environment-specific customizations. Each subdirectory is a Kustomize overlay for an environment (e.g., `production`, `development`) that modifies the base configuration.

## Directory Structure

```
deploy/
├── k8s/                     # Kustomize BASE: Generic Kubernetes manifests.
│   ├── base/
│   └── services/
│
├── k8s-overrides/           # Kustomize OVERLAYS: Environment-specific customizations.
│   └── production/          # Example for the 'production' environment.
│       ├── kustomization.yaml
│       └── *.patch.yaml
│
├── k8s-azure/               # Automation scripts for deploying to Azure AKS.
│   └── deploy.sh            # Deploys a Kustomize overlay to AKS.
│
├── docker-local/            # Simple Docker Compose for local development.
│
└── docker-finos-official/   # Official FINOS Legend Docker setup for evaluation.
```

## Quick Start

### Kubernetes Deployment (via Kustomize)

To deploy a specific environment to your currently configured Kubernetes cluster, use `kubectl apply -k` and point it to the overlay directory.

```bash
# Deploy the 'production' environment configuration
kubectl apply -k deploy/k8s-overrides/production/

# Deploy the 'development' environment configuration
kubectl apply -k deploy/k8s-overrides/development/
```

### Azure AKS Deployment

The scripts in the Azure directory automate the process of setting up an AKS cluster and deploying a Kustomize overlay.

```bash
cd deploy/k8s-azure
# This script should handle cluster setup and apply a Kustomize overlay
./deploy.sh production
```

### Local Development (Docker)

For quick local development, a simple Docker Compose setup is provided.

```bash
cd deploy/docker-local
./start.sh
```

## Key Principles

1.  **Kustomize is Standard:** All Kubernetes deployments MUST use the base/overlay structure.
2.  **Use Official Images:** All deployments use official FINOS Docker images.
3.  **No Custom Builds:** No modifications to Legend services.
4.  **Clear Separation:** Base configuration (`k8s`) is kept separate from environment-specific changes (`k8s-overrides`).

## Deployment Methods

- **k8s/**: Contains the Kustomize `base` manifests. **Do not modify** these for a specific environment.
- **k8s-overrides/**: Contains Kustomize `overlays`. Add a new directory here to define a new environment. All environment-specific changes (resource limits, domains, image tags) belong here.
- **k8s-azure/**: Provides automation for Azure. Scripts in this directory orchestrate the deployment of a Kustomize overlay to AKS.
- **docker-local/**: Simplified Docker Compose for quick local development.
- **docker-finos-official/**: The official, unmodified Docker setup from FINOS for local evaluation.
