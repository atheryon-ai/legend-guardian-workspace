# Kubernetes Customizations/Overrides

This directory contains environment-specific customizations and overrides for the base Kubernetes deployment.

## Structure

```
k8s-overrides/
├── README.md              # This file
├── production/           # Production-specific overrides
│   ├── kustomization.yaml
│   ├── resources.yaml    # Higher resource limits
│   └── ingress.yaml      # Production ingress rules
├── development/          # Development-specific overrides
│   ├── kustomization.yaml
│   └── resources.yaml    # Lower resource limits
└── azure/               # Azure AKS-specific overrides
    ├── kustomization.yaml
    └── storage.yaml      # Azure storage classes
```

## Usage

Use Kustomize to apply overrides on top of the base configuration:

```bash
# Apply production overrides
kubectl apply -k deploy/k8s-overrides/production/

# Apply development overrides
kubectl apply -k deploy/k8s-overrides/development/

# Apply Azure-specific overrides
kubectl apply -k deploy/k8s-overrides/azure/
```

## Creating New Overrides

1. Create a new directory for your environment
2. Add a `kustomization.yaml` that references the base:
   ```yaml
   bases:
     - ../../k8s-consolidated/
   ```
3. Add your patches, configMapGenerator, or other overrides
4. Apply with `kubectl apply -k deploy/k8s-overrides/your-env/`

## Important Notes

- **Never modify the base configuration** in `k8s-consolidated/`
- All customizations should be done through Kustomize overlays
- Keep secrets in separate Secret manifests (not in Git)