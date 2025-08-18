#!/bin/bash

# Simple Azure Legend Platform Deployment Script
# Uses Azure CLI commands directly instead of Bicep templates

set -e

# Configuration
SUBSCRIPTION_ID="34b8f36d-a89f-4848-8249-c4175ce5533e"
RESOURCE_GROUP="rs-finos-legend"
LOCATION="eastus"
AKS_CLUSTER_NAME="aks-legend"
ACR_NAME="acrlegend$(openssl rand -hex 4)"

echo "🚀 Starting Simple Azure Legend Platform Deployment"
echo "=================================================="
echo "Subscription ID: $SUBSCRIPTION_ID"
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "AKS Cluster: $AKS_CLUSTER_NAME"
echo "ACR: $ACR_NAME"
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

# Set subscription
echo "📋 Setting subscription to $SUBSCRIPTION_ID..."
az account set --subscription $SUBSCRIPTION_ID

# Create resource group
echo "🏗️  Creating resource group $RESOURCE_GROUP..."
az group create --name $RESOURCE_GROUP --location "$LOCATION"

# Create Azure Container Registry
echo "🐳 Creating Azure Container Registry $ACR_NAME..."
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer --output tsv)
echo "✅ ACR created: $ACR_LOGIN_SERVER"

# Create AKS cluster with available VM size
echo "🚀 Creating AKS cluster $AKS_CLUSTER_NAME..."
az aks create \
    --resource-group $RESOURCE_GROUP \
    --name $AKS_CLUSTER_NAME \
    --node-count 2 \
    --node-vm-size Standard_D2_v3 \
    --enable-addons monitoring \
    --generate-ssh-keys \
    --location "$LOCATION"

echo "✅ AKS cluster created successfully!"

# Get AKS credentials
echo "🔑 Getting AKS credentials..."
az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER_NAME --overwrite-existing

# Verify cluster connection
echo "🔍 Verifying cluster connection..."
kubectl cluster-info

# Assign ACR pull role to AKS
echo "🔐 Assigning ACR pull role to AKS..."
AKS_PRINCIPAL_ID=$(az aks show --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER_NAME --query identity.principalId --output tsv)
ACR_ID=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query id --output tsv)

az role assignment create \
    --assignee $AKS_PRINCIPAL_ID \
    --role AcrPull \
    --scope $ACR_ID

echo "✅ Role assignment completed!"

echo ""
echo "🎉 Azure infrastructure deployment complete!"
echo "=========================================="
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
echo "📚 For Legend deployment, use the FINOS provided manifests:"
echo "   https://legend.finos.org/docs/deployment/kubernetes"
echo ""
echo "🚀 Ready to deploy Legend to Azure!"
