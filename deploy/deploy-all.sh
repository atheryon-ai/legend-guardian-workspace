#!/bin/bash

# Master Deployment Script for Legend Platform
# Orchestrates deployment of all Legend services

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source common functions library
source "$SCRIPT_DIR/lib/common-functions.sh"

# Determine deployment environment (default to local)
DEPLOYMENT_ENV="${DEPLOYMENT_ENV:-local}"

# Load all configuration (base -> environment-specific -> secrets)
load_all_config "$DEPLOYMENT_ENV"

# Wrapper function to check prerequisites specific to this deployment
check_deployment_prerequisites() {
    print_section "Checking Deployment Prerequisites"
    
    # Use common function to check prerequisites based on environment
    if [ "$DEPLOYMENT_ENV" = "local" ]; then
        check_prerequisites "local"
    else
        check_prerequisites "k8s"
    fi
    
    # Check code quality (optional but recommended)
    if [ -f "$SCRIPT_DIR/check-code-quality.sh" ]; then
        print_status "Running code quality check..."
        if "$SCRIPT_DIR/check-code-quality.sh" >/dev/null 2>&1; then
            print_success "Code quality check passed"
        else
            print_warning "Code quality issues found - consider running ./check-code-quality.sh for details"
        fi
    fi
    
    # Validate configuration
    if [ -f "$SCRIPT_DIR/validate-config.sh" ]; then
        print_status "Validating configuration..."
        if "$SCRIPT_DIR/validate-config.sh" "$DEPLOYMENT_ENV" >/dev/null 2>&1; then
            print_success "Configuration validated"
        else
            print_warning "Configuration has issues - run ./validate-config.sh for details"
        fi
    fi
}

# Function to deploy a service
deploy_service() {
    local service=$1
    local deploy_script="$SCRIPT_DIR/$service/deploy.sh"
    
    if [ -f "$deploy_script" ]; then
        print_section "Deploying $service"
        bash "$deploy_script" deploy
    else
        print_warning "Deployment script not found for $service"
    fi
}

# Function to validate a service
validate_service() {
    local service=$1
    local deploy_script="$SCRIPT_DIR/$service/deploy.sh"
    
    if [ -f "$deploy_script" ]; then
        bash "$deploy_script" validate
    else
        print_warning "Validation script not found for $service"
    fi
}

# Function to show overall status
show_status() {
    print_section "Legend Platform Status"
    
    echo ""
    kubectl get all -n $K8S_NAMESPACE
    echo ""
    
    # Show service endpoints
    print_status "Service Endpoints:"
    kubectl get svc -n $K8S_NAMESPACE -o wide
    echo ""
    
    # Show pod status
    print_status "Pod Status:"
    kubectl get pods -n $K8S_NAMESPACE -o wide
    echo ""
    
    # Show ingress if exists
    if kubectl get ingress -n $K8S_NAMESPACE &>/dev/null; then
        print_status "Ingress:"
        kubectl get ingress -n $K8S_NAMESPACE
    fi
}

# Function to deploy all services
deploy_all() {
    print_section "Deploying Legend Platform"
    
    # Order matters - deploy dependencies first
    local services=(
        "mongodb"
        "legend-engine"
        "legend-sdlc"
        "legend-studio"
        "legend-guardian"
    )
    
    for service in "${services[@]}"; do
        deploy_service "$service"
        sleep 5  # Give service time to start
    done
    
    print_success "All services deployed!"
}

# Function to validate all services
validate_all() {
    print_section "Validating All Services"
    
    local services=(
        "mongodb"
        "legend-engine"
        "legend-sdlc"
        "legend-studio"
        "legend-guardian"
    )
    
    local all_valid=true
    
    for service in "${services[@]}"; do
        if ! validate_service "$service"; then
            all_valid=false
        fi
    done
    
    if [ "$all_valid" = true ]; then
        print_success "All services validated successfully!"
    else
        print_error "Some services failed validation"
        exit 1
    fi
}

# Function to clean up all services
cleanup_all() {
    print_section "Cleaning Up Legend Platform"
    
    print_warning "This will remove all Legend services from namespace $K8S_NAMESPACE"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Clean up services in reverse order
        local services=(
            "legend-guardian"
            "legend-studio"
            "legend-sdlc"
            "legend-engine"
            "mongodb"
        )
        
        for service in "${services[@]}"; do
            local deploy_script="$SCRIPT_DIR/$service/deploy.sh"
            if [ -f "$deploy_script" ]; then
                print_status "Removing $service..."
                bash "$deploy_script" clean
            fi
        done
        
        # Optionally remove namespace
        read -p "Remove namespace $K8S_NAMESPACE? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kubectl delete namespace $K8S_NAMESPACE --ignore-not-found=true
        fi
        
        print_success "Cleanup complete!"
    else
        print_status "Cleanup cancelled"
    fi
}

# Main menu
show_menu() {
    echo "========================================="
    echo "   Legend Platform Deployment Manager"
    echo "========================================="
    echo ""
    echo "1) Deploy all services"
    echo "2) Deploy specific service"
    echo "3) Validate all services"
    echo "4) Show status"
    echo "5) Clean up all"
    echo "6) Exit"
    echo ""
}

# Interactive mode
interactive_mode() {
    while true; do
        show_menu
        read -p "Select option: " choice
        
        case $choice in
            1)
                check_deployment_prerequisites
                create_namespace
                deploy_all
                validate_all
                show_status
                ;;
            2)
                echo "Available services:"
                echo "  - mongodb"
                echo "  - legend-engine"
                echo "  - legend-sdlc"
                echo "  - legend-studio"
                echo "  - legend-guardian"
                read -p "Enter service name: " service
                check_deployment_prerequisites
                create_namespace
                deploy_service "$service"
                ;;
            3)
                validate_all
                ;;
            4)
                show_status
                ;;
            5)
                cleanup_all
                ;;
            6)
                echo "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid option"
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Main execution
main() {
    case "${1:-menu}" in
        deploy)
            check_deployment_prerequisites
            create_namespace
            deploy_all
            validate_all
            show_status
            ;;
        validate)
            validate_all
            ;;
        status)
            show_status
            ;;
        clean|cleanup)
            cleanup_all
            ;;
        menu|interactive)
            interactive_mode
            ;;
        *)
            echo "Usage: $0 [deploy|validate|status|clean|menu]"
            echo "  deploy   - Deploy all services"
            echo "  validate - Validate all deployments"
            echo "  status   - Show current status"
            echo "  clean    - Remove all deployments"
            echo "  menu     - Interactive menu (default)"
            exit 1
            ;;
    esac
}

main "$@"