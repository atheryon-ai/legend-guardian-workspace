#!/bin/bash

# Legend Engine Deployment Script
# Deploys only Legend Engine service

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

# Load common variables
source "$SCRIPT_DIR/../common.env"

# Load secrets if available (from parent directory)
if [ -f "$SCRIPT_DIR/../../secrets.env" ]; then
    print_status "Loading secrets from secrets.env..."
    source "$SCRIPT_DIR/../../secrets.env"
elif [ -f "$SCRIPT_DIR/../../.env.local" ]; then
    print_status "Loading secrets from .env.local..."
    source "$SCRIPT_DIR/../../.env.local"
else
    print_warning "No secrets file found. Using placeholder values from common.env"
fi

# Load engine-specific variables
source "$SCRIPT_DIR/engine.env"

# Function to deploy Legend Engine
deploy_engine() {
    print_status "Deploying Legend Engine..."
    
    # Check if namespace exists
    if ! kubectl get namespace $K8S_NAMESPACE &>/dev/null; then
        print_status "Creating namespace $K8S_NAMESPACE..."
        kubectl create namespace $K8S_NAMESPACE
    fi
    
    # Apply ConfigMap
    if [ -f "$SCRIPT_DIR/config/engine-config.yml" ]; then
        print_status "Creating ConfigMap..."
        kubectl create configmap legend-engine-config \
            --from-file=config.yml="$SCRIPT_DIR/config/engine-config.yml" \
            -n $K8S_NAMESPACE \
            --dry-run=client -o yaml | kubectl apply -f -
    fi
    
    # Apply Kubernetes manifest
    if [ -f "$SCRIPT_DIR/k8s/engine.yaml" ]; then
        print_status "Applying Kubernetes manifest..."
        envsubst < "$SCRIPT_DIR/k8s/engine.yaml" | kubectl apply -f -
    else
        print_error "Kubernetes manifest not found at $SCRIPT_DIR/k8s/engine.yaml"
        exit 1
    fi
    
    # Wait for deployment
    print_status "Waiting for Legend Engine to be ready..."
    kubectl wait --for=condition=available --timeout=300s \
        deployment/legend-engine -n $K8S_NAMESPACE || true
    
    print_success "Legend Engine deployed successfully!"
}

# Function to validate deployment
validate_engine() {
    print_status "Validating Legend Engine deployment..."
    
    # Check pod status
    POD_STATUS=$(kubectl get pods -n $K8S_NAMESPACE -l app=legend-engine -o jsonpath='{.items[0].status.phase}' 2>/dev/null || echo "Not Found")
    
    if [ "$POD_STATUS" = "Running" ]; then
        print_success "Legend Engine pod is running"
    else
        print_error "Legend Engine pod status: $POD_STATUS"
        return 1
    fi
    
    # Check service
    SERVICE_EXISTS=$(kubectl get svc legend-engine -n $K8S_NAMESPACE &>/dev/null && echo "yes" || echo "no")
    
    if [ "$SERVICE_EXISTS" = "yes" ]; then
        print_success "Legend Engine service exists"
    else
        print_error "Legend Engine service not found"
        return 1
    fi
    
    # Port forward for testing
    print_status "Setting up port-forward for testing..."
    kubectl port-forward -n $K8S_NAMESPACE svc/legend-engine 6300:6300 &
    PF_PID=$!
    sleep 5
    
    # Test health endpoint
    if curl -f http://localhost:6300/api/server/v1/info &>/dev/null 2>&1; then
        print_success "Legend Engine health check passed"
    else
        print_warning "Legend Engine health check failed (may need more time to start)"
    fi
    
    # Clean up port-forward
    kill $PF_PID 2>/dev/null || true
    
    print_success "Validation complete!"
}

# Function to show status
show_status() {
    print_status "Legend Engine Status:"
    echo ""
    kubectl get deployment,pod,svc -n $K8S_NAMESPACE -l app=legend-engine
    echo ""
    
    # Show logs tail
    print_status "Recent logs:"
    kubectl logs -n $K8S_NAMESPACE -l app=legend-engine --tail=20 2>/dev/null || echo "No logs available"
}

# Function to clean up
cleanup() {
    print_warning "Removing Legend Engine deployment..."
    kubectl delete deployment legend-engine -n $K8S_NAMESPACE --ignore-not-found=true
    kubectl delete service legend-engine -n $K8S_NAMESPACE --ignore-not-found=true
    kubectl delete configmap legend-engine-config -n $K8S_NAMESPACE --ignore-not-found=true
    print_success "Legend Engine removed"
}

# Main execution
main() {
    echo "========================================="
    echo "     Legend Engine Deployment"
    echo "========================================="
    echo ""
    
    case "${1:-deploy}" in
        deploy)
            deploy_engine
            validate_engine
            show_status
            ;;
        validate)
            validate_engine
            ;;
        status)
            show_status
            ;;
        clean|cleanup)
            cleanup
            ;;
        *)
            echo "Usage: $0 [deploy|validate|status|clean]"
            echo "  deploy   - Deploy Legend Engine (default)"
            echo "  validate - Validate deployment"
            echo "  status   - Show current status"
            echo "  clean    - Remove deployment"
            exit 1
            ;;
    esac
}

main "$@"