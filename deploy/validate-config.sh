#!/bin/bash

# =============================================================================
# CONFIGURATION VALIDATION SCRIPT
# =============================================================================
# This script validates that all required configuration is properly set
# and doesn't contain placeholder values.

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source common functions
source "$SCRIPT_DIR/lib/common-functions.sh"

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

validate_base_config() {
    print_section "Validating Base Configuration"
    
    # Load only base config
    source "$SCRIPT_DIR/base.env"
    
    local required_vars=(
        "LEGEND_ENGINE_VERSION"
        "LEGEND_SDLC_VERSION"
        "LEGEND_STUDIO_VERSION"
        "K8S_NAMESPACE"
        "MONGODB_NAME"
        "JAVA_OPTS_COMMON"
    )
    
    if validate_required_vars "${required_vars[@]}"; then
        print_success "Base configuration valid"
        return 0
    else
        print_error "Base configuration has issues"
        return 1
    fi
}

validate_azure_config() {
    print_section "Validating Azure Configuration"
    
    # Load full Azure config stack
    load_all_config "azure"
    
    local required_vars=(
        "AZURE_SUBSCRIPTION_ID"
        "AZURE_RESOURCE_GROUP"
        "AZURE_LOCATION"
        "AZURE_AKS_CLUSTER"
        "AZURE_ACR_NAME"
        "AZURE_ACR_LOGIN_SERVER"
        "AZURE_ACR_USERNAME"
        "AZURE_ACR_PASSWORD"
        "GITLAB_APP_ID"
        "GITLAB_APP_SECRET"
        "LEGEND_ENGINE_URL"
        "LEGEND_SDLC_URL"
        "LEGEND_STUDIO_URL"
    )
    
    if validate_required_vars "${required_vars[@]}"; then
        print_success "Azure configuration valid"
        return 0
    else
        print_error "Azure configuration has issues"
        print_status "Make sure to override placeholder values in secrets.env"
        return 1
    fi
}

validate_local_config() {
    print_section "Validating Local Configuration"
    
    # Load full local config stack
    load_all_config "local"
    
    local required_vars=(
        "LEGEND_ENGINE_PORT"
        "LEGEND_SDLC_PORT"
        "LEGEND_STUDIO_PORT"
        "MONGO_ROOT_USERNAME"
        "MONGO_ROOT_PASSWORD"
        "LEGEND_API_KEY"
    )
    
    if validate_required_vars "${required_vars[@]}"; then
        print_success "Local configuration valid"
        return 0
    else
        print_error "Local configuration has issues"
        return 1
    fi
}

check_secrets_file() {
    print_section "Checking Secrets File"
    
    local project_root="$(get_project_root)"
    
    if [ -f "$project_root/secrets.env" ]; then
        print_success "secrets.env exists"
        
        # Check if it's git-ignored
        if grep -q "secrets.env" "$project_root/.gitignore" 2>/dev/null; then
            print_success "secrets.env is git-ignored"
        else
            print_warning "secrets.env is NOT git-ignored! Add it to .gitignore"
        fi
    elif [ -f "$project_root/.env.local" ]; then
        print_success ".env.local exists"
        
        # Check if it's git-ignored
        if grep -q ".env.local" "$project_root/.gitignore" 2>/dev/null; then
            print_success ".env.local is git-ignored"
        else
            print_warning ".env.local is NOT git-ignored! Add it to .gitignore"
        fi
    else
        print_warning "No secrets file found"
        print_status "Create $project_root/secrets.env from secrets.example"
        return 1
    fi
    
    return 0
}

check_file_structure() {
    print_section "Checking File Structure"
    
    local deploy_dir="$SCRIPT_DIR"
    local all_good=true
    
    # Check for required files
    local required_files=(
        "base.env"
        "lib/common-functions.sh"
        "azure/azure.env"
        "local/local.env"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "$deploy_dir/$file" ]; then
            print_success "Found: $file"
        else
            print_error "Missing: $file"
            all_good=false
        fi
    done
    
    if [ "$all_good" = true ]; then
        print_success "File structure is correct"
        return 0
    else
        print_error "File structure has issues"
        return 1
    fi
}

