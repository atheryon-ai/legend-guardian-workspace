#!/bin/bash

# Process Kubernetes Manifests with Environment Variables
# This script replaces environment variable placeholders in K8s manifests

set -e

# Load environment variables
ENV_FILE="$(dirname "$0")/azure-legend.env"
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
else
    echo "❌ azure-legend.env file not found. Please create it from azure-legend.env.example"
    exit 1
fi

# Load secrets if available (from parent directory)
if [ -f "$(dirname "$0")/../secrets.env" ]; then
    echo "🔐 Loading secrets from secrets.env..."
    source "$(dirname "$0")/../secrets.env"
elif [ -f "$(dirname "$0")/../.env.local" ]; then
    echo "🔐 Loading secrets from .env.local..."
    source "$(dirname "$0")/../.env.local"
else
    echo "⚠️  No secrets file found. Using placeholder values from azure-legend.env"
fi

echo "🔧 Processing Kubernetes manifests with environment variables..."

# Create processed manifests directory
SCRIPT_DIR="$(dirname "$0")"
mkdir -p "$SCRIPT_DIR/processed"

# Function to process a manifest file
process_manifest() {
    local input_file="$1"
    local output_file="$SCRIPT_DIR/processed/$(basename "$input_file")"
    
    echo "Processing: $input_file -> $output_file"
    
    # Create a copy of the file
    cp "$input_file" "$output_file"
    
    # Replace environment variables
    sed -i "s/\${K8S_NAMESPACE}/$K8S_NAMESPACE/g" "$output_file"
    sed -i "s/\${LEGEND_ENGINE_URL}/$LEGEND_ENGINE_URL/g" "$output_file"
    sed -i "s/\${LEGEND_SDLC_URL}/$LEGEND_SDLC_URL/g" "$output_file"
    sed -i "s/\${LEGEND_STUDIO_URL}/$LEGEND_STUDIO_URL/g" "$output_file"
    sed -i "s/\${MONGODB_URI}/$MONGODB_URI/g" "$output_file"
    sed -i "s/\${MONGODB_NAME}/$MONGODB_NAME/g" "$output_file"
    sed -i "s/\${MONGODB_SESSION_ENABLED}/$MONGODB_SESSION_ENABLED/g" "$output_file"
    sed -i "s/\${MONGODB_SESSION_STORE}/$MONGODB_SESSION_STORE/g" "$output_file"
    sed -i "s/\${MONGODB_SESSION_COLLECTION}/$MONGODB_SESSION_COLLECTION/g" "$output_file"
    sed -i "s/\${LEGEND_ENGINE_PORT}/$LEGEND_ENGINE_PORT/g" "$output_file"
    sed -i "s/\${LEGEND_ENGINE_HOST}/$LEGEND_ENGINE_HOST/g" "$output_file"
    sed -i "s/\${LEGEND_SDLC_PORT}/$LEGEND_SDLC_PORT/g" "$output_file"
    sed -i "s/\${LEGEND_SDLC_HOST}/$LEGEND_SDLC_HOST/g" "$output_file"
    sed -i "s/\${METADATA_PURE_HOST}/$METADATA_PURE_HOST/g" "$output_file"
    sed -i "s/\${METADATA_PURE_PORT}/$METADATA_PURE_PORT/g" "$output_file"
    sed -i "s/\${METADATA_PURE_PATH}/$METADATA_PURE_PATH/g" "$output_file"
    sed -i "s/\${NODE_ENV}/$NODE_ENV/g" "$output_file"
    sed -i "s/\${LOG_LEVEL}/$LOG_LEVEL/g" "$output_file"
    sed -i "s/\${LEGEND_ENGINE_VERSION}/$LEGEND_ENGINE_VERSION/g" "$output_file"
    sed -i "s/\${ENGINE_MEMORY_REQUEST}/$ENGINE_MEMORY_REQUEST/g" "$output_file"
    sed -i "s/\${ENGINE_MEMORY_LIMIT}/$ENGINE_MEMORY_LIMIT/g" "$output_file"
    sed -i "s/\${ENGINE_CPU_REQUEST}/$ENGINE_CPU_REQUEST/g" "$output_file"
    sed -i "s/\${ENGINE_CPU_LIMIT}/$ENGINE_CPU_LIMIT/g" "$output_file"
    
    # Base64 encode GitLab secrets
    GITLAB_APP_ID_BASE64=$(echo -n "$GITLAB_APP_ID" | base64)
    GITLAB_APP_SECRET_BASE64=$(echo -n "$GITLAB_APP_SECRET" | base64)
    GITLAB_HOST_BASE64=$(echo -n "$GITLAB_HOST" | base64)
    
    sed -i "s/\${GITLAB_APP_ID_BASE64}/$GITLAB_APP_ID_BASE64/g" "$output_file"
    sed -i "s/\${GITLAB_APP_SECRET_BASE64}/$GITLAB_APP_SECRET_BASE64/g" "$output_file"
    sed -i "s/\${GITLAB_HOST_BASE64}/$GITLAB_HOST_BASE64/g" "$output_file"
}

# Process all manifest files
echo "📁 Processing manifest files..."
for manifest in k8s/*.yaml; do
    if [ -f "$manifest" ]; then
        process_manifest "$manifest"
    fi
done

echo "✅ Kubernetes manifests processed successfully!"
echo "📁 Processed manifests are in: k8s/processed/"
echo ""
echo "🚀 To deploy, use:"
echo "   kubectl apply -f k8s/processed/"
echo ""
echo "🔧 To apply individual manifests:"
echo "   kubectl apply -f k8s/processed/legend-namespace.yaml"
echo "   kubectl apply -f k8s/processed/legend-secrets.yaml"
echo "   kubectl apply -f k8s/processed/legend-engine.yaml"
echo "   kubectl apply -f k8s/processed/legend-sdlc.yaml"
echo "   kubectl apply -f k8s/processed/legend-studio.yaml"
