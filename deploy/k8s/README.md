# Kubernetes Deployment for FINOS Legend

This directory contains the consolidated Kubernetes deployment configuration for the FINOS Legend platform.

## Structure

```
k8s-consolidated/
├── README.md           # This file
├── base/              # Base K8s resources (namespace, RBAC, etc.)
├── services/          # Service deployments using official FINOS images
│   ├── mongodb/       # MongoDB database
│   ├── legend-engine/ # Legend Engine service
│   ├── legend-sdlc/   # Legend SDLC service
│   └── legend-studio/ # Legend Studio UI
└── kustomization.yaml # Kustomize configuration
```

## Deployment Approach

**Using Official FINOS Images Only:**
- All Legend services use official Docker images from Docker Hub
- No custom builds or modifications
- Configuration via ConfigMaps and environment variables

## Quick Start

```bash
# Deploy everything
kubectl apply -k deploy/k8s-consolidated/

# Or deploy individual components
kubectl apply -f deploy/k8s-consolidated/base/
kubectl apply -f deploy/k8s-consolidated/services/mongodb/
kubectl apply -f deploy/k8s-consolidated/services/legend-engine/
# etc...
```

## Customization

Any environment-specific customizations should go in `deploy/k8s-overrides/`

## Official Images Used

- `finos/legend-engine-server:4.40.3`
- `finos/legend-sdlc-server:0.195.0`
- `finos/legend-studio:13.113.0`
- `mongo:7.0` (for MongoDB)

## Notes

This deployment uses standard Kubernetes manifests compatible with any K8s cluster.
For OpenShift-specific deployments, consider using the official FINOS Helm charts at:
https://github.com/finos/legend/tree/master/installers/helm-ocp