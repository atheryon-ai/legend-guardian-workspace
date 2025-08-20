#!/bin/bash

# Azure Legend Platform Deployment Script
# This script deploys the Azure infrastructure and then uses FINOS Legend's 
# production-ready Kubernetes manifests for the actual Legend deployment.

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source common functions library
source "$SCRIPT_DIR/../lib/common-functions.sh"

# Load all configuration for Azure deployment
load_all_config "azure"

# Validate required Azure variables
REQUIRED_VARS=(
    "AZURE_SUBSCRIPTION_ID"
    "AZURE_RESOURCE_GROUP"
    "AZURE_LOCATION"
    "AKS_NODE_COUNT"
    "AKS_VM_SIZE"
    "AKS_MIN_NODES"
    "AKS_MAX_NODES"
    "AKS_KUBERNETES_VERSION"
    "AKS_SERVICE_CIDR"
    "AKS_DNS_SERVICE_IP"
)

if ! validate_required_vars "${REQUIRED_VARS[@]}"; then
    print_error "Please fix configuration issues before deploying"
    exit 1
fi

# Configuration from environment variables
SUBSCRIPTION_ID="$AZURE_SUBSCRIPTION_ID"
RESOURCE_GROUP="$AZURE_RESOURCE_GROUP"
LOCATION="$AZURE_LOCATION"
BICEP_FILE="azure-resources.bicep"
PARAMETERS_FILE="azure-parameters.json"

print_section "Azure Legend Platform Deployment"
echo "Subscription ID: $SUBSCRIPTION_ID"
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo ""

# Check prerequisites
check_prerequisites "azure"

# Login to Azure
print_status "Logging into Azure..."
az login

# Set subscription
print_status "Setting subscription to $SUBSCRIPTION_ID..."
az account set --subscription $SUBSCRIPTION_ID

# Create resource group
print_status "Creating resource group $RESOURCE_GROUP..."
az group create --name $RESOURCE_GROUP --location "$LOCATION"

# Generate MongoDB password
MONGO_PASSWORD=$(openssl rand -base64 32)
print_status "Generated MongoDB password"

# Deploy Azure infrastructure
print_status "Deploying Azure infrastructure..."
az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --template-file $BICEP_FILE \
    --parameters \
        mongoAdminPassword="$MONGO_PASSWORD" \
        aksNodeCount="$AKS_NODE_COUNT" \
        aksVmSize="$AKS_VM_SIZE" \
        aksMinNodes="$AKS_MIN_NODES" \
        aksMaxNodes="$AKS_MAX_NODES" \
        aksKubernetesVersion="$AKS_KUBERNETES_VERSION" \
        aksServiceCidr="$AKS_SERVICE_CIDR" \
        aksDnsServiceIp="$AKS_DNS_SERVICE_IP"

# Get deployment outputs
print_status "Getting deployment outputs..."
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

print_success "Azure infrastructure deployed successfully!"
echo ""

# Get AKS credentials
print_status "Getting AKS credentials..."
az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER_NAME --overwrite-existing

# Verify cluster connection
print_status "Verifying cluster connection..."
kubectl cluster-info

echo ""
print_success "Azure infrastructure deployment complete!"
print_section "Deployment Summary"
echo "Resource Group: $RESOURCE_GROUP"
echo "AKS Cluster: $AKS_CLUSTER_NAME"
echo "ACR: $ACR_NAME"
echo "ACR Login Server: $ACR_LOGIN_SERVER"
echo ""
print_section "Next Steps"
echo "1. Update your GitLab OAuth app redirect URI to point to Azure"
echo "2. Build and push Legend images to ACR"
echo "3. Deploy Legend using FINOS Kubernetes manifests"
echo ""
print_warning "MongoDB password: $MONGO_PASSWORD"
print_warning "Save this password securely - you'll need it for Legend configuration"
echo ""
print_status "For Legend deployment, use the FINOS provided manifests:"
echo "   https://legend.finos.org/docs/deployment/kubernetes"
echo ""
print_success "Ready to deploy Legend to Azure!"
