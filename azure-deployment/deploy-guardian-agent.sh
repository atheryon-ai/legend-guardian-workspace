#!/bin/bash

# Legend Guardian Agent Azure Deployment Script
# This script builds and deploys the Legend Guardian Agent to Azure AKS

set -e

echo "🚀 Starting Legend Guardian Agent Azure Deployment..."

# Configuration
ACR_NAME="legendacr"
AKS_CLUSTER_NAME="aks-legend"
RESOURCE_GROUP="legend-rg"
NAMESPACE="legend"
IMAGE_NAME="legend-guardian-agent"
IMAGE_TAG="latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed. Please install it first."
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install it first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_status "Checking Azure login status..."
if ! az account show &> /dev/null; then
    print_warning "Not logged into Azure. Please run 'az login' first."
    exit 1
fi

print_status "Setting Azure subscription..."
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
print_status "Using subscription: $SUBSCRIPTION_ID"

# Get ACR login server
print_status "Getting ACR login server..."
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer -o tsv)
if [ -z "$ACR_LOGIN_SERVER" ]; then
    print_error "Could not find ACR: $ACR_NAME in resource group: $RESOURCE_GROUP"
    exit 1
fi
print_status "ACR login server: $ACR_LOGIN_SERVER"

# Get AKS credentials
print_status "Getting AKS credentials..."
az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER_NAME --overwrite-existing

# Check if namespace exists, create if not
print_status "Checking namespace..."
if ! kubectl get namespace $NAMESPACE &> /dev/null; then
    print_status "Creating namespace: $NAMESPACE"
    kubectl create namespace $NAMESPACE
fi

# Build Docker image
print_status "Building Docker image..."
cd ..
docker build -t $IMAGE_NAME:$IMAGE_TAG .

# Tag for ACR
FULL_IMAGE_NAME="$ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG"
docker tag $IMAGE_NAME:$IMAGE_TAG $FULL_IMAGE_NAME

# Push to ACR
print_status "Pushing image to ACR..."
az acr login --name $ACR_NAME
docker push $FULL_IMAGE_NAME

# Update deployment with correct image
print_status "Updating deployment with ACR image..."
cd azure-deployment
sed -i.bak "s|image: legend-guardian-agent:latest|image: $FULL_IMAGE_NAME|g" k8s/legend-guardian-agent.yaml

# Deploy to Kubernetes
print_status "Deploying to Kubernetes..."
kubectl apply -f k8s/legend-guardian-agent.yaml

# Wait for deployment to be ready
print_status "Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/legend-guardian-agent -n $NAMESPACE

# Check deployment status
print_status "Checking deployment status..."
kubectl get pods -n $NAMESPACE -l app=legend-guardian-agent

# Get service information
print_status "Getting service information..."
kubectl get svc -n $NAMESPACE legend-guardian-agent

# Get ingress information
print_status "Getting ingress information..."
kubectl get ingress -n $NAMESPACE legend-guardian-agent-ingress

print_status "🎉 Legend Guardian Agent deployment completed!"
print_status "The agent is now running on Azure AKS"
print_status "You can access it via the ingress URL or port-forward:"
echo ""
print_status "Port forward to local machine:"
echo "kubectl port-forward -n $NAMESPACE svc/legend-guardian-agent 8000:8000"
echo ""
print_status "Health check:"
echo "curl http://localhost:8000/health"
echo ""
print_status "API documentation:"
echo "http://localhost:8000/docs"
