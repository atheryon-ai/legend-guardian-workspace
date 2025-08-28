#!/bin/bash

# Legend Guardian - FINOS Legend Deployment Script
# This script sources secrets and runs the official FINOS Legend deployment

set -e

echo "🚀 Starting FINOS Legend deployment..."

# Source the secrets file from the root directory
# Try multiple possible locations for backward compatibility
if [ -f "../../.env.local" ]; then
    SECRETS_FILE="../../.env.local"
elif [ -f "../../.env.docker" ]; then
    SECRETS_FILE="../../.env.docker"
elif [ -f "../../secrets.env" ]; then
    SECRETS_FILE="../../secrets.env"
else
    echo "❌ Error: No secrets file found (.env.local, .env.docker, or secrets.env)"
    echo "   Please run: deploy/secrets/setup.sh --env local"
    exit 1
fi

echo "📁 Loading secrets from $SECRETS_FILE"
source "$SECRETS_FILE"

# Verify required variables are set
if [ -z "$GITLAB_APP_ID" ] || [ -z "$GITLAB_APP_SECRET" ]; then
    echo "❌ Error: GITLAB_APP_ID or GITLAB_APP_SECRET not set in secrets.env"
    exit 1
fi

echo "✅ GitLab OAuth credentials loaded"
echo "   Host: $GITLAB_HOST"
echo "   App ID: ${GITLAB_APP_ID:0:8}..."

# Export variables for docker-compose
export GITLAB_APP_ID
export GITLAB_APP_SECRET
export GITLAB_HOST

# Fix Docker Compose project name (must be lowercase)
export COMPOSE_PROJECT_NAME=legend-guardian

# Run docker-compose with the specified profile
if [ $# -eq 0 ]; then
    echo "📋 Usage: $0 <profile> [docker-compose-args...]"
    echo "   Profiles: setup, engine, sdlc, studio, depot, query, postgres"
    echo "   Example: $0 studio up -d"
    exit 1
fi

PROFILE="$1"
shift

echo "🎯 Running profile: $PROFILE"
echo "📋 Command: docker-compose --profile $PROFILE $@"

# Run docker-compose with the profile
docker-compose --profile "$PROFILE" "$@"
