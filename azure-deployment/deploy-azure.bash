#!/bin/bash

# Azure Legend Platform Deployment Script
# This script deploys the Azure infrastructure and then uses FINOS Legend's 
# production-ready Kubernetes manifests for the actual Legend deployment.

set -e

# Configuration
SUBSCRIPTION_ID="34b8f36d-a89f-4848-8249-c4175ce5533e"
RESOURCE_GROUP="rs-finos-legend"
LOCATION="eastus"
BICEP_FILE="azure-resources.bicep"
PARAMETERS_FILE="azure-parameters.json"

echo "🚀 Starting Azure Legend Platform Deployment"
echo "=============================================="
echo "Subscription ID: $SUBSCRIPTION_ID"
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install it first:"
    echo "   https://kubernetes.io/docs/tasks/tools/install-kubectl/"
    exit 1
fi

# Login to Azure
echo "🔐 Logging into Azure..."
az login

# Set subscription
echo "📋 Setting subscription to $SUBSCRIPTION_ID..."
az account set --subscription $SUBSCRIPTION_ID

# Create resource group
echo "🏗️  Creating resource group $RESOURCE_GROUP..."
az group create --name $RESOURCE_GROUP --location "$LOCATION"

# Generate MongoDB password
MONGO_PASSWORD=$(openssl rand -base64 32)
echo "🔑 Generated MongoDB password"

# Deploy Azure infrastructure
echo "🚀 Deploying Azure infrastructure..."
az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --template-file $BICEP_FILE \
    --parameters mongoAdminPassword="$MONGO_PASSWORD"

# Get deployment outputs
echo "📊 Getting deployment outputs..."
ACR_LOGIN_SERVER=$(az deployment group show \
    --resource-group $RESOURCE_GROUP \
    --name $BICEP_FILE \
    --query properties.outputs.acrLoginServer.value \
    --output tsv)

ACR_NAME=$(az deployment group show \
    --resource-group $RESOURCE_GROUP \
    --name $BICEP_FILE \
    --query properties.outputs.acrName.value \
    --output tsv)

AKS_CLUSTER_NAME=$(az deployment group show \
    --resource-group $RESOURCE_GROUP \
    --name $BICEP_FILE \
    --query properties.outputs.aksClusterName.value \
    --output tsv)

MONGO_CONNECTION_STRING=$(az deployment group show \
    --resource-group $RESOURCE_GROUP \
    --name $BICEP_FILE \
    --query properties.outputs.mongoConnectionString.value \
    --output tsv)

echo "✅ Azure infrastructure deployed successfully!"
echo ""

# Get AKS credentials
echo "🔑 Getting AKS credentials..."
az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER_NAME --overwrite-existing

# Verify cluster connection
echo "🔍 Verifying cluster connection..."
kubectl cluster-info

echo ""
echo "🎉 Azure infrastructure deployment complete!"
echo "=============================================="
echo "Resource Group: $RESOURCE_GROUP"
echo "AKS Cluster: $AKS_CLUSTER_NAME"
echo "ACR: $ACR_NAME"
echo "ACR Login Server: $ACR_LOGIN_SERVER"
echo ""
echo "📝 Next steps:"
echo "1. Update your GitLab OAuth app redirect URI to point to Azure"
echo "2. Build and push Legend images to ACR"
echo "3. Deploy Legend using FINOS Kubernetes manifests"
echo ""
echo "🔐 MongoDB password: $MONGO_PASSWORD"
echo "💾 Save this password securely - you'll need it for Legend configuration"
echo ""
echo "📚 For Legend deployment, use the FINOS provided manifests:"
echo "   https://legend.finos.org/docs/deployment/kubernetes"
echo ""
echo "🚀 Ready to deploy Legend to Azure!"
