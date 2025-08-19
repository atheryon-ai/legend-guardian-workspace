#!/bin/bash

# Legend Platform Secrets Setup Script
# This script helps you set up your secrets for deployment

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
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

echo "🔐 Legend Platform Secrets Setup"
echo "================================="
echo ""

# Check if secrets file exists
if [ -f "$SCRIPT_DIR/../secrets.env" ]; then
    print_success "Found secrets.env file"
    SECRETS_FILE="$SCRIPT_DIR/../secrets.env"
elif [ -f "$SCRIPT_DIR/../.env.local" ]; then
    print_success "Found .env.local file"
    SECRETS_FILE="$SCRIPT_DIR/../.env.local"
else
    print_warning "No secrets file found. Creating secrets.env..."
    SECRETS_FILE="$SCRIPT_DIR/../secrets.env"
    
    # Create secrets file from template
    if [ -f "$SCRIPT_DIR/../secrets.example" ]; then
        cp "$SCRIPT_DIR/../secrets.example" "$SECRETS_FILE"
        print_status "Created secrets.env from template"
    else
        print_error "No secrets.example template found"
        exit 1
    fi
fi

print_section "Secrets Configuration"
echo ""
echo "Your secrets file is located at: $SECRETS_FILE"
echo ""
echo "Please edit this file with your real values:"
echo ""

# Show what needs to be configured
echo "Required secrets to configure:"
echo "  🔑 Azure Subscription ID"
echo "  🔑 Azure Resource Group"
echo "  🔑 Azure Container Registry credentials"
echo "  🔑 GitLab OAuth credentials"
echo "  🔑 Domain names for your services"
echo ""

# Check if secrets are configured
print_status "Checking current configuration..."

# Source the secrets file to check values
source "$SECRETS_FILE"

# Check Azure configuration
if [[ "$AZURE_SUBSCRIPTION_ID" == "your-subscription-id" ]]; then
    print_warning "Azure Subscription ID not configured"
else
    print_success "Azure Subscription ID: $AZURE_SUBSCRIPTION_ID"
fi

if [[ "$AZURE_ACR_PASSWORD" == "your-acr-password" ]]; then
    print_warning "Azure Container Registry password not configured"
else
    print_success "Azure Container Registry password configured"
fi

# Check GitLab configuration
if [[ "$GITLAB_APP_SECRET" == "your-gitlab-app-secret" ]]; then
    print_warning "GitLab OAuth secret not configured"
else
    print_success "GitLab OAuth secret configured"
fi

# Check domain configuration
if [[ "$LEGEND_ENGINE_URL" == *"your-domain.com"* ]]; then
    print_warning "Domain names not configured"
else
    print_success "Domain names configured"
fi

echo ""
print_section "Next Steps"
echo ""
echo "1. Edit your secrets file:"
echo "   nano $SECRETS_FILE"
echo ""
echo "2. Configure the following values:"
echo "   - Replace 'your-subscription-id' with your Azure subscription ID"
echo "   - Replace 'your-acr-password' with your Azure Container Registry password"
echo "   - Replace 'your-gitlab-app-secret' with your GitLab OAuth secret"
echo "   - Replace 'your-domain.com' with your actual domain names"
echo ""
echo "3. Test your configuration:"
echo "   cd deploy"
echo "   ./deploy-all.sh status"
echo ""
echo "4. Deploy when ready:"
echo "   ./deploy-all.sh deploy"
echo ""

# Check if .gitignore includes secrets
if grep -q "secrets.env\|\.env.local" "$SCRIPT_DIR/../.gitignore"; then
    print_success "Secrets files are properly git-ignored"
else
    print_warning "Secrets files may not be git-ignored. Check .gitignore"
fi

print_success "Secrets setup complete!"
echo ""
echo "Remember: Never commit your secrets.env file to git!"
