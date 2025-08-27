#!/bin/bash

# MongoDB Deployment Script
# Handles deployment, validation, and cleanup of MongoDB service

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source common functions
source "$DEPLOY_DIR/shared/lib/common-functions.sh"

# Determine deployment environment
DEPLOYMENT_ENV="${DEPLOYMENT_ENV:-local}"

# Load configuration
load_all_config "$DEPLOYMENT_ENV"

# Service-specific variables
SERVICE_NAME="mongodb"
SERVICE_PORT="${MONGODB_PORT:-27017}"

# Deploy function
deploy() {
    print_section "Deploying MongoDB"
    
    # Process and apply Kubernetes manifest
    print_status "Applying MongoDB deployment..."
    envsubst < "$SCRIPT_DIR/k8s/mongodb.yaml" | kubectl apply -f -
    
    # Wait for deployment to be ready
    print_status "Waiting for MongoDB to be ready..."
    kubectl wait --for=condition=available --timeout=300s \
        deployment/mongodb -n $K8S_NAMESPACE
    
    # Wait for pod to be ready
    kubectl wait --for=condition=ready --timeout=300s \
        pod -l app=mongodb -n $K8S_NAMESPACE
    
    print_success "MongoDB deployed successfully!"
}

# Validate function
validate() {
    print_section "Validating MongoDB"
    
    local validation_passed=true
    
    # Check deployment
    print_status "Checking MongoDB deployment..."
    if kubectl get deployment mongodb -n $K8S_NAMESPACE &>/dev/null; then
        print_success "MongoDB deployment exists"
    else
        print_error "MongoDB deployment not found"
        validation_passed=false
    fi
    
    # Check service
    print_status "Checking MongoDB service..."
    if kubectl get service mongodb -n $K8S_NAMESPACE &>/dev/null; then
        print_success "MongoDB service exists"
    else
        print_error "MongoDB service not found"
        validation_passed=false
    fi
    
    # Check pod status
    print_status "Checking MongoDB pod status..."
    local pod_status=$(kubectl get pods -n $K8S_NAMESPACE -l app=mongodb \
        -o jsonpath='{.items[0].status.phase}' 2>/dev/null)
    
    if [ "$pod_status" = "Running" ]; then
        print_success "MongoDB pod is running"
    else
        print_error "MongoDB pod is not running (status: $pod_status)"
        validation_passed=false
    fi
    
    # Check connectivity (if port-forward is available)
    print_status "Checking MongoDB connectivity..."
    local pod_name=$(kubectl get pods -n $K8S_NAMESPACE -l app=mongodb \
        -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    
    if [ -n "$pod_name" ]; then
        # Try to connect to MongoDB
        if kubectl exec -n $K8S_NAMESPACE $pod_name -- mongosh --eval "db.version()" &>/dev/null; then
            print_success "MongoDB is responding to queries"
        else
            print_warning "MongoDB connectivity check failed (this may be normal if auth is required)"
        fi
    fi
    
    if [ "$validation_passed" = true ]; then
        print_success "MongoDB validation passed!"
        return 0
    else
        print_error "MongoDB validation failed!"
        return 1
    fi
}

# Status function
status() {
    print_section "MongoDB Status"
    
    echo ""
    kubectl get deployment,service,pods,pvc -n $K8S_NAMESPACE -l app=mongodb
    echo ""
    
    # Show logs tail
    print_status "Recent logs:"
    kubectl logs -n $K8S_NAMESPACE -l app=mongodb --tail=10
}

# Clean function
clean() {
    print_section "Cleaning up MongoDB"
    
    print_warning "This will remove MongoDB and all its data!"
    
    # Delete Kubernetes resources
    print_status "Removing MongoDB deployment..."
    kubectl delete -f "$SCRIPT_DIR/k8s/mongodb.yaml" --ignore-not-found=true
    
    print_success "MongoDB cleaned up!"
}

# Main execution
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    validate)
        validate
        ;;
    status)
        status
        ;;
    clean|cleanup)
        clean
        ;;
    *)
        echo "Usage: $0 [deploy|validate|status|clean]"
        echo "  deploy   - Deploy MongoDB"
        echo "  validate - Validate MongoDB deployment"
        echo "  status   - Show MongoDB status"
        echo "  clean    - Remove MongoDB deployment"
        exit 1
        ;;
esac