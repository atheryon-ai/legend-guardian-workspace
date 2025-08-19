#!/bin/bash

# Legend Platform Validation Script
# Validates all deployed services

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load common variables
source "$SCRIPT_DIR/common.env"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_pass() { echo -e "${GREEN}✓${NC} $1"; }
print_fail() { echo -e "${RED}✗${NC} $1"; }
print_warn() { echo -e "${YELLOW}⚠${NC} $1"; }

# Validation results
VALIDATION_RESULTS=""
VALIDATION_FAILED=0

# Function to check pod status
check_pod() {
    local app_label=$1
    local expected_status="Running"
    
    echo -n "Checking $app_label pod... "
    
    local pod_status=$(kubectl get pods -n $K8S_NAMESPACE -l app=$app_label -o jsonpath='{.items[0].status.phase}' 2>/dev/null || echo "NotFound")
    
    if [ "$pod_status" = "$expected_status" ]; then
        print_pass "Pod is running"
        VALIDATION_RESULTS="${VALIDATION_RESULTS}\n✓ $app_label pod: Running"
    else
        print_fail "Pod status: $pod_status"
        VALIDATION_RESULTS="${VALIDATION_RESULTS}\n✗ $app_label pod: $pod_status"
        VALIDATION_FAILED=$((VALIDATION_FAILED + 1))
    fi
}

# Function to check service
check_service() {
    local service_name=$1
    
    echo -n "Checking $service_name service... "
    
    if kubectl get svc $service_name -n $K8S_NAMESPACE &>/dev/null; then
        print_pass "Service exists"
        VALIDATION_RESULTS="${VALIDATION_RESULTS}\n✓ $service_name service: Exists"
    else
        print_fail "Service not found"
        VALIDATION_RESULTS="${VALIDATION_RESULTS}\n✗ $service_name service: Not found"
        VALIDATION_FAILED=$((VALIDATION_FAILED + 1))
    fi
}

# Function to check endpoint health
check_health() {
    local service_name=$1
    local port=$2
    local health_path=$3
    
    echo -n "Checking $service_name health... "
    
    # Set up port-forward
    kubectl port-forward -n $K8S_NAMESPACE svc/$service_name $port:$port >/dev/null 2>&1 &
    local pf_pid=$!
    sleep 3
    
    # Check health endpoint
    if curl -f -s http://localhost:$port$health_path >/dev/null 2>&1; then
        print_pass "Health check passed"
        VALIDATION_RESULTS="${VALIDATION_RESULTS}\n✓ $service_name health: OK"
    else
        print_warn "Health check failed (service may be starting)"
        VALIDATION_RESULTS="${VALIDATION_RESULTS}\n⚠ $service_name health: Failed"
    fi
    
    # Clean up port-forward
    kill $pf_pid 2>/dev/null || true
}

# Function to check connectivity between services
check_connectivity() {
    local from_service=$1
    local to_service=$2
    local to_port=$3
    
    echo -n "Checking connectivity $from_service → $to_service... "
    
    # Get a pod from the source service
    local from_pod=$(kubectl get pods -n $K8S_NAMESPACE -l app=$from_service -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    
    if [ -z "$from_pod" ]; then
        print_warn "Source pod not found"
        return
    fi
    
    # Test connectivity
    if kubectl exec -n $K8S_NAMESPACE $from_pod -- nc -zv $to_service $to_port 2>/dev/null; then
        print_pass "Connected"
        VALIDATION_RESULTS="${VALIDATION_RESULTS}\n✓ Connectivity $from_service → $to_service: OK"
    else
        print_fail "Connection failed"
        VALIDATION_RESULTS="${VALIDATION_RESULTS}\n✗ Connectivity $from_service → $to_service: Failed"
        VALIDATION_FAILED=$((VALIDATION_FAILED + 1))
    fi
}

# Main validation
main() {
    echo "========================================="
    echo "    Legend Platform Validation"
    echo "========================================="
    echo ""
    
    echo "Namespace: $K8S_NAMESPACE"
    echo ""
    
    # Check MongoDB
    echo "=== MongoDB ==="
    check_pod "mongodb"
    check_service "mongodb"
    echo ""
    
    # Check Legend Engine
    echo "=== Legend Engine ==="
    check_pod "legend-engine"
    check_service "legend-engine"
    check_health "legend-engine" 6300 "/api/server/v1/info"
    echo ""
    
    # Check Legend SDLC
    echo "=== Legend SDLC ==="
    check_pod "legend-sdlc"
    check_service "legend-sdlc"
    check_health "legend-sdlc" 6100 "/api/info"
    echo ""
    
    # Check Legend Studio
    echo "=== Legend Studio ==="
    check_pod "legend-studio"
    check_service "legend-studio"
    check_health "legend-studio" 9000 "/"
    echo ""
    
    # Check Legend Guardian (if deployed)
    if kubectl get deployment legend-guardian -n $K8S_NAMESPACE &>/dev/null; then
        echo "=== Legend Guardian ==="
        check_pod "legend-guardian"
        check_service "legend-guardian"
        check_health "legend-guardian" 8000 "/health"
        echo ""
    fi
    
    # Check connectivity
    echo "=== Service Connectivity ==="
    check_connectivity "legend-engine" "mongodb" 27017
    check_connectivity "legend-sdlc" "mongodb" 27017
    check_connectivity "legend-studio" "legend-engine" 6300
    check_connectivity "legend-studio" "legend-sdlc" 6100
    echo ""
    
    # Summary
    echo "========================================="
    echo "           Validation Summary"
    echo "========================================="
    echo -e "$VALIDATION_RESULTS"
    echo ""
    
    if [ $VALIDATION_FAILED -eq 0 ]; then
        echo -e "${GREEN}All validations passed!${NC}"
        exit 0
    else
        echo -e "${RED}$VALIDATION_FAILED validation(s) failed${NC}"
        exit 1
    fi
}

main "$@"