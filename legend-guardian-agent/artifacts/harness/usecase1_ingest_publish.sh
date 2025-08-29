#!/bin/bash

# Use Case 1: Ingest → Model → Map → Publish Service
# This script demonstrates the complete flow from CSV ingestion to service publication

set -e
source "$(dirname "$0")/env.sh"

TEST_NAME="usecase1_ingest_publish"

log_info "Starting Use Case 1: Ingest → Model → Map → Publish Service"

# Check services
check_all_services || exit 1

# Sample CSV data
CSV_DATA="id,ticker,quantity,price,notional
1,AAPL,100,150.50,15050.00
2,GOOGL,50,2800.00,140000.00
3,MSFT,75,380.25,28518.75"

# Step 1: Call the flow endpoint
log_info "Executing ingest and publish flow..."

REQUEST_BODY=$(cat <<EOF
{
  "csv_data": "$CSV_DATA",
  "model_name": "Trade",
  "service_path": "trades/byNotional",
  "mapping_name": "TradeMapping"
}
EOF
)

RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$REQUEST_BODY" \
  "$AGENT_URL/flows/usecase1/ingest-publish")

echo "$RESPONSE" | jq '.' > "${OUTPUT_DIR}/${TEST_NAME}_response.json"

# Check response status
STATUS=$(echo "$RESPONSE" | jq -r '.status')
if [ "$STATUS" = "completed" ]; then
    log_info "Flow completed successfully"
else
    log_error "Flow failed with status: $STATUS"
    exit 1
fi

# Step 2: Test the generated service
SERVICE_URL=$(echo "$RESPONSE" | jq -r '.service_url')
log_info "Testing generated service at: $SERVICE_URL"

# Query the service with parameters
SERVICE_RESPONSE=$(curl -s -X GET \
  -H "Authorization: Bearer $API_KEY" \
  "${SERVICE_URL}?minNotional=20000")

echo "$SERVICE_RESPONSE" | jq '.' > "${OUTPUT_DIR}/${TEST_NAME}_service_response.json"

# Step 3: Verify results
log_info "Verifying results..."

# Check if we got data back
if echo "$SERVICE_RESPONSE" | jq -e '. | length > 0' > /dev/null; then
    log_info "Service returned data successfully"
    
    # Count results
    COUNT=$(echo "$SERVICE_RESPONSE" | jq '. | length')
    log_info "Number of trades with notional > 20000: $COUNT"
    
    # Display summary
    echo "$SERVICE_RESPONSE" | jq '.[] | {ticker, notional}'
else
    log_warning "Service returned no data"
fi

# Step 4: Alternative - Use intent endpoint
log_info "Testing via natural language intent..."

INTENT_REQUEST=$(cat <<EOF
{
  "prompt": "Create a Trade model from CSV, compile it, and generate a service at trades/byNotional",
  "project_id": "$PROJECT_ID",
  "workspace_id": "${WORKSPACE_ID}_intent",
  "execute": true
}
EOF
)

INTENT_RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$INTENT_REQUEST" \
  "$AGENT_URL/intent")

echo "$INTENT_RESPONSE" | jq '.' > "${OUTPUT_DIR}/${TEST_NAME}_intent_response.json"

# Check intent execution
INTENT_STATUS=$(echo "$INTENT_RESPONSE" | jq -r '.status')
if [ "$INTENT_STATUS" = "completed" ]; then
    log_info "Intent execution completed"
    
    # Show plan steps
    log_info "Executed steps:"
    echo "$INTENT_RESPONSE" | jq -r '.plan[] | "\(.id): \(.action) - \(.status)"'
else
    log_warning "Intent execution status: $INTENT_STATUS"
fi

# Summary
log_info "Use Case 1 Test Complete"
log_info "Results saved to: $OUTPUT_DIR"
log_info "Key outputs:"
log_info "  - Flow response: ${TEST_NAME}_response.json"
log_info "  - Service response: ${TEST_NAME}_service_response.json"
log_info "  - Intent response: ${TEST_NAME}_intent_response.json"

# Exit with success
exit 0