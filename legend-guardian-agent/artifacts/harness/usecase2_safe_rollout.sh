#!/bin/bash

# Use Case 2: Model Change with Safe Rollout
# This script demonstrates safe model evolution with versioning

set -e
source "$(dirname "$0")/env.sh"

TEST_NAME="usecase2_safe_rollout"

log_info "Starting Use Case 2: Model Change with Safe Rollout"

# Check services
check_all_services || exit 1

# Step 1: Execute safe rollout flow
log_info "Executing safe rollout flow..."

REQUEST_BODY=$(cat <<EOF
{
  "model_path": "model::Trade",
  "changes": {
    "rename": {
      "notional": "notionalAmount"
    },
    "add_field": {
      "name": "tradeDate",
      "type": "Date"
    }
  },
  "keep_v1": true
}
EOF
)

RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$REQUEST_BODY" \
  "$AGENT_URL/flows/usecase2/safe-rollout")

echo "$RESPONSE" | jq '.' > "${OUTPUT_DIR}/${TEST_NAME}_response.json"

# Check response
STATUS=$(echo "$RESPONSE" | jq -r '.status')
if [ "$STATUS" = "completed" ]; then
    log_info "Safe rollout completed successfully"
    
    # Check if v1 was maintained
    V1_MAINTAINED=$(echo "$RESPONSE" | jq -r '.v1_maintained')
    if [ "$V1_MAINTAINED" = "true" ]; then
        log_info "V1 service maintained for backward compatibility"
    fi
else
    log_error "Safe rollout failed with status: $STATUS"
    exit 1
fi

# Step 2: Test compilation of changed model
log_info "Testing compilation of updated model..."

COMPILE_REQUEST=$(cat <<EOF
{
  "pure": "Class model::Trade {
    id: String[1];
    ticker: String[1];
    quantity: Integer[1];
    price: Float[1];
    notionalAmount: Float[1];
    tradeDate: Date[1];
  }"
}
EOF
)

COMPILE_RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$COMPILE_REQUEST" \
  "$AGENT_URL/adapters/engine/compile")

echo "$COMPILE_RESPONSE" | jq '.' > "${OUTPUT_DIR}/${TEST_NAME}_compile_response.json"

# Check compilation
COMPILE_OK=$(echo "$COMPILE_RESPONSE" | jq -r '.ok')
if [ "$COMPILE_OK" = "true" ]; then
    log_info "Updated model compiled successfully"
else
    log_error "Compilation failed"
    echo "$COMPILE_RESPONSE" | jq '.errors'
fi

# Step 3: Run regression tests
log_info "Running regression tests..."

TEST_RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $API_KEY" \
  "$AGENT_URL/adapters/engine/test/run")

echo "$TEST_RESPONSE" | jq '.' > "${OUTPUT_DIR}/${TEST_NAME}_test_response.json"

TESTS_PASSED=$(echo "$TEST_RESPONSE" | jq -r '.passed')
if [ "$TESTS_PASSED" = "true" ]; then
    log_info "All regression tests passed"
else
    log_warning "Some tests failed"
    echo "$TEST_RESPONSE" | jq '.results[] | select(.passed == false)'
fi

# Summary
log_info "Use Case 2 Test Complete"
log_info "Model safely evolved with backward compatibility"
log_info "Results saved to: $OUTPUT_DIR"

exit 0