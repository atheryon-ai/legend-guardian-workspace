#!/bin/bash

# Legend SDLC Deployment Script
# Deploys only Legend SDLC service

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source common functions library
source "$SCRIPT_DIR/../lib/common-functions.sh"

# Determine deployment environment (default to local)
DEPLOYMENT_ENV="${DEPLOYMENT_ENV:-local}"

# Load all configuration (base -> environment-specific -> secrets)
load_all_config "$DEPLOYMENT_ENV"

# Load SDLC-specific overrides if they exist
if [ -f "$SCRIPT_DIR/sdlc.env" ]; then
    source "$SCRIPT_DIR/sdlc.env"
fi

# Function to deploy Legend SDLC
deploy_sdlc() {
    print_status "Deploying Legend SDLC..."
    
    # Create namespace if it doesn't exist
    create_namespace
    
    # Apply ConfigMap if exists
    if [ -f "$SCRIPT_DIR/config/sdlc-config.yml" ]; then
        print_status "Creating ConfigMap..."
        kubectl create configmap legend-sdlc-config \
            --from-file=config.yml="$SCRIPT_DIR/config/sdlc-config.yml" \
            -n $K8S_NAMESPACE \
            --dry-run=client -o yaml | kubectl apply -f -
    fi
    
    # Apply Kubernetes manifest
    if [ -f "$SCRIPT_DIR/k8s/sdlc.yaml" ]; then
        print_status "Applying Kubernetes manifest..."
        envsubst < "$SCRIPT_DIR/k8s/sdlc.yaml" | kubectl apply -f -
    else
        print_error "Kubernetes manifest not found at $SCRIPT_DIR/k8s/sdlc.yaml"
        exit 1
    fi
    
    # Wait for deployment
    wait_for_deployment "legend-sdlc" "$K8S_NAMESPACE" 300
    
    print_success "Legend SDLC deployed successfully!"
}

# Function to validate deployment
validate_sdlc() {
    print_status "Validating Legend SDLC deployment..."
    
    # Check pod status
    if check_pod_status "legend-sdlc" "$K8S_NAMESPACE"; then
        print_success "Legend SDLC pod is running"
    else
        print_error "Legend SDLC pod is not running properly"
        return 1
    fi
    
    # Check service
    SERVICE_EXISTS=$(kubectl get svc legend-sdlc -n $K8S_NAMESPACE &>/dev/null && echo "yes" || echo "no")
    
    if [ "$SERVICE_EXISTS" = "yes" ]; then
        print_success "Legend SDLC service exists"
    else
        print_error "Legend SDLC service not found"
        return 1
    fi
    
    # Port forward for testing (if running locally)
    if [ "$DEPLOYMENT_ENV" = "local" ]; then
        print_status "Setting up port-forward for testing..."
        kubectl port-forward -n $K8S_NAMESPACE svc/legend-sdlc 6100:6100 &
        PF_PID=$!
        sleep 5
        
        # Test health endpoint
        if curl -f http://localhost:6100/api/info &>/dev/null 2>&1; then
            print_success "Legend SDLC health check passed"
        else
            print_warning "Legend SDLC health check failed (may need more time to start)"
        fi
        
        # Clean up port-forward
        kill $PF_PID 2>/dev/null || true
    fi
    
    print_success "Validation complete!"
    return 0
}

# Function to show status
show_status() {
    print_section "Legend SDLC Status"
    echo ""
    kubectl get deployment,pod,svc -n $K8S_NAMESPACE -l app=legend-sdlc
    echo ""
    
    # Show recent logs
    print_status "Recent logs:"
    kubectl logs -n $K8S_NAMESPACE -l app=legend-sdlc --tail=20 2>/dev/null || echo "No logs available"
}

# Function to clean up
cleanup() {
    print_warning "Removing Legend SDLC deployment..."
    kubectl delete deployment legend-sdlc -n $K8S_NAMESPACE --ignore-not-found=true
    kubectl delete service legend-sdlc -n $K8S_NAMESPACE --ignore-not-found=true
    kubectl delete configmap legend-sdlc-config -n $K8S_NAMESPACE --ignore-not-found=true
    print_success "Legend SDLC removed"
}

# Show configuration
show_config() {
    print_section "Legend SDLC Configuration"
    echo "Environment: $DEPLOYMENT_ENV"
    echo "Namespace: $K8S_NAMESPACE"
    echo "Version: $LEGEND_SDLC_VERSION"
    echo "Port: $LEGEND_SDLC_PORT"
    echo "Memory Limit: $SDLC_MEMORY_LIMIT"
    echo "CPU Limit: $SDLC_CPU_LIMIT"
    echo "Replicas: $SDLC_REPLICAS"
    echo "Java Options: $SDLC_JAVA_OPTS"
    echo "GitLab Host: $GITLAB_HOST"
    echo "GitLab App ID: ${GITLAB_APP_ID:0:10}..." # Show only first 10 chars for security
}

# Main execution
main() {
    print_section "Legend SDLC Deployment"
    echo ""
    
    case "${1:-deploy}" in
        deploy)
            show_config
            echo ""
            deploy_sdlc
            validate_sdlc
            show_status
            ;;
        validate)
            validate_sdlc
            ;;
        status)
            show_status
            ;;
        clean|cleanup)
            cleanup
            ;;
        config)
            show_config
            ;;
        *)
            echo "Usage: $0 [deploy|validate|status|clean|config]"
            echo "  deploy   - Deploy Legend SDLC (default)"
            echo "  validate - Validate deployment"
            echo "  status   - Show current status"
            echo "  clean    - Remove deployment"
            echo "  config   - Show configuration"
            exit 1
            ;;
    esac
}

main "$@"