# Azure Kubernetes Deployment for Legend

This directory provides scripts to automate the deployment of the Legend platform to Azure Kubernetes Service (AKS) using the project's standard Kustomize configuration.

## Deployment Strategy

The deployment scripts in this directory are wrappers around `kubectl` and `az`. They are designed to:

1.  Provision or configure an AKS cluster and its dependencies.
2.  Deploy the Legend platform by applying a Kustomize overlay from the `deploy/k8s-overrides/` directory.

This ensures that deployments to Azure are consistent with the project's standard Kubernetes configuration.

## 🚀 Quick Start

To deploy a specific environment configuration to AKS, use the main deployment script.

```bash
# Ensure you are logged into Azure CLI
az login

# Deploy the 'production' overlay to AKS
./deploy.sh production

# Deploy the 'development' overlay to AKS
./deploy.sh development
```

## Configuration

### Azure Configuration

Azure-specific parameters (like resource group, cluster name, VM size) should be configured within the `deploy.sh` script or an associated configuration file.

### Kubernetes Configuration

All Kubernetes manifest configurations, including resource limits, image tags, and domain names, are managed by Kustomize.

- **Base Manifests:** `deploy/k8s/`
- **Environment Overlays:** `deploy/k8s-overrides/`

To customize the Azure deployment, modify the appropriate overlay in the `k8s-overrides` directory. The `deploy.sh` script simply applies the chosen overlay.

## Deployment Process

The `deploy.sh` script should perform the following actions:

1.  **Select Environment:** Takes an environment name (e.g., `production`) as an argument.
2.  **Setup Infrastructure (Optional):** Creates or configures the AKS cluster and necessary resources like resource groups.
3.  **Get Credentials:** Connects `kubectl` to the target AKS cluster.
4.  **Apply Kustomize Overlay:** Executes `kubectl apply -k ../k8s-overrides/<environment>` to deploy Legend.
5.  **Validate:** Performs post-deployment checks to ensure services are running correctly.

For detailed status checks and troubleshooting, please use `kubectl` commands directly.

```bash
# Check pod status in the 'legend' namespace
kubectl get pods -n legend

# View logs for the Legend Engine
kubectl logs -f deployment/legend-engine -n legend
```
