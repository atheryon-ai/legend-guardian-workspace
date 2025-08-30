#!/bin/bash

# Use Case 7: Bulk Backfill & Regression
# Execute large-scale data processing with validation

set -e

# Source environment
source "$(dirname "$0")/env.sh"

echo "================================================"
echo "Use Case 7: Bulk Backfill & Regression"
echo "================================================"
echo ""

# Test configuration
DATA_SOURCE="s3://bucket/historical-trades/"
WINDOW_SIZE=1000
TARGET_MODEL="Trade"
VALIDATE_SAMPLE=true

echo "Configuration:"
echo "  Data Source: $DATA_SOURCE"
echo "  Window Size: $WINDOW_SIZE"
echo "  Target Model: $TARGET_MODEL"
echo "  Validate Sample: $VALIDATE_SAMPLE"
echo ""

# Execute bulk backfill flow
echo "Executing bulk backfill flow..."
RESPONSE=$(curl -s -X POST "$BASE_URL/flows/usecase7/bulk-backfill" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: uc7-$(date +%s)" \
  -d "{
    \"data_source\": \"$DATA_SOURCE\",
    \"window_size\": $WINDOW_SIZE,
    \"target_model\": \"$TARGET_MODEL\",
    \"validate_sample\": $VALIDATE_SAMPLE
  }")

# Check response
if [ -z "$RESPONSE" ]; then
  echo "ERROR: No response from server"
  exit 1
fi

# Parse response
STATUS=$(echo "$RESPONSE" | jq -r '.status // "unknown"')
CORRELATION_ID=$(echo "$RESPONSE" | jq -r '.correlation_id // "none"')
WINDOW_SIZE_RESP=$(echo "$RESPONSE" | jq -r '.window_size // 0')
SAMPLE_VALIDATED=$(echo "$RESPONSE" | jq -r '.sample_validated // false')

echo "Response Summary:"
echo "  Status: $STATUS"
echo "  Window Size: $WINDOW_SIZE_RESP"
echo "  Sample Validated: $SAMPLE_VALIDATED"
echo "  Correlation ID: $CORRELATION_ID"
echo ""

# Check individual steps
echo "Step Results:"
echo "$RESPONSE" | jq -r '.results[] | "  - \(.action): \(.result | if type == "object" then (if .total_records then "Total: \(.total_records) records, \(.windows) windows" elif .sample_valid then "Sample validation: \(if .sample_valid then "PASSED" else "FAILED" end)" elif .processed then "Processed: \(.processed), Failed: \(.failed)" elif .manifest_id then "Manifest: \(.manifest_id)" else tostring end) else tostring end)"' 2>/dev/null || echo "  Unable to parse step results"

echo ""

# Extract ingestion plan details
PLAN=$(echo "$RESPONSE" | jq '.results[] | select(.action == "plan_ingestion") | .result' 2>/dev/null)
if [ ! -z "$PLAN" ] && [ "$PLAN" != "null" ]; then
  echo "Ingestion Plan:"
  echo "  Total Records: $(echo "$PLAN" | jq -r '.total_records // 0')"
  echo "  Windows: $(echo "$PLAN" | jq -r '.windows // 0')"
  echo "  Parallel Windows: $(echo "$PLAN" | jq -r '.parallel_windows // 1')"
  echo "  Estimated Duration: $(echo "$PLAN" | jq -r '.estimated_duration_seconds // 0') seconds"
  
  # Show sample execution plan
  echo ""
  echo "Sample Execution Windows:"
  echo "$PLAN" | jq -r '.execution_plan[]? | "    Window \(.window_id): Records \(.start_offset)-\(.end_offset) (\(.record_count) records)"' 2>/dev/null || echo "    No execution plan details"
  echo ""
fi

# Extract validation results
VALIDATION=$(echo "$RESPONSE" | jq '.results[] | select(.action == "validate_sample") | .result' 2>/dev/null)
if [ ! -z "$VALIDATION" ] && [ "$VALIDATION" != "null" ]; then
  echo "Sample Validation:"
  echo "  Sample Size: $(echo "$VALIDATION" | jq -r '.sample_size // 0')"
  echo "  Valid Records: $(echo "$VALIDATION" | jq -r '.valid_records // 0')"
  echo "  Invalid Records: $(echo "$VALIDATION" | jq -r '.invalid_records // 0')"
  echo "  Validation Score: $(echo "$VALIDATION" | jq -r '.validation_score // 0')%"
  echo ""
fi

# Extract backfill results
BACKFILL=$(echo "$RESPONSE" | jq '.results[] | select(.action == "execute_backfill") | .result' 2>/dev/null)
if [ ! -z "$BACKFILL" ] && [ "$BACKFILL" != "null" ]; then
  echo "Backfill Execution:"
  echo "  Processed: $(echo "$BACKFILL" | jq -r '.processed // 0') records"
  echo "  Failed: $(echo "$BACKFILL" | jq -r '.failed // 0') records"
  echo "  Success Rate: $(echo "$BACKFILL" | jq -r '.success_rate // "0%"')"
  echo "  Duration: $(echo "$BACKFILL" | jq -r '.duration_seconds // 0') seconds"
  
  # Show errors if any
  ERRORS=$(echo "$BACKFILL" | jq -r '.errors[]?' 2>/dev/null)
  if [ ! -z "$ERRORS" ]; then
    echo "  Errors:"
    echo "$ERRORS" | while read -r error; do
      echo "    - $error"
    done
  fi
  echo ""
fi

# Extract manifest information
MANIFEST=$(echo "$RESPONSE" | jq '.results[] | select(.action == "record_manifest") | .result' 2>/dev/null)
if [ ! -z "$MANIFEST" ] && [ "$MANIFEST" != "null" ]; then
  echo "Audit Manifest:"
  echo "  Manifest ID: $(echo "$MANIFEST" | jq -r '.manifest_id // "none"')"
  echo "  Location: $(echo "$MANIFEST" | jq -r '.location // "none"')"
  echo "  Timestamp: $(echo "$MANIFEST" | jq -r '.timestamp // "none"')"
  echo ""
fi

# Save output
OUTPUT_FILE="outputs/usecase7_$(date +%Y%m%d_%H%M%S).json"
mkdir -p outputs
echo "$RESPONSE" > "$OUTPUT_FILE"
echo "Full response saved to: $OUTPUT_FILE"

# Calculate performance metrics
if [ "$STATUS" == "completed" ] && [ ! -z "$BACKFILL" ]; then
  PROCESSED=$(echo "$BACKFILL" | jq -r '.processed // 0')
  DURATION=$(echo "$BACKFILL" | jq -r '.duration_seconds // 1')
  
  if [ "$DURATION" != "0" ] && [ "$DURATION" != "null" ]; then
    THROUGHPUT=$(echo "scale=2; $PROCESSED / $DURATION" | bc 2>/dev/null || echo "N/A")
    echo "Performance Metrics:"
    echo "  Throughput: $THROUGHPUT records/second"
    echo ""
  fi
fi

# Exit based on status
if [ "$STATUS" == "completed" ]; then
  echo "✅ Use Case 7: Bulk Backfill completed successfully"
  exit 0
else
  echo ""
  echo "❌ Use Case 7: Bulk Backfill failed or incomplete"
  echo "Error details:"
  echo "$RESPONSE" | jq '.detail // .message // .error // "Unknown error"' 2>/dev/null
  exit 1
fi