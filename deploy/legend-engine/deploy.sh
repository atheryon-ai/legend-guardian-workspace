#!/bin/bash

# Legend Engine Deployment Script
# Deploys only Legend Engine service

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source common functions library
source "$SCRIPT_DIR/../lib/common-functions.sh"

# Determine deployment environment (default to local)
DEPLOYMENT_ENV="${DEPLOYMENT_ENV:-local}"

# Load all configuration (base -> environment-specific -> secrets)
load_all_config "$DEPLOYMENT_ENV"

# Load engine-specific overrides if they exist
if [ -f "$SCRIPT_DIR/engine.env" ]; then
    source "$SCRIPT_DIR/engine.env"
fi

# Function to deploy Legend Engine
deploy_engine() {
    print_status "Deploying Legend Engine..."
    
    # Create namespace if it doesn't exist
    create_namespace
    
    # Apply ConfigMap if exists
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
    wait_for_deployment "legend-engine" "$K8S_NAMESPACE" 300
    
    print_success "Legend Engine deployed successfully!"
}

# Function to validate deployment
validate_engine() {
    print_status "Validating Legend Engine deployment..."
    
    # Check pod status
    if check_pod_status "legend-engine" "$K8S_NAMESPACE"; then
        print_success "Legend Engine pod is running"
    else
        print_error "Legend Engine pod is not running properly"
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
    
    # Port forward for testing (if running locally)
    if [ "$DEPLOYMENT_ENV" = "local" ]; then
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
    fi
    
    print_success "Validation complete!"
    return 0
}

# Function to show status
show_status() {
    print_section "Legend Engine Status"
    echo ""
    kubectl get deployment,pod,svc -n $K8S_NAMESPACE -l app=legend-engine
    echo ""
    
    # Show recent logs
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

# Show configuration
show_config() {
    print_section "Legend Engine Configuration"
    echo "Environment: $DEPLOYMENT_ENV"
    echo "Namespace: $K8S_NAMESPACE"
    echo "Version: $LEGEND_ENGINE_VERSION"
    echo "Port: $LEGEND_ENGINE_PORT"
    echo "Memory Limit: $ENGINE_MEMORY_LIMIT"
    echo "CPU Limit: $ENGINE_CPU_LIMIT"
    echo "Replicas: $ENGINE_REPLICAS"
    echo "Java Options: $ENGINE_JAVA_OPTS"
}

# Main execution
main() {
    print_section "Legend Engine Deployment"
    echo ""
    
    case "${1:-deploy}" in
        deploy)
            show_config
            echo ""
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
        config)
            show_config
            ;;
        *)
            echo "Usage: $0 [deploy|validate|status|clean|config]"
            echo "  deploy   - Deploy Legend Engine (default)"
            echo "  validate - Validate deployment"
            echo "  status   - Show current status"
            echo "  clean    - Remove deployment"
            echo "  config   - Show configuration"
            exit 1
            ;;
    esac
}

main "$@"