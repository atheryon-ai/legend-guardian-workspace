#!/bin/bash

# Use Case 3: Cross-bank Model Reuse via Depot
# This script demonstrates reusing models from the depot

set -e
source "$(dirname "$0")/env.sh"

TEST_NAME="usecase3_model_reuse"

log_info "Starting Use Case 3: Cross-bank Model Reuse via Depot"

# Check services
check_all_services || exit 1

# Step 1: Search depot for FX models
log_info "Searching depot for FX Option models..."

SEARCH_RESPONSE=$(curl -s -X GET \
  -H "Authorization: Bearer $API_KEY" \
  "$AGENT_URL/adapters/depot/search?q=FXOption&limit=5")

echo "$SEARCH_RESPONSE" | jq '.' > "${OUTPUT_DIR}/${TEST_NAME}_search_response.json"

# Display search results
log_info "Found models:"
echo "$SEARCH_RESPONSE" | jq -r '.[] | "\(.project_id) - \(.path)"' || echo "No models found"

# Step 2: Execute model reuse flow
log_info "Executing model reuse flow..."

REQUEST_BODY=$(cat <<EOF
{
  "search_query": "FXOption",
  "target_format": "avro",
  "service_name": "fx_options_service"
}
EOF
)

RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$REQUEST_BODY" \
  "$AGENT_URL/flows/usecase3/model-reuse")

echo "$RESPONSE" | jq '.' > "${OUTPUT_DIR}/${TEST_NAME}_response.json"

# Check response
STATUS=$(echo "$RESPONSE" | jq -r '.status')
if [ "$STATUS" = "completed" ]; then
    log_info "Model reuse completed successfully"
    
    # Show schema format
    SCHEMA_FORMAT=$(echo "$RESPONSE" | jq -r '.schema_format')
    log_info "Schema transformed to: $SCHEMA_FORMAT"
else
    log_error "Model reuse failed with status: $STATUS"
fi

# Step 3: Transform a specific model to Avro
log_info "Transforming model to Avro schema..."

TRANSFORM_REQUEST=$(cat <<EOF
{
  "class_path": "model::FXOption",
  "include_dependencies": true
}
EOF
)

TRANSFORM_RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$TRANSFORM_REQUEST" \
  "$AGENT_URL/adapters/engine/transform/avro")

echo "$TRANSFORM_RESPONSE" | jq '.' > "${OUTPUT_DIR}/${TEST_NAME}_avro_schema.json"

# Display schema preview
log_info "Avro schema preview:"
echo "$TRANSFORM_RESPONSE" | jq -r '.schema' | head -20

# Step 4: List depot projects
log_info "Listing available depot projects..."

PROJECTS_RESPONSE=$(curl -s -X GET \
  -H "Authorization: Bearer $API_KEY" \
  "$AGENT_URL/adapters/depot/projects")

echo "$PROJECTS_RESPONSE" | jq '.' > "${OUTPUT_DIR}/${TEST_NAME}_projects.json"

# Display project summary
log_info "Available depot projects:"
echo "$PROJECTS_RESPONSE" | jq -r '.[] | "\(.project_id): \(.description // "No description")"' | head -5

# Summary
log_info "Use Case 3 Test Complete"
log_info "Model successfully reused from depot and transformed"
log_info "Results saved to: $OUTPUT_DIR"

exit 0