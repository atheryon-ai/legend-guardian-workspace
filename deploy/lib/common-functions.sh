#!/bin/bash

# =============================================================================
# COMMON FUNCTIONS LIBRARY
# =============================================================================
# This file contains shared functions used across all deployment scripts.
# Source this file at the beginning of your scripts:
#   source "$(dirname "$0")/lib/common-functions.sh"

# =============================================================================
# COLOR OUTPUT FUNCTIONS
# =============================================================================
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_section() { echo -e "${BLUE}========== $1 ==========${NC}"; }

# =============================================================================
# CONFIGURATION LOADING FUNCTIONS
# =============================================================================

# Function to get the deploy directory (parent of lib)
get_deploy_dir() {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
}

# Function to get the project root directory
get_project_root() {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
}

# Function to load base configuration
load_base_config() {
    local deploy_dir="$(get_deploy_dir)"
    local base_env="$deploy_dir/base.env"
    
    if [ -f "$base_env" ]; then
        print_status "Loading base configuration..."
        source "$base_env"
    else
        print_error "Base configuration not found at $base_env"
        exit 1
    fi
}

# Function to load environment-specific configuration
load_env_config() {
    local env_name="$1"
    local deploy_dir="$(get_deploy_dir)"
    local env_file=""
    
    case "$env_name" in
        azure)
            env_file="$deploy_dir/azure/azure.env"
            ;;
        local)
            env_file="$deploy_dir/local/local.env"
            ;;
        *)
            print_warning "Unknown environment: $env_name"
            return 1
            ;;
    esac
    
    if [ -f "$env_file" ]; then
        print_status "Loading $env_name configuration..."
        source "$env_file"
        export DEPLOYMENT_ENV="$env_name"
    else
        print_warning "$env_name configuration not found at $env_file"
    fi
}

# Function to load secrets (standardized location)
load_secrets() {
    local project_root="$(get_project_root)"
    local secrets_loaded=false
    
    # Check for secrets.env in project root
    if [ -f "$project_root/secrets.env" ]; then
        print_status "Loading secrets from secrets.env..."
        source "$project_root/secrets.env"
        secrets_loaded=true
    # Check for .env.local as alternative
    elif [ -f "$project_root/.env.local" ]; then
        print_status "Loading secrets from .env.local..."
        source "$project_root/.env.local"
        secrets_loaded=true
    fi
    
    if [ "$secrets_loaded" = false ]; then
        print_warning "No secrets file found in project root."
        print_warning "Please create $project_root/secrets.env from secrets.example"
        return 1
    fi
    
    return 0
}

# Function to load all configuration in order
load_all_config() {
    local env_name="${1:-local}"
    
    # Load in order: base -> environment-specific -> secrets
    load_base_config
    load_env_config "$env_name"
    load_secrets || true  # Don't exit if secrets not found, just warn
}

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

# Function to check if a variable contains a placeholder value
is_placeholder() {
    local value="$1"
    if [[ "$value" == *"your-"* ]] || [[ "$value" == *"[PASSWORD]"* ]] || [[ "$value" == *"[UNIQUE_SUFFIX]"* ]]; then
        return 0
    fi
    return 1
}

