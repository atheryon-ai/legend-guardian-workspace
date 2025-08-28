#!/bin/bash

# Legend Platform Secrets Setup Script
# Interactive and secure configuration for all environments

set -e

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Output functions
print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_section() { echo -e "\n${BLUE}═══════════════════════════════════════${NC}"; echo -e "${BLUE}  $1${NC}"; echo -e "${BLUE}═══════════════════════════════════════${NC}"; }
print_prompt() { echo -e "${CYAN}[?]${NC} $1"; }

# Default values
DEFAULT_ENV="local"
INTERACTIVE=false
VALIDATE_ONLY=false
ENVIRONMENT=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --interactive|-i)
            INTERACTIVE=true
            shift
            ;;
        --validate|-v)
            VALIDATE_ONLY=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --env <env>      Environment to configure (local, docker, azure)"
            echo "  --interactive    Run in interactive mode"
            echo "  --validate       Validate existing configuration only"
            echo "  --help           Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --env local            Configure local environment"
            echo "  $0 --interactive          Interactive setup wizard"
            echo "  $0 --validate --env azure Validate Azure configuration"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Set default environment if not specified
if [ -z "$ENVIRONMENT" ]; then
    ENVIRONMENT="$DEFAULT_ENV"
fi

# Header
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║     🔐 Legend Platform Secrets Setup Wizard 🔐       ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Validate environment
VALID_ENVS=("local" "docker" "azure" "k8s")
if [[ ! " ${VALID_ENVS[@]} " =~ " ${ENVIRONMENT} " ]]; then
    print_error "Invalid environment: $ENVIRONMENT"
    print_status "Valid environments: ${VALID_ENVS[*]}"
    exit 1
fi

# Set environment file paths
ENV_FILE="$REPO_ROOT/.env.$ENVIRONMENT"
TEMPLATE_FILE="$SCRIPT_DIR/.env.$ENVIRONMENT.example"
MAIN_TEMPLATE="$REPO_ROOT/.env.example"

# Validation mode
if [ "$VALIDATE_ONLY" = true ]; then
    print_section "Validating $ENVIRONMENT Configuration"
    
    if [ ! -f "$ENV_FILE" ]; then
        print_error "Configuration file not found: $ENV_FILE"
        exit 1
    fi
    
    # Source the environment file
    set -a
    source "$ENV_FILE"
    set +a
    
    # Validate GitLab OAuth
    print_status "Checking GitLab OAuth configuration..."
    if [[ -z "$GITLAB_APP_ID" ]] || [[ "$GITLAB_APP_ID" == *"<YOUR"* ]]; then
        print_error "GitLab Application ID not configured"
    else
        # Check if it's a hex string (not numeric)
        if [[ "$GITLAB_APP_ID" =~ ^[0-9]+$ ]]; then
            print_error "GitLab Application ID appears to be numeric. Use the hex Application ID instead!"
        else
            print_success "GitLab Application ID configured (${#GITLAB_APP_ID} characters)"
        fi
    fi
    
    if [[ -z "$GITLAB_APP_SECRET" ]] || [[ "$GITLAB_APP_SECRET" == *"<YOUR"* ]]; then
        print_error "GitLab Application Secret not configured"
    else
        print_success "GitLab Application Secret configured"
    fi
    
    # Environment-specific validation
    case $ENVIRONMENT in
        azure)
            print_status "Checking Azure configuration..."
            if [[ -z "$AZURE_SUBSCRIPTION_ID" ]] || [[ "$AZURE_SUBSCRIPTION_ID" == *"<YOUR"* ]]; then
                print_error "Azure Subscription ID not configured"
            else
                print_success "Azure Subscription ID configured"
            fi
            
            if [[ -z "$AZURE_ACR_PASSWORD" ]] || [[ "$AZURE_ACR_PASSWORD" == *"<YOUR"* ]]; then
                print_error "Azure Container Registry password not configured"
            else
                print_success "Azure Container Registry configured"
            fi
            ;;
        local|docker)
            print_status "Checking local MongoDB configuration..."
            if [[ -z "$MONGODB_PASSWORD" ]] || [[ "$MONGODB_PASSWORD" == "changeme" ]]; then
                print_warning "Using default MongoDB password - consider changing for security"
            else
                print_success "MongoDB password configured"
            fi
            ;;
    esac
    
    print_section "Validation Complete"
    exit 0
fi

# Interactive mode
if [ "$INTERACTIVE" = true ]; then
    print_section "Interactive Setup Mode"
    
    # Select environment
    echo ""
    print_prompt "Select deployment environment:"
    echo "  1) Local Development"
    echo "  2) Docker Compose"
    echo "  3) Azure (AKS)"
    echo "  4) Kubernetes (Generic)"
    echo ""
    read -p "Enter choice [1-4]: " env_choice
    
    case $env_choice in
        1) ENVIRONMENT="local" ;;
        2) ENVIRONMENT="docker" ;;
        3) ENVIRONMENT="azure" ;;
        4) ENVIRONMENT="k8s" ;;
        *) print_error "Invalid choice"; exit 1 ;;
    esac
    
    ENV_FILE="$REPO_ROOT/.env.$ENVIRONMENT"