show_configuration() {
    local env_name="$1"
    
    print_section "Current Configuration ($env_name)"
    
    load_all_config "$env_name"
    
    echo ""
    echo "Key Configuration Values:"
    echo "  Deployment Environment: $DEPLOYMENT_ENV"
    echo "  Kubernetes Namespace: $K8S_NAMESPACE"
    echo "  Legend Engine Version: $LEGEND_ENGINE_VERSION"
    echo "  Legend SDLC Version: $LEGEND_SDLC_VERSION"
    echo "  Legend Studio Version: $LEGEND_STUDIO_VERSION"
    echo "  Java Options: $JAVA_OPTS_COMMON"
    
    if [ "$env_name" = "azure" ]; then
        echo ""
        echo "Azure-specific:"
        echo "  Resource Group: $AZURE_RESOURCE_GROUP"
        echo "  Location: $AZURE_LOCATION"
        echo "  AKS Cluster: $AZURE_AKS_CLUSTER"
        echo "  ACR Name: $AZURE_ACR_NAME"
        echo "  Engine Memory: $ENGINE_MEMORY_LIMIT"
        echo "  Engine Replicas: $ENGINE_REPLICAS"
    elif [ "$env_name" = "local" ]; then
        echo ""
        echo "Local-specific:"
        echo "  Engine Port: $LEGEND_ENGINE_PORT"
        echo "  SDLC Port: $LEGEND_SDLC_PORT"
        echo "  Studio Port: $LEGEND_STUDIO_PORT"
        echo "  MongoDB User: $MONGO_ROOT_USERNAME"
        echo "  API Key: $LEGEND_API_KEY"
        echo "  Engine Memory: $ENGINE_MEMORY_LIMIT"
    fi
    
    echo ""
}

# =============================================================================
# MAIN MENU
# =============================================================================

show_menu() {
    echo "========================================="
    echo "   Configuration Validation Tool"
    echo "========================================="
    echo ""
    echo "1) Validate all configurations"
    echo "2) Validate base configuration"
    echo "3) Validate Azure configuration"
    echo "4) Validate local configuration"
    echo "5) Check secrets file"
    echo "6) Check file structure"
    echo "7) Show Azure configuration"
    echo "8) Show local configuration"
    echo "9) Exit"
    echo ""
}

validate_all() {
    local all_valid=true
    
    check_file_structure || all_valid=false
    echo ""
    
    validate_base_config || all_valid=false
    echo ""
    
    check_secrets_file || all_valid=false
    echo ""
    
    validate_local_config || all_valid=false
    echo ""
    
    validate_azure_config || all_valid=false
    echo ""
    
    if [ "$all_valid" = true ]; then
        print_success "All configurations are valid!"
    else
        print_error "Some configurations have issues. Please fix them before deploying."
    fi
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    case "${1:-menu}" in
        all)
            validate_all
            ;;
        base)
            validate_base_config
            ;;
        azure)
            validate_azure_config
            ;;
        local)
            validate_local_config
            ;;
        secrets)
            check_secrets_file
            ;;
        structure)
            check_file_structure
            ;;
        show-azure)
            show_configuration "azure"
            ;;
        show-local)
            show_configuration "local"
            ;;
        menu|interactive)
            while true; do
                show_menu
                read -p "Select option: " choice
                
                case $choice in
                    1) validate_all ;;
                    2) validate_base_config ;;
                    3) validate_azure_config ;;
                    4) validate_local_config ;;
                    5) check_secrets_file ;;
                    6) check_file_structure ;;
                    7) show_configuration "azure" ;;
                    8) show_configuration "local" ;;
                    9) 
                        echo "Goodbye!"
                        exit 0
                        ;;
                    *)
                        print_error "Invalid option"
                        ;;
                esac
                
                echo ""
                read -p "Press Enter to continue..."
                echo ""
            done
            ;;
        *)
            echo "Usage: $0 [all|base|azure|local|secrets|structure|show-azure|show-local|menu]"
            echo ""
            echo "Commands:"
            echo "  all          - Validate all configurations"
            echo "  base         - Validate base configuration"
            echo "  azure        - Validate Azure configuration"
            echo "  local        - Validate local configuration"
            echo "  secrets      - Check secrets file"
            echo "  structure    - Check file structure"
            echo "  show-azure   - Show Azure configuration values"
            echo "  show-local   - Show local configuration values"
            echo "  menu         - Interactive menu (default)"
            exit 1
            ;;
    esac
}

main "$@"