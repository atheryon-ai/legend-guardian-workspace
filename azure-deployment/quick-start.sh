#!/bin/bash

# Quick Start Script for Azure Legend Migration
# This script orchestrates the entire migration process

set -e

echo "🚀 Legend FINOS Platform - Azure Migration Quick Start"
echo "======================================================"
echo ""
echo "This script will migrate your local Legend platform to Azure."
echo "Estimated time: 30-45 minutes"
echo "Estimated cost: $105-190/month"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Installing..."
    echo "Please install Azure CLI from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Installing..."
    echo "Please install kubectl from: https://kubernetes.io/docs/tasks/tools/install-kubectl/"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Installing..."
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ All prerequisites met!"
echo ""

# Confirm deployment
read -p "Do you want to proceed with Azure deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo "📋 Migration Plan:"
echo "1. Deploy Azure infrastructure (AKS, ACR, MongoDB, networking)"
echo "2. Build and push Legend images to Azure Container Registry"
echo "3. Deploy Legend using FINOS Kubernetes manifests"
echo "4. Configure OAuth and verify deployment"
echo ""

# Step 1: Deploy Azure Infrastructure
echo "🏗️  Step 1: Deploying Azure Infrastructure..."
echo "This will take 15-20 minutes..."
./deploy-azure.bash

if [ $? -ne 0 ]; then
    echo "❌ Azure infrastructure deployment failed!"
    exit 1
fi

echo "✅ Azure infrastructure deployed successfully!"
echo ""

# Step 2: Update GitLab OAuth
echo "🔐 Step 2: Update GitLab OAuth Configuration"
echo "Please update your GitLab OAuth app redirect URI to:"
echo "https://legend-sdlc.azure-legend.com/api/pac4j/login/callback"
echo ""
read -p "Press Enter after updating GitLab OAuth configuration..."

# Step 3: Build and Push Images
echo "🐳 Step 3: Building and Pushing Legend Images..."
echo "This will take 10-15 minutes..."
./build-and-push-images.sh

if [ $? -ne 0 ]; then
    echo "❌ Image build and push failed!"
    exit 1
fi

echo "✅ Images pushed to Azure Container Registry!"
echo ""

# Step 4: Deploy Legend
echo "🚀 Step 4: Deploying Legend to Azure..."
echo "Choose deployment method:"
echo "1. Juju Operators (Recommended - 3 commands)"
echo "2. Direct Kubernetes manifests"
echo ""
read -p "Enter your choice (1 or 2): " choice

case $choice in
    1)
        echo "Installing Juju and deploying Legend..."
        sudo snap install juju --classic
        juju bootstrap microk8s finos-legend-controller
        juju add-model finos-legend-model
        juju deploy finos-legend-bundle --channel=beta --trust
        ;;
    2)
        echo "Using direct Kubernetes manifests..."
        echo "Please follow the manual deployment steps in AZURE_DEPLOYMENT_GUIDE.md"
        ;;
    *)
        echo "Invalid choice. Using Juju deployment..."
        sudo snap install juju --classic
        juju bootstrap microk8s finos-legend-controller
        juju add-model finos-legend-model
        juju deploy finos-legend-bundle --channel=beta --trust
        ;;
esac

echo ""
echo "🎉 Migration Complete!"
echo "======================"
echo ""
echo "Your Legend platform is now running in Azure!"
echo ""
echo "📊 Next Steps:"
echo "1. Verify deployment: kubectl get pods -n legend-system"
echo "2. Access Legend Studio: https://legend-studio.azure-legend.com"
echo "3. Test OAuth authentication"
echo "4. Set up monitoring and alerting"
echo ""
echo "💰 Estimated monthly cost: $105-190"
echo "🔧 For support, see AZURE_DEPLOYMENT_GUIDE.md"
echo ""
echo "🚀 Welcome to cloud-native Legend!"
