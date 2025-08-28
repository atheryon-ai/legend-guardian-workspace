#!/bin/bash

# Legend Platform Azure Deployment Script
# Uses Kustomize to apply environment-specific overlays to the base k8s manifests.
# See deploy/README.md for details on the Kustomize strategy.

set -e

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Environment and Action are passed as arguments
ENVIRONMENT=$1
ACTION=${2:-deploy}

# Dynamic configuration based on environment
OVERLAY_DIR="$PROJECT_ROOT/deploy/k8s-overrides/$ENVIRONMENT"
NAMESPACE=${NAMESPACE:-legend}
RESOURCE_GROUP=${AZURE_RESOURCE_GROUP:-rs-finos-legend}
AKS_CLUSTER=${AZURE_AKS_CLUSTER:-aks-legend}
LOCATION=${AZURE_LOCATION:-eastus}

# --- Output Colors ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

# --- Script Functions ---

# Check for required tools and Azure login
check_prerequisites() {
    print_status "Checking prerequisites..."
    local missing_tools=()
    command -v az &>/dev/null || missing_tools+=("az")
    command -v kubectl &>/dev/null || missing_tools+=("kubectl")
    command -v kustomize &>/dev/null || missing_tools+=("kustomize")

    if [ ${#missing_tools[@]} -gt 0 ]; then
        print_error "Missing required tools: ${missing_tools[*]}"
        exit 1
    fi

    if ! az account show &>/dev/null; then
        print_error "Not logged into Azure. Please run: az login"
        exit 1
    fi
    print_success "Prerequisites check completed"
}

# Provision Azure infrastructure (Resource Group, AKS Cluster, Ingress)
setup_infrastructure() {
    print_status "Setting up Azure infrastructure..."

    if ! az group show --name $RESOURCE_GROUP &>/dev/null; then
        print_status "Creating resource group: $RESOURCE_GROUP"
        az group create --name $RESOURCE_GROUP --location $LOCATION
    fi

    if ! az aks show --name $AKS_CLUSTER --resource-group $RESOURCE_GROUP &>/dev/null; then
        print_status "Creating AKS cluster with optimized configuration..."
        az aks create \
            --resource-group $RESOURCE_GROUP \
            --name $AKS_CLUSTER \
            --location $LOCATION \
            --node-count 3 \
            --node-vm-size Standard_D4s_v3 \
            --enable-cluster-autoscaler \
            --min-count 3 \
            --max-count 5 \
            --enable-managed-identity \
            --network-plugin azure \
            --generate-ssh-keys
    fi

    print_status "Getting AKS credentials..."
    az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER --overwrite-existing

    if ! kubectl get namespace ingress-nginx &>/dev/null; then
        print_status "Installing NGINX Ingress Controller..."
        kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
        print_status "Waiting for ingress controller to be ready..."
        kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=120s || true
    fi
    print_success "Infrastructure setup completed"
}

# Deploy services using the specified Kustomize overlay
deploy_services() {
    print_status "Deploying Legend services from overlay: $OVERLAY_DIR"

    # NOTE: Secret management (e.g., for GitLab OAuth) is now handled declaratively
    # within the Kustomize overlay itself, typically using a secretGenerator.
    # This script no longer handles secrets imperatively.

    print_status "Building and applying manifests with Kustomize..."
    kubectl apply -k "$OVERLAY_DIR"

    print_status "Waiting for deployments to be ready..."
    kubectl wait --for=condition=available --timeout=300s \
        deployment/legend-engine deployment/legend-studio deployment/legend-sdlc \
        -n $NAMESPACE || print_warning "Timed out waiting for all deployments to become available. Check status manually."

    print_success "Services deployed successfully"
}

# Validate the deployment by checking pods and testing an endpoint
validate_deployment() {
    print_status "Validating deployment..."
    local errors=0

    print_status "Checking pod status..."
    local not_running=$(kubectl get pods -n $NAMESPACE --field-selector=status.phase!=Running --no-headers 2>/dev/null | wc -l)
    if [ "$not_running" -gt 0 ]; then
        print_warning "Some pods are not running:"
        kubectl get pods -n $NAMESPACE
        ((errors++))
    else
        print_success "All pods are running"
    fi

    print_status "Testing Legend Engine service endpoint..."
    kubectl port-forward -n $NAMESPACE svc/legend-engine 6300:6300 &>/dev/null &
    local pf_pid=$!
    sleep 5
    if curl -s http://localhost:6300/api/server/v1/info &>/dev/null; then
        print_success "Legend Engine is responding"
    else
        print_error "Legend Engine not responding"
        ((errors++))
    fi
    kill $pf_pid 2>/dev/null || true

    if [ $errors -eq 0 ]; then
        print_success "Validation passed!"
        return 0
    else
        print_error "Validation failed with $errors errors"
        return 1
    fi
}

# Show the status of the deployment
show_status() {
    echo ""
    echo "=== Deployment Status for Environment: $ENVIRONMENT ==="
    echo -e "\nDeployments:"
    kubectl get deployments -n $NAMESPACE 2>/dev/null || echo "No deployments found"
    echo -e "\nPods:"
    kubectl get pods -n $NAMESPACE 2>/dev/null || echo "No pods found"
    echo -e "\nServices:"
    kubectl get svc -n $NAMESPACE 2>/dev/null || echo "No services found"
    echo -e "\nIngress:"
    kubectl get ingress -n $NAMESPACE 2>/dev/null || echo "No ingress found"
}

# Clean the deployment by deleting the namespace
clean_deployment() {
    print_warning "This will delete the entire '$NAMESPACE' namespace in your cluster."
    read -p "Are you sure? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cleaning Legend deployment..."
        kubectl delete namespace $NAMESPACE --wait=true --timeout=60s || true
        print_success "Cleanup completed"
    else
        print_status "Cleanup cancelled."
    fi
}

# --- Main Execution ---
main() {
    if [ -z "$ENVIRONMENT" ]; then
        print_error "Usage: $0 <environment> [action]"
        echo "  <environment>: Name of the overlay directory in 'deploy/k8s-overrides/' (e.g., production, development)"
        echo "  [action]: deploy, apply, validate, status, clean (default: deploy)"
        exit 1
    fi

    if [ ! -d "$OVERLAY_DIR" ]; then
        print_error "Overlay directory not found for environment '$ENVIRONMENT' at: $OVERLAY_DIR"
        exit 1
    fi

    echo "================================================"
    echo "  Legend Platform Azure Deployment"
    echo "  Environment: $ENVIRONMENT"
    echo "  Action:      $ACTION"
    echo "================================================"

    case "$ACTION" in
        deploy)
            check_prerequisites
            setup_infrastructure
            deploy_services
            validate_deployment
            show_status
            ;;
        apply)
            check_prerequisites
            deploy_services
            validate_deployment
            ;;
        validate)
            validate_deployment
            ;;
        status)
            show_status
            ;;
        clean)
            clean_deployment
            ;;
        *)
            print_error "Invalid action: $ACTION"
            echo "Valid actions are: deploy, apply, validate, status, clean"
            exit 1
            ;;
    esac
}

main "$@"
