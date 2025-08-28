# Deployment History - Azure Legend Platform

**NOTE: This documentation is historical and represents a previous Azure deployment approach. The current project focuses on Docker-based deployments using the official FINOS Legend Docker Compose setup.**

---

## Historical Azure Deployment Documentation

This directory previously contained the complete Azure deployment configuration for the FINOS Legend platform, using a centralized environment variable system for configuration management.

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Copy the example environment file
cp azure-legend.env.example azure-legend.env

# Edit the environment file with your values
nano azure-legend.env
```

### 2. Deploy Infrastructure
```bash
# Deploy Azure infrastructure (AKS, ACR, MongoDB)
./deploy-azure.bash
```

### 3. Build and Push Images
```bash
# Build and push Legend images to Azure Container Registry
./build-and-push-images.sh
```

### 4. Deploy Legend Platform
```bash
# Deploy Legend to Azure AKS
./deploy-legend.sh
```

## 🔧 Environment Configuration

### Environment File Structure

The `azure-legend.env` file contains all configuration parameters organized by category:

#### Azure Infrastructure Configuration
```bash
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group-name
AZURE_LOCATION=eastus
AZURE_AKS_CLUSTER=your-aks-cluster-name
AZURE_ACR_NAME=your-acr-name
AZURE_ACR_LOGIN_SERVER=your-acr-name.azurecr.io
```

#### Legend Service Configuration
```bash
LEGEND_ENGINE_URL=https://legend-engine.your-domain.com
LEGEND_SDLC_URL=https://legend-sdlc.your-domain.com
LEGEND_STUDIO_URL=https://legend-studio.your-domain.com
LEGEND_ENGINE_PORT=6300
LEGEND_SDLC_PORT=6100
LEGEND_STUDIO_PORT=9000
```

#### MongoDB Configuration
```bash
MONGODB_URI=mongodb://admin:[PASSWORD]@mongo-legend-[UNIQUE_SUFFIX].mongo.cosmos.azure.com:10255/legend?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@mongo-legend-[UNIQUE_SUFFIX]@
MONGODB_NAME=legend
MONGODB_SESSION_ENABLED=false
```

#### GitLab OAuth Configuration
```bash
GITLAB_APP_ID=your-gitlab-app-id
GITLAB_APP_SECRET=your-gitlab-app-secret
GITLAB_HOST=gitlab.com
```

#### Kubernetes Configuration
```bash
K8S_NAMESPACE=legend
AKS_NODE_COUNT=2
AKS_VM_SIZE=Standard_DS2_v2
AKS_KUBERNETES_VERSION=1.28.0
```

#### Legend Versions
```bash
LEGEND_ENGINE_VERSION=4.40.3
LEGEND_SDLC_VERSION=0.195.0
LEGEND_STUDIO_VERSION=13.113.0
```

#### Resource Limits
```bash
ENGINE_MEMORY_REQUEST=512Mi
ENGINE_MEMORY_LIMIT=1Gi
ENGINE_CPU_REQUEST=250m
ENGINE_CPU_LIMIT=500m
```

## 📁 File Structure

```
azure-deployment/
├── azure-legend.env              # Main environment configuration
├── azure-legend.env.example      # Example environment file
├── deploy-azure.bash            # Azure infrastructure deployment
├── deploy-legend.sh             # Legend platform deployment
├── build-and-push-images.sh     # Image build and push
├── process-k8s-manifests.sh     # Process K8s manifests with env vars
├── azure-resources.bicep        # Azure infrastructure template
├── k8s/                         # Kubernetes manifests
│   ├── legend-namespace.yaml    # Namespace and config
│   ├── legend-secrets.yaml      # Secrets (OAuth, etc.)
│   ├── legend-engine.yaml       # Legend Engine deployment
│   ├── legend-sdlc.yaml         # Legend SDLC deployment
│   └── legend-studio.yaml       # Legend Studio deployment
└── k8s/processed/               # Processed manifests (auto-generated)
```

## 🔄 Environment Variable Processing

### Kubernetes Manifests

All Kubernetes manifests now use environment variable placeholders (e.g., `${K8S_NAMESPACE}`) that get processed by the `process-k8s-manifests.sh` script.

**Before processing:**
```yaml
metadata:
  name: legend-engine
  namespace: ${K8S_NAMESPACE}
