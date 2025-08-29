#!/bin/bash

# Test Harness Environment Configuration
# Source this file before running test scripts: source env.sh

# Service URLs
export ENGINE_URL="${ENGINE_URL:-http://localhost:6300}"
export SDLC_URL="${SDLC_URL:-http://localhost:6100}"
export DEPOT_URL="${DEPOT_URL:-http://localhost:6200}"
export STUDIO_URL="${STUDIO_URL:-http://localhost:9000}"
export AGENT_URL="${AGENT_URL:-http://localhost:8000}"

# Authentication
export API_KEY="${API_KEY:-demo-key}"

# Project Configuration
export PROJECT_ID="${PROJECT_ID:-demo-project}"
export WORKSPACE_ID="${WORKSPACE_ID:-terry-dev}"
export SERVICE_PATH="${SERVICE_PATH:-trades/byNotional}"

# Output Configuration
export OUTPUT_DIR="${OUTPUT_DIR:-./outputs}"
export VERBOSE="${VERBOSE:-false}"

# Colors for output
export RED='\033[0;31m'
export GREEN='\033[0;32m'
export YELLOW='\033[1;33m'
export NC='\033[0m' # No Color

# Helper Functions

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

check_service() {
    local service_name=$1
    local service_url=$2
    local health_path=${3:-/health}
    
    log_info "Checking $service_name at $service_url"
    
    if curl -s -f -o /dev/null "$service_url$health_path"; then
        log_info "$service_name is healthy"
        return 0
    else
        log_error "$service_name is not responding"
        return 1
    fi
}

check_all_services() {
    log_info "Checking all services..."
    
    local all_healthy=true
    
    check_service "Legend Engine" "$ENGINE_URL" "/api/server/v1/info" || all_healthy=false
    check_service "Legend SDLC" "$SDLC_URL" "/api/info" || all_healthy=false
    check_service "Legend Depot" "$DEPOT_URL" "/api/info" || all_healthy=false
    check_service "Guardian Agent" "$AGENT_URL" "/health" || all_healthy=false
    
    if [ "$all_healthy" = true ]; then
        log_info "All services are healthy"
        return 0
    else
        log_error "Some services are not healthy"
        return 1
    fi
}

make_request() {
    local method=$1
    local url=$2
    local data=${3:-}
    local output_file=${4:-}
    
    if [ "$VERBOSE" = "true" ]; then
        log_info "Making $method request to $url"
        [ -n "$data" ] && log_info "Request body: $data"
    fi
    
    local curl_opts="-s -X $method"
    curl_opts="$curl_opts -H 'Authorization: Bearer $API_KEY'"
    curl_opts="$curl_opts -H 'Content-Type: application/json'"
    
    if [ -n "$data" ]; then
        curl_opts="$curl_opts -d '$data'"
    fi
    
    if [ -n "$output_file" ]; then
        eval "curl $curl_opts '$url' | jq '.' > '$output_file'"
    else
        eval "curl $curl_opts '$url' | jq '.'"
    fi
}

ensure_output_dir() {
    mkdir -p "$OUTPUT_DIR"
}

save_output() {
    local test_name=$1
    local content=$2
    local filename="${OUTPUT_DIR}/${test_name}_$(date +%Y%m%d_%H%M%S).json"
    
    echo "$content" > "$filename"
    log_info "Output saved to $filename"
}

# Initialize
ensure_output_dir

# Print configuration
log_info "Test Harness Environment Loaded"
log_info "Agent URL: $AGENT_URL"
log_info "Project ID: $PROJECT_ID"
log_info "Workspace ID: $WORKSPACE_ID"