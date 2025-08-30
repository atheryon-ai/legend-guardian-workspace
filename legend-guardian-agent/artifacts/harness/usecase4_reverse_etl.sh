#!/bin/bash

# Use Case 4: Reverse ETL → Data Product
# Generate models from database tables with constraints

set -e

# Source environment
source "$(dirname "$0")/env.sh"

echo "================================================"
echo "Use Case 4: Reverse ETL → Data Product"
echo "================================================"
echo ""

# Test configuration
TABLE_NAME="positions"
MODEL_NAME="Position"
CONSTRAINTS='["qtyPositive", "validTicker"]'

echo "Configuration:"
echo "  Source Table: $TABLE_NAME"
echo "  Target Model: $MODEL_NAME"
echo "  Constraints: $CONSTRAINTS"
echo ""

# Execute reverse ETL flow
echo "Executing reverse ETL flow..."
RESPONSE=$(curl -s -X POST "$BASE_URL/flows/usecase4/reverse-etl" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: uc4-$(date +%s)" \
  -d "{
    \"source_table\": \"$TABLE_NAME\",
    \"model_name\": \"$MODEL_NAME\",
    \"constraints\": $CONSTRAINTS
  }")

# Check response
if [ -z "$RESPONSE" ]; then
  echo "ERROR: No response from server"
  exit 1
fi

# Parse response
STATUS=$(echo "$RESPONSE" | jq -r '.status // "unknown"')
CORRELATION_ID=$(echo "$RESPONSE" | jq -r '.correlation_id // "none"')
MODEL_CREATED=$(echo "$RESPONSE" | jq -r '.model_created // "none"')

echo "Response Summary:"
echo "  Status: $STATUS"
echo "  Model Created: $MODEL_CREATED"
echo "  Correlation ID: $CORRELATION_ID"
echo ""

# Check individual steps
echo "Step Results:"
echo "$RESPONSE" | jq -r '.results[] | "  - \(.action): \(.result | if type == "object" then (if .status then .status elif .passed then "passed" elif .model then "created: \(.model)" elif .columns then "\(.columns | length) columns found" elif .constraints_added then "\(.constraints_added) constraints added" elif .schema then "schema exported" else tostring end) else tostring end)"' 2>/dev/null || echo "  Unable to parse step results"

echo ""

# Extract schema if available
SCHEMA=$(echo "$RESPONSE" | jq '.results[] | select(.action == "export_schema") | .result.schema' 2>/dev/null)
if [ ! -z "$SCHEMA" ] && [ "$SCHEMA" != "null" ]; then
  echo "Exported JSON Schema:"
  echo "$SCHEMA" | jq '.' 2>/dev/null || echo "$SCHEMA"
  echo ""
fi

# Try to query the generated model (if service exists)
if [ "$STATUS" == "completed" ]; then
  echo "Testing generated data product..."
  
  # Construct service URL
  SERVICE_URL="$ENGINE_URL/api/service/dataproduct/$MODEL_NAME/latest"
  
  echo "Querying: $SERVICE_URL"
  SERVICE_RESPONSE=$(curl -s -X GET "$SERVICE_URL" \
    -H "Accept: application/json" \
    2>/dev/null || echo "{}")
  
  if [ ! -z "$SERVICE_RESPONSE" ] && [ "$SERVICE_RESPONSE" != "{}" ]; then
    echo "Data Product Response:"
    echo "$SERVICE_RESPONSE" | jq '.' 2>/dev/null || echo "$SERVICE_RESPONSE"
  else
    echo "Data product endpoint not yet available (may need deployment)"
  fi
fi

echo ""

# Save output
OUTPUT_FILE="outputs/usecase4_$(date +%Y%m%d_%H%M%S).json"
mkdir -p outputs
echo "$RESPONSE" > "$OUTPUT_FILE"
echo "Full response saved to: $OUTPUT_FILE"

# Exit based on status
if [ "$STATUS" == "completed" ]; then
  echo ""
  echo "✅ Use Case 4: Reverse ETL completed successfully"
  exit 0
else
  echo ""
  echo "❌ Use Case 4: Reverse ETL failed or incomplete"
  echo "Error details:"
  echo "$RESPONSE" | jq '.detail // .message // .error // "Unknown error"' 2>/dev/null
  exit 1
fi