#!/bin/bash

# Legend Platform Deployment Script for Azure AKS
# This script deploys the complete Legend platform once AKS is ready

set -e

echo "🚀 Legend Platform Deployment to Azure AKS"
echo "=========================================="

# Configuration
RESOURCE_GROUP="rs-finos-legend"
AKS_CLUSTER_NAME="aks-legend"
ACR_NAME="acrlegend10a89eda"
ACR_LOGIN_SERVER="${ACR_NAME}.azurecr.io"

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

# Check if AKS cluster is ready
check_aks_ready() {
    print_status "Checking AKS cluster status..."
    
    PROVISIONING_STATE=$(az aks show --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER_NAME --query provisioningState --output tsv)
    
    if [ "$PROVISIONING_STATE" = "Succeeded" ]; then
        print_status "✅ AKS cluster is ready!"
        return 0
    else
        print_warning "AKS cluster is still in state: $PROVISIONING_STATE"
        return 1
    fi
}

# Get AKS credentials
get_aks_credentials() {
    print_status "Getting AKS credentials..."
    az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER_NAME --overwrite-existing
    
    # Verify connection
    kubectl cluster-info
    print_status "✅ AKS credentials configured successfully"
}

# Assign ACR pull role to AKS
assign_acr_role() {
    print_status "Assigning ACR pull role to AKS..."
    
    AKS_PRINCIPAL_ID=$(az aks show --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER_NAME --query identity.principalId --output tsv)
    ACR_ID=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query id --output tsv)
    
    # Check if role assignment already exists
    EXISTING_ROLE=$(az role assignment list --assignee $AKS_PRINCIPAL_ID --scope $ACR_ID --query "[?roleDefinitionName=='AcrPull']" --output tsv)
    
    if [ -z "$EXISTING_ROLE" ]; then
        az role assignment create \
            --assignee $AKS_PRINCIPAL_ID \
            --role AcrPull \
            --scope $ACR_ID
        print_status "✅ ACR pull role assigned successfully"
    else
        print_status "✅ ACR pull role already assigned"
    fi
}

# Tag and push images to ACR
push_images_to_acr() {
    print_status "Tagging and pushing Legend images to ACR..."
    
    # Login to ACR
    az acr login --name $ACR_NAME
    
    # Tag images
    docker tag legend-engine:latest $ACR_LOGIN_SERVER/legend-engine:latest
    docker tag legend-sdlc:latest $ACR_LOGIN_SERVER/legend-sdlc:latest
    docker tag legend-studio:latest $ACR_LOGIN_SERVER/legend-studio:latest
    
    # Push images
    docker push $ACR_LOGIN_SERVER/legend-engine:latest
    docker push $ACR_LOGIN_SERVER/legend-sdlc:latest
    docker push $ACR_LOGIN_SERVER/legend-studio:latest
    
    print_status "✅ All Legend images pushed to ACR successfully"
}

# Deploy Legend platform
deploy_legend() {
    print_status "Deploying Legend platform to AKS..."
    
    # Create namespace and config
    kubectl apply -f k8s/legend-namespace.yaml
    
    # Create secrets
    kubectl apply -f k8s/legend-secrets.yaml
    
    # Deploy services
    kubectl apply -f k8s/legend-engine.yaml
    kubectl apply -f k8s/legend-sdlc.yaml
    kubectl apply -f k8s/legend-studio.yaml
    
    print_status "✅ Legend platform deployment initiated"
}

# Wait for deployment to be ready
wait_for_deployment() {
    print_status "Waiting for Legend services to be ready..."
    
    # Wait for Engine
    kubectl wait --for=condition=available --timeout=300s deployment/legend-engine -n legend
    print_status "✅ Legend Engine is ready"
    
    # Wait for SDLC
    kubectl wait --for=condition=available --timeout=300s deployment/legend-sdlc -n legend
    print_status "✅ Legend SDLC is ready"
    
    # Wait for Studio
    kubectl wait --for=condition=available --timeout=300s deployment/legend-studio -n legend
    print_status "✅ Legend Studio is ready"
}

# Install NGINX Ingress Controller
install_ingress_controller() {
    print_status "Installing NGINX Ingress Controller..."
    
    # Check if ingress controller already exists
    if kubectl get namespace ingress-nginx >/dev/null 2>&1; then
        print_status "✅ NGINX Ingress Controller already installed"
        return 0
    fi
    
    # Install NGINX Ingress Controller
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
    
    # Wait for ingress controller to be ready
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=300s
    
    print_status "✅ NGINX Ingress Controller installed and ready"
}

# Verify deployment
verify_deployment() {
    print_status "Verifying Legend platform deployment..."
    
    echo ""
    echo "📊 Deployment Status:"
    kubectl get all -n legend
    
    echo ""
    echo "🔍 Service Endpoints:"
    kubectl get svc -n legend
    
    echo ""
    echo "📡 Pod Status:"
    kubectl get pods -n legend
    
    echo ""
    echo "🌐 Ingress Status:"
    kubectl get ingress -n legend
}

# Display access information
display_access_info() {
    echo ""
    echo "🎉 Legend Platform Deployment Complete!"
    echo "====================================="
    echo ""
    echo "📱 Access Information:"
    echo "  • Legend Studio: http://localhost:9000 (port-forward)"
    echo "  • Legend Engine: http://localhost:6300 (port-forward)"
    echo "  • Legend SDLC: http://localhost:6100 (port-forward)"
    echo ""
    echo "🔧 Management Commands:"
    echo "  • Check status: kubectl get all -n legend"
    echo "  • View logs: kubectl logs -l app=legend-engine -n legend"
    echo "  • Port forward: kubectl port-forward svc/legend-studio 9000:9000 -n legend"
    echo ""
    echo "📚 Next Steps:"
    echo "  1. Update GitLab OAuth redirect URI to point to Azure endpoints"
    echo "  2. Configure custom domain and TLS certificates"
    echo "  3. Set up monitoring and alerting"
    echo "  4. Test authentication and functionality"
}

# Main deployment flow
main() {
    echo "Starting Legend platform deployment..."
    
    # Check prerequisites
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI is not installed"
        exit 1
    fi
    
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    # Check if AKS is ready
    if ! check_aks_ready; then
        print_error "AKS cluster is not ready yet. Please wait and try again."
        exit 1
    fi
    
    # Deploy Legend platform
    get_aks_credentials
    assign_acr_role
    push_images_to_acr
    deploy_legend
    wait_for_deployment
    install_ingress_controller
    verify_deployment
    display_access_info
    
    print_status "🎉 Legend platform deployment completed successfully!"
}

# Run main function
main "$@"
