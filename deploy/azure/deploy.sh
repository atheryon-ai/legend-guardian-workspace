#!/bin/bash

# Legend Platform Azure Deployment Script
# Single source of truth for deploying Legend to Azure AKS

set -e

# Configuration
RESOURCE_GROUP="rs-finos-legend"
AKS_CLUSTER="aks-legend"
ACR_NAME="legendacr"
NAMESPACE="legend-system"
LOCATION="eastus"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Azure CLI
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI not installed. Please install: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    fi
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl not installed. Please install: https://kubernetes.io/docs/tasks/tools/"
        exit 1
    fi
    
    # Check Docker
    if ! docker info &> /dev/null; then
        print_error "Docker not running. Please start Docker."
        exit 1
    fi
    
    # Check Azure login
    if ! az account show &> /dev/null; then
        print_error "Not logged into Azure. Please run: az login"
        exit 1
    fi
    
    print_success "Prerequisites check completed"
}

# Function to setup Azure resources
setup_azure() {
    print_status "Setting up Azure resources..."
    
    # Create resource group if it doesn't exist
    if ! az group show --name $RESOURCE_GROUP &> /dev/null; then
        print_status "Creating resource group: $RESOURCE_GROUP"
        az group create --name $RESOURCE_GROUP --location $LOCATION
    fi
    
    # Create ACR if it doesn't exist
    if ! az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
        print_status "Creating Azure Container Registry: $ACR_NAME"
        az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic
    fi
    
    # Get ACR login server
    ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer -o tsv)
    print_status "ACR Login Server: $ACR_LOGIN_SERVER"
    
    # Login to ACR
    print_status "Logging into ACR..."
    az acr login --name $ACR_NAME
    
    # Create AKS cluster if it doesn't exist
    if ! az aks show --name $AKS_CLUSTER --resource-group $RESOURCE_GROUP &> /dev/null; then
        print_status "Creating AKS cluster: $AKS_CLUSTER"
        az aks create \
            --resource-group $RESOURCE_GROUP \
            --name $AKS_CLUSTER \
            --node-count 3 \
            --node-vm-size Standard_D2_v3 \
            --generate-ssh-keys \
            --attach-acr $ACR_NAME
    fi
    
    # Get AKS credentials
    print_status "Getting AKS credentials..."
    az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER --overwrite-existing
    
    print_success "Azure setup completed"
}

# Function to push Docker images
push_images() {
    print_status "Pushing Docker images to ACR..."
    
    # Check if images exist locally
    if docker images | grep -q "finos/legend-engine"; then
        print_status "Tagging and pushing Legend Engine..."
        docker tag finos/legend-engine-server:4.40.3 $ACR_LOGIN_SERVER/legend-engine:latest
        docker push $ACR_LOGIN_SERVER/legend-engine:latest || print_warning "Engine push failed - may already exist"
    fi
    
    if docker images | grep -q "finos/legend-sdlc"; then
        print_status "Tagging and pushing Legend SDLC..."
        docker tag finos/legend-sdlc-server:0.195.0 $ACR_LOGIN_SERVER/legend-sdlc:latest
        docker push $ACR_LOGIN_SERVER/legend-sdlc:latest || print_warning "SDLC push failed - may already exist"
    fi
    
    if docker images | grep -q "finos/legend-studio"; then
        print_status "Tagging and pushing Legend Studio..."
        docker tag finos/legend-studio:13.113.0 $ACR_LOGIN_SERVER/legend-studio:latest
        docker push $ACR_LOGIN_SERVER/legend-studio:latest || print_warning "Studio push failed - may already exist"
    fi
    
    print_success "Image push completed"
}

# Function to deploy to Kubernetes
deploy_to_k8s() {
    print_status "Deploying to Kubernetes..."
    
    # Apply the consolidated manifest
    kubectl apply -f "$(dirname "$0")/legend-stack.yaml"
    
    # Wait for deployments
    print_status "Waiting for deployments to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/mongodb -n $NAMESPACE || true
    kubectl wait --for=condition=available --timeout=300s deployment/legend-engine -n $NAMESPACE || true
    kubectl wait --for=condition=available --timeout=300s deployment/legend-sdlc -n $NAMESPACE || true
    kubectl wait --for=condition=available --timeout=300s deployment/legend-studio -n $NAMESPACE || true
    
    print_success "Deployment completed"
}

# Function to show status
show_status() {
    print_status "Deployment Status:"
    echo ""
    kubectl get pods -n $NAMESPACE
    echo ""
    kubectl get svc -n $NAMESPACE
    echo ""
    
    # Get external IP for Legend Studio
    STUDIO_IP=$(kubectl get svc legend-studio -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    
    print_status "Access URLs:"
    echo "  Legend Studio: http://$STUDIO_IP (LoadBalancer)"
    echo ""
    echo "For local access, use port-forward:"
    echo "  kubectl port-forward -n $NAMESPACE svc/legend-studio 9000:80"
    echo "  kubectl port-forward -n $NAMESPACE svc/legend-engine 6060:6060"
    echo "  kubectl port-forward -n $NAMESPACE svc/legend-sdlc 7070:7070"
}

# Main execution
main() {
    echo "========================================="
    echo "  Legend Platform Azure Deployment"
    echo "========================================="
    echo ""
    
    case "${1:-deploy}" in
        deploy)
            check_prerequisites
            setup_azure
            push_images
            deploy_to_k8s
            show_status
            ;;
        status)
            show_status
            ;;
        clean)
            print_status "Cleaning up deployments..."
            kubectl delete namespace $NAMESPACE --ignore-not-found=true
            print_success "Cleanup completed"
            ;;
        *)
            echo "Usage: $0 [deploy|status|clean]"
            echo "  deploy - Full deployment (default)"
            echo "  status - Show current status"
            echo "  clean  - Remove all deployments"
            exit 1
            ;;
    esac
}

main "$@"