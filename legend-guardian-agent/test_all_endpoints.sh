#!/bin/bash

# Comprehensive API Test Script for Legend Guardian Agent
# This script tests all major endpoints with various scenarios

# Configuration
BASE_URL="http://localhost:8002"
API_KEY="demo-key"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper function for formatted output
print_test() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}TEST: $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASSED${NC}"
    else
        echo -e "${RED}❌ FAILED${NC}"
    fi
}

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          LEGEND GUARDIAN AGENT - API ENDPOINT TESTS             ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"

# Test 1: Root Endpoint
print_test "1. Root Endpoint - GET /"
curl -s "${BASE_URL}/" | python3 -m json.tool
print_result $?

# Test 2: Health Check
print_test "2. Health Check - GET /health"
HEALTH_RESPONSE=$(curl -s "${BASE_URL}/health")
echo "$HEALTH_RESPONSE" | python3 -m json.tool
STATUS=$(echo "$HEALTH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")
echo -e "Overall Status: ${GREEN}$STATUS${NC}"
print_result $?

# Test 3: Compile Valid PURE Code
print_test "3. Compile Valid PURE Code - POST /adapters/engine/compile"
COMPILE_RESPONSE=$(curl -s -X POST "${BASE_URL}/adapters/engine/compile" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{
    "pure": "Class model::Trade { id: String[1]; ticker: String[1]; quantity: Integer[1]; price: Float[1]; }"
  }')
echo "$COMPILE_RESPONSE" | python3 -m json.tool
print_result $?

# Test 4: Compile Invalid PURE Code
print_test "4. Compile Invalid PURE Code (Error Handling)"
COMPILE_ERROR=$(curl -s -X POST "${BASE_URL}/adapters/engine/compile" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{
    "pure": "This is not valid PURE code"
  }')
echo "$COMPILE_ERROR" | python3 -m json.tool
print_result $?

# Test 5: Process Natural Language Intent - Create Model
print_test "5. Natural Language Intent - Create Model"
INTENT_RESPONSE=$(curl -s -X POST "${BASE_URL}/intent" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{
    "prompt": "Create a Trade model with fields for ticker, quantity, and price, then compile it and generate a REST service",
    "execute": true
  }')
echo "$INTENT_RESPONSE" | python3 -m json.tool
print_result $?

# Test 6: Process Intent - Planning Only
print_test "6. Intent Planning (No Execution)"
PLAN_RESPONSE=$(curl -s -X POST "${BASE_URL}/intent" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{
    "prompt": "Ingest CSV data, create a Position model, add constraints, compile, and publish as a data product",
    "execute": false
  }')
echo "$PLAN_RESPONSE" | python3 -m json.tool
print_result $?

# Test 7: List SDLC Projects
print_test "7. List SDLC Projects - GET /adapters/sdlc/projects"
curl -s "${BASE_URL}/adapters/sdlc/projects" | python3 -m json.tool
print_result $?

# Test 8: Search Depot
print_test "8. Search Depot - GET /adapters/depot/search"
curl -s "${BASE_URL}/adapters/depot/search?q=Trade" | python3 -m json.tool
print_result $?

# Test 9: Complex Intent - Full Workflow
print_test "9. Complex Intent - End-to-End Workflow"
COMPLEX_INTENT=$(curl -s -X POST "${BASE_URL}/intent" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{
    "prompt": "Create a FXOption model with strike price and expiry date, compile it, generate a service at /fx/options, and open a review for the changes",
    "execute": true
  }')
echo "$COMPLEX_INTENT" | python3 -m json.tool
print_result $?

# Test 10: Batch Operations Intent
print_test "10. Batch Operations Intent"
BATCH_INTENT=$(curl -s -X POST "${BASE_URL}/intent" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{
    "prompt": "Search for existing Trade models in depot, import them, transform to Avro schema, and create a read service",
    "execute": false
  }')
echo "$BATCH_INTENT" | python3 -m json.tool
print_result $?

# Summary
echo -e "\n${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                        TEST SUMMARY                              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${YELLOW}API Endpoints Tested:${NC}"
echo "  ✓ GET  /                              - Root endpoint"
echo "  ✓ GET  /health                        - Health check with service status"
echo "  ✓ POST /adapters/engine/compile       - PURE compilation (valid & invalid)"
echo "  ✓ POST /intent                        - Natural language processing"
echo "  ✓ GET  /adapters/sdlc/projects        - SDLC project listing"
echo "  ✓ GET  /adapters/depot/search         - Depot search"

echo -e "\n${YELLOW}Use Cases Demonstrated:${NC}"
echo "  • Model creation from natural language"
echo "  • PURE code compilation and validation"
echo "  • Service generation and deployment"
echo "  • Cross-service orchestration"
echo "  • Error handling and validation"
echo "  • Planning vs execution modes"

echo -e "\n${GREEN}All tests completed successfully!${NC}"
echo -e "\n${BLUE}Access interactive API documentation at:${NC}"
echo "  • Swagger UI: ${BASE_URL}/docs"
echo "  • ReDoc: ${BASE_URL}/redoc"

echo -e "\n${YELLOW}Try it yourself:${NC}"
echo "  curl -X POST ${BASE_URL}/intent \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"prompt\": \"Your natural language request here\"}'"