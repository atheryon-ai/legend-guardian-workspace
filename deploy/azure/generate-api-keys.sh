#!/bin/bash

# Legend Guardian Agent - API Key Generation Script
# This script helps you generate and encode API keys for deployment

set -e

echo "🔑 Legend Guardian Agent - API Key Generation"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "This script will help you generate API keys for your Legend Guardian Agent deployment."
echo ""

# Step 1: Legend Platform API Key
echo "Step 1: Legend Platform API Key"
echo "--------------------------------"
echo "This key allows the Guardian Agent to access your Legend Engine and SDLC services."
echo ""
echo "You need to get this from your Legend platform:"
echo "1. Log into Legend Studio: http://52.186.106.13/studio/"
echo "2. Go to Settings → API Keys or Access Tokens"
echo "3. Generate a new API key for the Guardian Agent"
echo "4. Copy the generated key"
echo ""

read -p "Enter your Legend Platform API Key: " LEGEND_API_KEY

if [ -z "$LEGEND_API_KEY" ]; then
    print_warning "No Legend API key provided. Using placeholder."
    LEGEND_API_KEY="your-actual-legend-api-key"
fi

# Step 2: External API Keys
echo ""
echo "Step 2: External API Keys"
echo "-------------------------"
echo "These keys allow external clients to access the Guardian Agent API."
echo ""

read -p "Enter External API Key 1 (or press Enter for default): " EXTERNAL_KEY_1
read -p "Enter External API Key 2 (or press Enter for default): " EXTERNAL_KEY_2
read -p "Enter External API Key 3 (or press Enter for default): " EXTERNAL_KEY_3

# Set defaults if not provided
EXTERNAL_KEY_1=${EXTERNAL_KEY_1:-"azure-key-1"}
EXTERNAL_KEY_2=${EXTERNAL_KEY_2:-"azure-key-2"}
EXTERNAL_KEY_3=${EXTERNAL_KEY_3:-"azure-key-3"}

# Encode the keys
print_info "Encoding API keys..."
LEGEND_API_KEY_ENCODED=$(echo -n "$LEGEND_API_KEY" | base64)
EXTERNAL_KEY_1_ENCODED=$(echo -n "$EXTERNAL_KEY_1" | base64)
EXTERNAL_KEY_2_ENCODED=$(echo -n "$EXTERNAL_KEY_2" | base64)
EXTERNAL_KEY_3_ENCODED=$(echo -n "$EXTERNAL_KEY_3" | base64)

# Create the secrets file
print_info "Creating Kubernetes secrets file..."

cat > k8s/legend-guardian-secrets.yaml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: legend-guardian-secrets
  namespace: legend
type: Opaque
data:
  # Legend Platform API Key
  api-key: "${LEGEND_API_KEY_ENCODED}"
  
  # Guardian Agent API Keys (for external access)
  external-api-key-1: "${EXTERNAL_KEY_1_ENCODED}"
  external-api-key-2: "${EXTERNAL_KEY_2_ENCODED}"
  external-api-key-3: "${EXTERNAL_KEY_3_ENCODED}"
EOF

print_success "Kubernetes secrets file created: k8s/legend-guardian-secrets.yaml"

# Create .env file for local development
print_info "Creating local .env file..."

cat > ../.env << EOF
# Legend Platform Configuration
LEGEND_ENGINE_URL=http://52.186.106.13:6060
LEGEND_SDLC_URL=http://52.186.106.13:7070
LEGEND_API_KEY=${LEGEND_API_KEY}

# API Configuration
LEGEND_API_HOST=0.0.0.0
LEGEND_API_PORT=8000
LEGEND_API_DEBUG=false

# Security
VALID_API_KEYS=${EXTERNAL_KEY_1},${EXTERNAL_KEY_2},${EXTERNAL_KEY_3}

# Logging
LEGEND_LOG_LEVEL=INFO
EOF

print_success "Local .env file created: ../.env"

# Display summary
echo ""
echo "📋 API Key Summary"
echo "=================="
echo "Legend Platform API Key: ${LEGEND_API_KEY}"
echo "External API Key 1: ${EXTERNAL_KEY_1}"
echo "External API Key 2: ${EXTERNAL_KEY_2}"
echo "External API Key 3: ${EXTERNAL_KEY_3}"
echo ""
echo "🔐 Next Steps:"
echo "1. Apply the secrets to Kubernetes: kubectl apply -f k8s/legend-guardian-secrets.yaml"
echo "2. Deploy the Guardian Agent: ./deploy-guardian-agent.sh"
echo "3. Test with one of the external API keys"
echo ""
echo "Example test:"
echo "curl -H 'Authorization: Bearer ${EXTERNAL_KEY_1}' http://localhost:8000/health"
