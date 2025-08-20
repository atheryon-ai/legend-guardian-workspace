# Legend Platform Deployment Guide

## Overview

This deployment system provides a modular, environment-specific configuration approach for deploying the Legend platform to various targets (local, Azure, Kubernetes).

## Configuration Structure

The deployment configuration follows a hierarchical structure:

```
deploy/
├── base.env                 # Base configuration (shared by all environments)
├── lib/
│   └── common-functions.sh  # Shared bash functions library
├── azure/
│   └── azure.env            # Azure-specific overrides
├── local/
│   └── local.env            # Local development overrides
└── secrets.env              # Your actual secrets (created from secrets.example)
```

### Configuration Hierarchy

1. **base.env** - Contains all default configuration values
2. **Environment-specific files** (azure.env, local.env) - Override base values as needed
3. **secrets.env** - Contains actual secrets (API keys, passwords, etc.)

Configuration is loaded in this order, with later values overriding earlier ones.

## Quick Start

### 1. Set Up Secrets

```bash
# Copy the template
cp ../secrets.example ../secrets.env

# Edit with your actual values
nano ../secrets.env
```

### 2. Validate Configuration

```bash
# Check all configuration
./validate-config.sh all

# Check specific environment
./validate-config.sh azure
./validate-config.sh local
```

### 3. Deploy

#### Local Development
```bash
cd local
./start.sh
```

#### Azure Deployment
```bash
cd azure
./deploy-azure.bash
```

#### Kubernetes Deployment
```bash
./deploy-all.sh deploy
```

## Configuration Files

### base.env
Contains default values for all deployments:
- Legend service versions
- Default ports and hosts
- Resource limits
- Common settings

### azure/azure.env
Azure-specific overrides:
- Azure subscription and resource group
- AKS configuration
- Azure Container Registry settings
- Production URLs
- Azure-specific resource limits

### local/local.env
Local development overrides:
- Local service URLs
- Docker Compose settings
- Development-friendly resource limits
- Debug settings

### secrets.env
Your actual secrets (never commit this file):
- Azure credentials
- GitLab OAuth credentials
- API keys
- Passwords

## Deployment Scripts

### Master Deployment Script
```bash
./deploy-all.sh [command]
```
Commands:
- `deploy` - Deploy all services
- `validate` - Validate deployments
- `status` - Show current status
- `clean` - Remove deployments
- `menu` - Interactive menu (default)

### Configuration Validation
```bash
./validate-config.sh [command]
```
Commands:
- `all` - Validate all configurations
- `base` - Validate base configuration
- `azure` - Validate Azure configuration
- `local` - Validate local configuration
- `secrets` - Check secrets file
- `structure` - Check file structure
- `menu` - Interactive menu (default)

### Azure Deployment
```bash
cd azure
./deploy-azure.bash        # Deploy Azure infrastructure
./build-and-push-images.sh # Build and push Docker images
./process-k8s-manifests.sh # Process Kubernetes manifests
```

### Local Development
```bash
cd local
./start.sh [all|core|guardian]
```
Options:
- `all` - Start all services including Guardian
- `core` - Start only core Legend services
- `guardian` - Start only Guardian agent

## Common Functions Library

The `lib/common-functions.sh` file provides reusable functions:

- **Output functions**: `print_status`, `print_error`, `print_warning`, `print_success`
- **Configuration loading**: `load_base_config`, `load_env_config`, `load_secrets`
- **Validation**: `validate_required_vars`, `is_placeholder`
- **Prerequisites**: `check_kubectl`, `check_docker`, `check_azure_cli`
- **Kubernetes helpers**: `create_namespace`, `wait_for_deployment`
- **Port checking**: `check_port_available`, `check_ports_available`

## Environment Variables

### Required for All Deployments
- `LEGEND_ENGINE_VERSION` - Legend Engine version
- `LEGEND_SDLC_VERSION` - Legend SDLC version
- `LEGEND_STUDIO_VERSION` - Legend Studio version
- `K8S_NAMESPACE` - Kubernetes namespace
- `MONGODB_NAME` - MongoDB database name

### Required for Azure
- `AZURE_SUBSCRIPTION_ID` - Azure subscription ID
- `AZURE_RESOURCE_GROUP` - Resource group name
- `AZURE_ACR_USERNAME` - ACR username
- `AZURE_ACR_PASSWORD` - ACR password
- `GITLAB_APP_ID` - GitLab OAuth app ID
- `GITLAB_APP_SECRET` - GitLab OAuth app secret

### Required for Local
- `LEGEND_ENGINE_PORT` - Engine port (default: 6300)
- `LEGEND_SDLC_PORT` - SDLC port (default: 6100)
- `LEGEND_STUDIO_PORT` - Studio port (default: 9000)

## Troubleshooting

### Configuration Issues
```bash
# Check what values are being loaded
./validate-config.sh show-azure
./validate-config.sh show-local

# Validate specific environment
./validate-config.sh azure
```

### Missing Secrets
```bash
# Check if secrets file exists and is properly configured
./validate-config.sh secrets

# Create from template if missing
cp ../secrets.example ../secrets.env
```

### Port Conflicts (Local)
```bash
# Check which ports are in use
lsof -i :6300
lsof -i :6100
lsof -i :9000
```

### Kubernetes Issues
```bash
# Check cluster connection
kubectl cluster-info

# Check namespace
kubectl get namespace legend

# Check pods
kubectl get pods -n legend
```

## Best Practices

1. **Never commit secrets.env** - It's already in .gitignore
2. **Use validate-config.sh** before deploying
3. **Keep environment-specific files minimal** - Only override what's necessary
4. **Use placeholder detection** - The system warns about placeholder values
5. **Test locally first** - Use local deployment before Azure/K8s
6. **Document changes** - Update this guide when adding new configuration

## Adding New Configuration

1. Add default value to `base.env`
2. Add environment-specific overrides if needed
3. Update validation in `validate-config.sh`
4. Document in this guide

## Support

For issues or questions:
1. Run validation: `./validate-config.sh all`
2. Check logs: `kubectl logs -n legend <pod-name>`
3. Review this guide
4. Check deployment script output for specific errors