# Function to validate required variables
validate_required_vars() {
    local vars=("$@")
    local missing_vars=()
    local placeholder_vars=()
    
    for var in "${vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        elif is_placeholder "${!var}"; then
            placeholder_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        print_error "Missing required variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
    fi
    
    if [ ${#placeholder_vars[@]} -gt 0 ]; then
        print_warning "Variables with placeholder values:"
        for var in "${placeholder_vars[@]}"; do
            echo "  - $var = ${!var}"
        done
    fi
    
    if [ ${#missing_vars[@]} -gt 0 ] || [ ${#placeholder_vars[@]} -gt 0 ]; then
        return 1
    fi
    
    return 0
}

# =============================================================================
# PREREQUISITE CHECK FUNCTIONS
# =============================================================================

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to check kubectl
check_kubectl() {
    if ! command_exists kubectl; then
        print_error "kubectl not installed"
        print_status "Install: https://kubernetes.io/docs/tasks/tools/"
        return 1
    fi
    
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Not connected to Kubernetes cluster"
        return 1
    fi
    
    print_success "kubectl connected to cluster"
    return 0
}

# Function to check Docker
check_docker() {
    if ! command_exists docker; then
        print_error "Docker not installed"
        print_status "Install: https://docs.docker.com/get-docker/"
        return 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running"
        return 1
    fi
    
    print_success "Docker is running"
    return 0
}

# Function to check Azure CLI
check_azure_cli() {
    if ! command_exists az; then
        print_error "Azure CLI not installed"
        print_status "Install: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        return 1
    fi
    
    print_success "Azure CLI installed"
    return 0
}

# Function to check all prerequisites based on environment
check_prerequisites() {
    local env_name="${1:-local}"
    
    print_section "Checking Prerequisites"
    
    case "$env_name" in
        azure)
            check_azure_cli || return 1
            check_kubectl || return 1
            ;;
        local)
            check_docker || return 1
            command_exists docker-compose || {
                print_error "Docker Compose not installed"
                return 1
            }
            ;;
        k8s|kubernetes)
            check_kubectl || return 1
            ;;
    esac
    
    # Check for envsubst (needed for template processing)
    if ! command_exists envsubst; then
        print_warning "envsubst not found. Installing..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install gettext
            brew link --force gettext
        else
            apt-get update && apt-get install -y gettext-base
        fi
    fi
    
    print_success "All prerequisites met"
    return 0
}

# =============================================================================
# KUBERNETES HELPER FUNCTIONS
# =============================================================================

# Function to create namespace if it doesn't exist
create_namespace() {
    local namespace="${1:-$K8S_NAMESPACE}"
    
    if ! kubectl get namespace "$namespace" &>/dev/null; then
        print_status "Creating namespace $namespace..."
        kubectl create namespace "$namespace"
    else
        print_status "Namespace $namespace already exists"
    fi
}

# Function to wait for deployment
wait_for_deployment() {
    local deployment="$1"
    local namespace="${2:-$K8S_NAMESPACE}"
    local timeout="${3:-300}"
    
    print_status "Waiting for $deployment to be ready..."
    kubectl wait --for=condition=available --timeout="${timeout}s" \
        "deployment/$deployment" -n "$namespace" || {
        print_warning "$deployment not ready after ${timeout}s"
        return 1
    }
    
    print_success "$deployment is ready"
    return 0
}

# Function to check pod status
check_pod_status() {
    local app_label="$1"
    local namespace="${2:-$K8S_NAMESPACE}"
    
    local pod_status=$(kubectl get pods -n "$namespace" -l "app=$app_label" \
        -o jsonpath='{.items[0].status.phase}' 2>/dev/null || echo "Not Found")
    
    if [ "$pod_status" = "Running" ]; then
        print_success "$app_label pod is running"
        return 0
    else
        print_error "$app_label pod status: $pod_status"
        return 1
    fi
}

# =============================================================================
# PORT CHECKING FUNCTIONS
# =============================================================================

# Function to check if port is available
check_port_available() {
    local port="$1"
    
    if lsof -Pi ":$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $port is already in use"
        return 1
    fi
    
    return 0
}

# Function to check multiple ports
check_ports_available() {
    local ports=("$@")
    local ports_in_use=()
    
    for port in "${ports[@]}"; do
        if ! check_port_available "$port"; then
            ports_in_use+=("$port")
        fi
    done
    
    if [ ${#ports_in_use[@]} -gt 0 ]; then
        print_warning "The following ports are in use: ${ports_in_use[*]}"
        return 1
    fi
    
    print_success "All required ports are available"
    return 0
}

# =============================================================================
# EXPORT FUNCTIONS FOR USE IN SCRIPTS
# =============================================================================
export -f print_status
export -f print_warning
export -f print_error
export -f print_success
export -f print_section
export -f get_deploy_dir
export -f get_project_root
export -f load_base_config
export -f load_env_config
export -f load_secrets
export -f load_all_config
export -f is_placeholder
export -f validate_required_vars
export -f command_exists
export -f check_kubectl
export -f check_docker
export -f check_azure_cli
export -f check_prerequisites
export -f create_namespace
export -f wait_for_deployment
export -f check_pod_status
export -f check_port_available
export -f check_ports_available