spec:
  containers:
  - name: legend-engine
    image: finos/legend-engine-server:${LEGEND_ENGINE_VERSION}
    ports:
    - containerPort: ${LEGEND_ENGINE_PORT}
```

**After processing:**
```yaml
metadata:
  name: legend-engine
  namespace: legend
spec:
  containers:
  - name: legend-engine
    image: finos/legend-engine-server:4.40.3
    ports:
    - containerPort: 6300
```

### Processing Script

The `process-k8s-manifests.sh` script:
1. Loads environment variables from `azure-legend.env`
2. Creates processed manifests in `k8s/processed/`
3. Replaces all placeholders with actual values
4. Base64 encodes secrets automatically

## 🚀 Deployment Workflow

### 1. Infrastructure Deployment
```bash
./deploy-azure.bash
```
- Creates Azure resource group
- Deploys AKS cluster with configurable parameters
- Sets up Azure Container Registry
- Configures networking and security

### 2. Image Management
```bash
./build-and-push-images.sh
```
- Builds Legend images with versioned tags
- Pushes images to Azure Container Registry
- Uses environment variables for versions

### 3. Platform Deployment
```bash
./deploy-legend.sh
```
- Processes Kubernetes manifests
- Deploys to Azure AKS
- Configures services and networking
- Waits for deployment readiness

## 🔒 Security Features

### Secrets Management
- GitLab OAuth credentials stored as Kubernetes secrets
- Automatic base64 encoding during manifest processing
- Environment-specific secret configuration

### Network Security
- Azure network policies enabled
- Service mesh integration ready
- TLS configuration support

## 📊 Monitoring and Management

### Health Checks
```bash
# Check deployment status
kubectl get all -n $K8S_NAMESPACE

# View service endpoints
kubectl get svc -n $K8S_NAMESPACE

# Check pod status
kubectl get pods -n $K8S_NAMESPACE
```

### Logs and Debugging
```bash
# View engine logs
kubectl logs -l app=legend-engine -n $K8S_NAMESPACE

# Port forward for local access
kubectl port-forward svc/legend-studio $LEGEND_STUDIO_PORT:$LEGEND_STUDIO_PORT -n $K8S_NAMESPACE
```

## 🔧 Customization

### Adding New Environment Variables

1. **Add to `.env` file:**
```bash
# New configuration
NEW_SETTING=value
```

2. **Update Kubernetes manifests:**
```yaml
metadata:
  name: service-name
  annotations:
    custom.annotation: ${NEW_SETTING}
```

3. **Update processing script:**
```bash
# In process-k8s-manifests.sh
sed -i "s/\${NEW_SETTING}/$NEW_SETTING/g" "$output_file"
```

### Environment-Specific Configurations

Create multiple environment files for different environments:

```bash
# Development
cp azure-legend.env.example azure-legend.dev.env

# Staging
cp azure-legend.env.example azure-legend.staging.env

# Production
cp azure-legend.env.example azure-legend.prod.env
```

## 🚨 Troubleshooting

### Common Issues

1. **Environment file not found:**
   - Ensure `azure-legend.env` exists
   - Copy from `azure-legend.env.example`

2. **Manifest processing errors:**
   - Check environment variable values
   - Verify placeholder syntax `${VARIABLE_NAME}`

3. **Deployment failures:**
   - Check AKS cluster status
   - Verify image availability in ACR
   - Check namespace and resource quotas

### Debug Commands

```bash
# Check environment variables
source azure-legend.env && env | grep LEGEND

# Test manifest processing
./process-k8s-manifests.sh

# Verify processed manifests
diff k8s/legend-engine.yaml k8s/processed/legend-engine.yaml
```

## 📚 Additional Resources

- [Azure Bicep Documentation](https://docs.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
- [AKS Best Practices](https://docs.microsoft.com/en-us/azure/aks/best-practices)
- [FINOS Legend Documentation](https://legend.finos.org/)
- [Kubernetes Manifest Reference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.28/)

## 🤝 Contributing

When adding new configuration parameters:

1. **Add to environment file** with clear documentation
2. **Update example file** with placeholder values
3. **Update processing script** for Kubernetes manifests
4. **Add to documentation** with examples
5. **Test across environments** to ensure compatibility

---

**Note**: This deployment system centralizes all configuration in environment variables, eliminating duplication and making it easy to manage multiple environments. Always use the `.env` file for configuration changes rather than editing scripts directly.