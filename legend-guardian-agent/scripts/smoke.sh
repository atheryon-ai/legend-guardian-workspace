#!/bin/bash

# Smoke test script for Legend Guardian Agent

set -e

# Configuration
AGENT_URL="${AGENT_URL:-http://localhost:8000}"
API_KEY="${API_KEY:-demo-key}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local test_name=$1
    local endpoint=$2
    local method=${3:-GET}
    local data=${4:-}
    
    echo -n "Testing $test_name... "
    
    local curl_opts="-s -o /dev/null -w %{http_code}"
    curl_opts="$curl_opts -X $method"
    curl_opts="$curl_opts -H 'Authorization: Bearer $API_KEY'"
    
    if [ -n "$data" ]; then
        curl_opts="$curl_opts -H 'Content-Type: application/json'"
        curl_opts="$curl_opts -d '$data'"
    fi
    
    local status_code=$(eval "curl $curl_opts '$AGENT_URL$endpoint'")
    
    if [ "$status_code" -ge 200 ] && [ "$status_code" -lt 300 ]; then
        echo -e "${GREEN}✓${NC} ($status_code)"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} ($status_code)"
        ((TESTS_FAILED++))
    fi
}

echo -e "${GREEN}Running smoke tests for Legend Guardian Agent${NC}"
echo "Target: $AGENT_URL"
echo ""

# Health checks
echo -e "${YELLOW}Health Checks:${NC}"
run_test "Main health endpoint" "/health"
run_test "Liveness probe" "/health/live"
run_test "Readiness probe" "/health/ready"

# API endpoints
echo -e "\n${YELLOW}API Endpoints:${NC}"
run_test "Root endpoint" "/"
run_test "OpenAPI spec" "/openapi.json"
run_test "Docs page" "/docs" GET

# Adapter endpoints
echo -e "\n${YELLOW}Adapter Endpoints:${NC}"
run_test "Engine info" "/adapters/engine/info"
run_test "SDLC projects" "/adapters/sdlc/projects"
run_test "Depot projects" "/adapters/depot/projects"

# Intent validation
echo -e "\n${YELLOW}Intent Processing:${NC}"
INTENT_DATA='{"prompt":"test","execute":false}'
run_test "Intent validation" "/intent/validate" POST "$INTENT_DATA"

# Compilation test
echo -e "\n${YELLOW}Compilation:${NC}"
COMPILE_DATA='{"pure":"Class test::Model {}"}'
run_test "PURE compilation" "/adapters/engine/compile" POST "$COMPILE_DATA"

# Summary
echo -e "\n${YELLOW}=================${NC}"
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
else
    echo -e "${GREEN}Tests Failed: $TESTS_FAILED${NC}"
fi

# Exit code
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "\n${RED}Smoke tests FAILED${NC}"
    exit 1
else
    echo -e "\n${GREEN}All smoke tests PASSED${NC}"
    exit 0
fi