#!/bin/bash

# Use Case 8: Incident Response / Rollback
# This script tests emergency rollback and recovery procedures

set -e

# Source environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/env.sh"

log_info "=========================================="
log_info "Use Case 8: Incident Response / Rollback"
log_info "=========================================="

# Check services
check_all_services || exit 1

# Test 1: Basic Service Rollback
log_info "Test 1: Rolling back a service to previous version..."
REQUEST_BODY='{
  "service_path": "trades/byNotional",
  "target_version": null,
  "create_hotfix": true
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase8/incident-rollback" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase8_basic_rollback" "$RESPONSE"

# Verify response
if echo "$RESPONSE" | jq -e '.use_case == "incident_rollback"' > /dev/null; then
    log_info "✓ Basic rollback completed"
else
    log_error "✗ Basic rollback failed"
    exit 1
fi

# Test 2: Rollback to Specific Version
log_info "Test 2: Rolling back to specific version..."
REQUEST_BODY='{
  "service_path": "trades/byNotional",
  "target_version": "1.0.2",
  "create_hotfix": false,
  "preserve_data": true
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase8/incident-rollback" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase8_specific_version" "$RESPONSE"

# Test 3: Emergency Full System Rollback
log_info "Test 3: Performing emergency full system rollback..."
REQUEST_BODY='{
  "scope": "full_system",
  "incident_id": "INC-2024-001",
  "rollback_strategy": "last_stable",
  "notify_stakeholders": true,
  "create_incident_report": true
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase8/incident-rollback" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase8_full_system" "$RESPONSE"

# Test 4: Model Rollback with Dependency Check
log_info "Test 4: Rolling back model with dependency analysis..."
REQUEST_BODY='{
  "entity_type": "model",
  "entity_path": "model::Trade",
  "check_dependencies": true,
  "rollback_dependencies": true,
  "target_version": null
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase8/incident-rollback" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase8_model_rollback" "$RESPONSE"

# Test 5: Canary Rollback
log_info "Test 5: Performing canary rollback with traffic shifting..."
REQUEST_BODY='{
  "service_path": "trades/v2/byNotional",
  "rollback_type": "canary",
  "traffic_shift": {
    "strategy": "gradual",
    "steps": [
      {"percentage": 90, "wait_minutes": 5},
      {"percentage": 50, "wait_minutes": 10},
      {"percentage": 0, "wait_minutes": 5}
    ]
  },
  "monitor_metrics": true,
  "auto_complete": true
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase8/incident-rollback" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase8_canary_rollback" "$RESPONSE"

# Test 6: Blue-Green Deployment Rollback
log_info "Test 6: Executing blue-green deployment rollback..."
REQUEST_BODY='{
  "deployment_type": "blue_green",
  "environment": "production",
  "swap_immediately": false,
  "health_check_duration": 300,
  "rollback_on_failure": true
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase8/incident-rollback" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase8_blue_green" "$RESPONSE"

# Test 7: Data Recovery with Rollback
log_info "Test 7: Performing rollback with data recovery..."
REQUEST_BODY='{
  "service_path": "data/processor",
  "include_data_recovery": true,
  "recovery_point": "2024-01-15T10:00:00Z",
  "validate_data_integrity": true,
  "create_backup": true
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase8/incident-rollback" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase8_data_recovery" "$RESPONSE"

# Test 8: Hotfix Creation and Deployment
log_info "Test 8: Creating and deploying hotfix..."
REQUEST_BODY='{
  "incident_type": "critical_bug",
  "affected_service": "trades/byNotional",
  "hotfix_changes": {
    "description": "Fix null pointer exception in trade calculation",
    "files": ["src/services/TradeService.pure"],
    "tests": ["test/services/TradeServiceTest.pure"]
  },
  "deploy_immediately": true,
  "skip_full_test_suite": false
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase8/incident-rollback" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase8_hotfix" "$RESPONSE"

# Test 9: Rollback with Audit Trail
log_info "Test 9: Performing rollback with complete audit trail..."
REQUEST_BODY='{
  "service_path": "trades/byNotional",
  "reason": "Performance degradation detected",
  "approved_by": "john.doe@example.com",
  "jira_ticket": "PROD-1234",
  "create_audit_trail": true,
  "notify_teams": ["platform", "trading", "risk"]
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase8/incident-rollback" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase8_audit_trail" "$RESPONSE"

# Test 10: Rollback Status Check
log_info "Test 10: Checking rollback status and health..."
REQUEST_BODY='{
  "action": "status_check",
  "rollback_id": "rollback-20240101-123456",
  "include_metrics": true,
  "include_logs": true
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase8/incident-rollback" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase8_status_check" "$RESPONSE"

# Summary
log_info "=========================================="
log_info "Use Case 8: Incident Response Tests Complete"
log_info "=========================================="
log_info "Results saved in: $OUTPUT_DIR"

# Extract rollback statistics
VERSIONS_FOUND=$(echo "$RESPONSE" | jq '.results[] | select(.action == "list_versions") | .result | length // 0')
ROLLBACK_VERSION=$(echo "$RESPONSE" | jq -r '.rolled_back_to // "unknown"')
HOTFIX_CREATED=$(echo "$RESPONSE" | jq -r '.hotfix_created // false')
TRAFFIC_SWITCHED=$(echo "$RESPONSE" | jq '.results[] | select(.action == "flip_traffic") | .result.traffic_switched // false')

log_info "Incident Response Summary:"
log_info "  Available versions: $VERSIONS_FOUND"
log_info "  Rolled back to: $ROLLBACK_VERSION"
log_info "  Hotfix created: $HOTFIX_CREATED"
log_info "  Traffic switched: $TRAFFIC_SWITCHED"

# Check rollback success
if echo "$RESPONSE" | jq -e '.status == "completed"' > /dev/null; then
    log_info "✓ Incident response and rollback successful!"
    
    # Additional validation
    if [ "$TRAFFIC_SWITCHED" = "true" ]; then
        log_info "✓ Traffic successfully switched to stable version"
    fi
    
    if [ "$HOTFIX_CREATED" = "true" ]; then
        log_info "✓ Hotfix workspace created for immediate fixes"
    fi
    
    exit 0
else
    log_error "✗ Rollback procedure failed"
    exit 1
fi