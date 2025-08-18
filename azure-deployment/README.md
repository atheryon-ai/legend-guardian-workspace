# Azure Deployment Scripts

This directory contains scripts for deploying Legend FINOS to Azure.

## Scripts

- `quick-start.sh` - One-command complete deployment
- `deploy-simple.sh` - Infrastructure setup (AKS, ACR, networking)
- `add-mongodb.sh` - MongoDB deployment in AKS
- `build-and-push-images.sh` - Docker image management
- `deploy-legend.sh` - Application deployment to Kubernetes
- `azure-resources.bicep` - Infrastructure as Code template

## Configuration

- `azure-legend.env` - Environment variables
- `Dockerfile.*` - Optimized Legend images

## Usage

See [DEPLOYMENT.md](../DEPLOYMENT.md) for complete instructions.

## Key Resources

After deployment:
- Resource Group: `rs-finos-legend`
- AKS Cluster: `aks-legend`
- MongoDB: Deployed in cluster namespace `legend`

## Support Files

- `LESSONS_LEARNED.md` - Deployment experience and solutions
- `FINOS_COMPARISON_ANALYSIS.md` - FINOS requirements analysis
- `JUJU_DEPLOYMENT_ANALYSIS.md` - Juju operators vs. manual deployment