fi

# Create environment file from template
print_section "Setting up $ENVIRONMENT Environment"

if [ -f "$ENV_FILE" ]; then
    print_warning "Configuration file already exists: $ENV_FILE"
    read -p "Overwrite existing configuration? (y/N): " overwrite
    if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
        print_status "Keeping existing configuration"
        exit 0
    fi
fi

# Copy appropriate template
if [ -f "$TEMPLATE_FILE" ]; then
    cp "$TEMPLATE_FILE" "$ENV_FILE"
    print_success "Created $ENV_FILE from template"
elif [ -f "$MAIN_TEMPLATE" ]; then
    cp "$MAIN_TEMPLATE" "$ENV_FILE"
    print_success "Created $ENV_FILE from main template"
else
    print_error "No template found for $ENVIRONMENT"
    exit 1
fi

# Interactive configuration
if [ "$INTERACTIVE" = true ]; then
    print_section "GitLab OAuth Configuration"
    
    echo ""
    echo "Create a GitLab OAuth application at:"
    echo "https://gitlab.com/-/profile/applications"
    echo ""
    echo "Important:"
    echo "  - Check 'Confidential' checkbox"
    echo "  - Select scopes: api, openid, profile"
    echo "  - Add redirect URIs for your environment"
    echo ""
    
    read -p "Enter GitLab Application ID (hex string): " gitlab_app_id
    read -s -p "Enter GitLab Application Secret: " gitlab_app_secret
    echo ""
    read -p "Enter GitLab Host [gitlab.com]: " gitlab_host
    gitlab_host=${gitlab_host:-gitlab.com}
    
    # Update configuration file
    sed -i.bak "s|<YOUR-GITLAB-APP-ID>|$gitlab_app_id|g" "$ENV_FILE"
    sed -i.bak "s|<YOUR-GITLAB-APPLICATION-ID-HEX-STRING>|$gitlab_app_id|g" "$ENV_FILE"
    sed -i.bak "s|<YOUR-GITLAB-SECRET>|$gitlab_app_secret|g" "$ENV_FILE"
    sed -i.bak "s|<YOUR-GITLAB-APP-SECRET>|$gitlab_app_secret|g" "$ENV_FILE"
    sed -i.bak "s|gitlab.com|$gitlab_host|g" "$ENV_FILE"
    
    # Environment-specific configuration
    if [ "$ENVIRONMENT" = "azure" ]; then
        print_section "Azure Configuration"
        
        read -p "Enter Azure Subscription ID: " azure_sub_id
        read -p "Enter Azure Resource Group: " azure_rg
        read -p "Enter Azure ACR Name: " azure_acr
        read -s -p "Enter Azure ACR Password: " azure_acr_pwd
        echo ""
        read -p "Enter your domain (e.g., example.com): " domain
        
        sed -i.bak "s|<YOUR-SUBSCRIPTION-ID>|$azure_sub_id|g" "$ENV_FILE"
        sed -i.bak "s|<YOUR-RESOURCE-GROUP>|$azure_rg|g" "$ENV_FILE"
        sed -i.bak "s|<YOUR-ACR-NAME>|$azure_acr|g" "$ENV_FILE"
        sed -i.bak "s|<YOUR-ACR-PASSWORD>|$azure_acr_pwd|g" "$ENV_FILE"
        sed -i.bak "s|<YOUR-DOMAIN>|$domain|g" "$ENV_FILE"
    fi
    
    # Clean up backup files
    rm -f "$ENV_FILE.bak"
fi

# Check .gitignore
print_section "Security Check"

GITIGNORE_FILE="$REPO_ROOT/.gitignore"
FILES_TO_IGNORE=(".env.local" ".env.docker" ".env.azure" ".env.k8s" "secrets.env")

for file in "${FILES_TO_IGNORE[@]}"; do
    if ! grep -q "^$file$" "$GITIGNORE_FILE" 2>/dev/null; then
        echo "$file" >> "$GITIGNORE_FILE"
        print_status "Added $file to .gitignore"
    fi
done

print_success "Security check complete - secrets are gitignored"

# Final instructions
print_section "Setup Complete!"

echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Review and edit your configuration:"
echo "   ${CYAN}nano $ENV_FILE${NC}"
echo ""
echo "2. Validate your configuration:"
echo "   ${CYAN}$0 --validate --env $ENVIRONMENT${NC}"
echo ""
echo "3. Deploy Legend Platform:"
case $ENVIRONMENT in
    local|docker)
        echo "   ${CYAN}cd $REPO_ROOT/deploy/docker-finos-official${NC}"
        echo "   ${CYAN}./run-legend.sh studio up -d${NC}"
        ;;
    azure)
        echo "   ${CYAN}cd $REPO_ROOT/deploy/k8s-azure${NC}"
        echo "   ${CYAN}./deploy.sh${NC}"
        ;;
    k8s)
        echo "   ${CYAN}kubectl apply -k $REPO_ROOT/deploy/k8s/${NC}"
        ;;
esac
echo ""
echo "⚠️  Remember: NEVER commit files with real secrets to git!"
echo ""
print_success "Configuration saved to: $ENV_FILE"