#!/bin/bash

# Build and Push Legend Images to Azure Container Registry
# This script builds the Legend images and pushes them to ACR

set -e

# Load Azure environment variables
if [ -f "azure-legend.env" ]; then
    source azure-legend.env
else
    echo "❌ azure-legend.env file not found. Please run the Azure deployment first."
    exit 1
fi

echo "🐳 Building and Pushing Legend Images to Azure Container Registry"
echo "================================================================"
echo "ACR Login Server: $AZURE_ACR_LOGIN_SERVER"
echo "ACR Username: $AZURE_ACR_USERNAME"
echo ""

# Login to Azure Container Registry
echo "🔐 Logging into Azure Container Registry..."
echo $AZURE_ACR_PASSWORD | docker login $AZURE_ACR_LOGIN_SERVER -u $AZURE_ACR_USERNAME --password-stdin

# Build and push Legend Engine
echo "🚀 Building and pushing Legend Engine..."
docker build -t $AZURE_ACR_LOGIN_SERVER/legend-engine:latest \
    --build-arg LEGEND_VERSION=4.40.3 \
    -f Dockerfile.engine .
docker push $AZURE_ACR_LOGIN_SERVER/legend-engine:latest

# Build and push Legend SDLC
echo "📚 Building and pushing Legend SDLC..."
docker build -t $AZURE_ACR_LOGIN_SERVER/legend-sdlc:latest \
    --build-arg LEGEND_VERSION=0.195.0 \
    -f Dockerfile.sdlc .
docker push $AZURE_ACR_LOGIN_SERVER/legend-sdlc:latest

# Build and push Legend Studio
echo "🎨 Building and pushing Legend Studio..."
docker build -t $AZURE_ACR_LOGIN_SERVER/legend-studio:latest \
    --build-arg LEGEND_VERSION=13.113.0 \
    -f Dockerfile.studio .
docker push $AZURE_ACR_LOGIN_SERVER/legend-studio:latest

echo ""
echo "✅ All Legend images built and pushed successfully!"
echo "=================================================="
echo "Images available in ACR:"
echo "- $AZURE_ACR_LOGIN_SERVER/legend-engine:latest"
echo "- $AZURE_ACR_LOGIN_SERVER/legend-sdlc:latest"
echo "- $AZURE_ACR_LOGIN_SERVER/legend-studio:latest"
echo ""
echo "🚀 Ready to deploy Legend to AKS!"
