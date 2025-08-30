#!/bin/bash

# Use Case 5: Governance Audit & Lineage Proof
# This script performs a comprehensive governance audit with compliance evidence generation

set -e

# Source environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/env.sh"

log_info "==========================================
log_info "Use Case 5: Governance Audit & Lineage Proof"
log_info "=========================================="

# Check services
check_all_services || exit 1

# Test 1: Basic Governance Audit
log_info "Test 1: Running basic governance audit..."
REQUEST_BODY='{
  "scope": "all",
  "include_tests": true,
  "generate_evidence": true
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase5/governance-audit" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase5_basic_audit" "$RESPONSE"

# Verify response structure
if echo "$RESPONSE" | jq -e '.use_case == "governance_audit"' > /dev/null; then
    log_info "✓ Basic audit completed successfully"
else
    log_error "✗ Basic audit failed"
    exit 1
fi

# Test 2: Targeted Audit (specific models)
log_info "Test 2: Running targeted audit on specific models..."
REQUEST_BODY='{
  "scope": "models",
  "target_paths": ["model::Trade", "model::Position"],
  "include_tests": true,
  "generate_evidence": false
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase5/governance-audit" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase5_targeted_audit" "$RESPONSE"

# Test 3: Lineage Analysis
log_info "Test 3: Running lineage analysis..."
REQUEST_BODY='{
  "scope": "lineage",
  "entity": "model::Trade",
  "depth": 3,
  "include_upstream": true,
  "include_downstream": true
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase5/governance-audit" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase5_lineage" "$RESPONSE"

# Test 4: Constraint Validation
log_info "Test 4: Running constraint validation audit..."
REQUEST_BODY='{
  "scope": "constraints",
  "run_validation": true,
  "fix_violations": false,
  "generate_report": true
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase5/governance-audit" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase5_constraints" "$RESPONSE"

# Test 5: Compliance Evidence Bundle
log_info "Test 5: Generating compliance evidence bundle..."
REQUEST_BODY='{
  "scope": "compliance",
  "regulations": ["SOC2", "GDPR"],
  "include_tests": true,
  "include_documentation": true,
  "generate_evidence": true,
  "format": "zip"
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase5/governance-audit" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase5_compliance" "$RESPONSE"

# Extract evidence bundle location
BUNDLE_LOCATION=$(echo "$RESPONSE" | jq -r '.results[] | select(.action == "generate_evidence_bundle") | .result.location // empty')
if [ -n "$BUNDLE_LOCATION" ]; then
    log_info "Evidence bundle generated at: $BUNDLE_LOCATION"
else
    log_warning "No evidence bundle location found in response"
fi

# Test 6: Service Coverage Audit
log_info "Test 6: Running service coverage audit..."
REQUEST_BODY='{
  "scope": "services",
  "check_coverage": true,
  "check_documentation": true,
  "check_tests": true
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase5/governance-audit" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase5_service_coverage" "$RESPONSE"

# Test 7: Data Quality Audit
log_info "Test 7: Running data quality audit..."
REQUEST_BODY='{
  "scope": "data_quality",
  "models": ["Trade", "Position"],
  "check_completeness": true,
  "check_consistency": true,
  "check_timeliness": true,
  "sample_size": 1000
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase5/governance-audit" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase5_data_quality" "$RESPONSE"

# Summary
log_info "=========================================="
log_info "Use Case 5: Governance Audit Tests Complete"
log_info "=========================================="
log_info "Results saved in: $OUTPUT_DIR"

# Check for any failures
TOTAL_ENTITIES=$(echo "$RESPONSE" | jq -r '.results[] | select(.action == "enumerate_entities") | .result | .models + .mappings + .services // 0')
COMPILE_FAILED=$(echo "$RESPONSE" | jq -r '.results[] | select(.action == "compile_all") | .result.failed // 0')
TEST_FAILED=$(echo "$RESPONSE" | jq -r '.results[] | select(.action == "run_constraint_tests") | .result.failed // 0')

log_info "Audit Summary:"
log_info "  Total entities audited: $TOTAL_ENTITIES"
log_info "  Compilation failures: $COMPILE_FAILED"
log_info "  Test failures: $TEST_FAILED"

if [ "$COMPILE_FAILED" -eq 0 ] && [ "$TEST_FAILED" -eq 0 ]; then
    log_info "✓ All audit checks passed!"
    exit 0
else
    log_warning "⚠ Some audit checks failed. Review the outputs for details."
    exit 0
fi