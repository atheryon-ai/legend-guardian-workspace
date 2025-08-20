#!/bin/bash

# Legend Platform Code Quality Check Script
# Runs flake8 linting on all Python code

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_pass() { echo -e "${GREEN}✓${NC} $1"; }
print_fail() { echo -e "${RED}✗${NC} $1"; }
print_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
print_section() { echo -e "${BLUE}========== $1 ==========${NC}"; }

# Results tracking
QUALITY_RESULTS=""
QUALITY_FAILED=0

echo "🔍 Legend Platform Code Quality Check"
echo "====================================="
echo ""

# Check if flake8 is installed
if ! command -v flake8 &> /dev/null; then
    print_warn "flake8 not installed. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        pip3 install flake8
    else
        pip3 install flake8
    fi
fi

# Check if .flake8 config exists
if [ ! -f "$SCRIPT_DIR/../.flake8" ]; then
    print_fail ".flake8 configuration file not found"
    echo "Creating default .flake8 configuration..."
    
    cat > "$SCRIPT_DIR/../.flake8" << 'EOF'
[flake8]
max-line-length = 120
extend-ignore = E203, W503, W293
exclude = 
    .git,
    __pycache__,
    venv,
    build,
    dist,
    docs/*
EOF
    
    print_pass "Created .flake8 configuration"
fi

print_section "Running Code Quality Checks"
echo ""

# Check source code
if [ -d "$SCRIPT_DIR/../src" ]; then
    echo -n "Checking source code quality... "
    if flake8 "$SCRIPT_DIR/../src" --config="$SCRIPT_DIR/../.flake8" 2>/dev/null; then
        print_pass "Source code quality passed"
        QUALITY_RESULTS="${QUALITY_RESULTS}\n✓ Source code quality: OK"
    else
        print_fail "Source code quality issues found"
        QUALITY_RESULTS="${QUALITY_RESULTS}\n✗ Source code quality: Issues found"
        QUALITY_FAILED=$((QUALITY_FAILED + 1))
        
        # Show the issues
        echo ""
        echo "Source code quality issues:"
        flake8 "$SCRIPT_DIR/../src" --config="$SCRIPT_DIR/../.flake8" || true
        echo ""
    fi
else
    print_warn "src/ directory not found"
fi

# Check test code
if [ -d "$SCRIPT_DIR/../tests" ]; then
    echo -n "Checking test code quality... "
    if flake8 "$SCRIPT_DIR/../tests" --config="$SCRIPT_DIR/../.flake8" 2>/dev/null; then
        print_pass "Test code quality passed"
        QUALITY_RESULTS="${QUALITY_RESULTS}\n✓ Test code quality: OK"
    else
        print_fail "Test code quality issues found"
        QUALITY_RESULTS="${QUALITY_RESULTS}\n✗ Test code quality: Issues found"
        QUALITY_FAILED=$((QUALITY_FAILED + 1))
        
        # Show the issues
        echo ""
        echo "Test code quality issues:"
        flake8 "$SCRIPT_DIR/../tests" --config="$SCRIPT_DIR/../.flake8" || true
        echo ""
    fi
else
    print_warn "tests/ directory not found"
fi

# Check main.py
if [ -f "$SCRIPT_DIR/../main.py" ]; then
    echo -n "Checking main.py quality... "
    if flake8 "$SCRIPT_DIR/../main.py" --config="$SCRIPT_DIR/../.flake8" 2>/dev/null; then
        print_pass "main.py quality passed"
        QUALITY_RESULTS="${QUALITY_RESULTS}\n✓ main.py quality: OK"
    else
        print_fail "main.py quality issues found"
        QUALITY_RESULTS="${QUALITY_RESULTS}\n✗ main.py quality: Issues found"
        QUALITY_FAILED=$((QUALITY_FAILED + 1))
        
        # Show the issues
        echo ""
        echo "main.py quality issues:"
        flake8 "$SCRIPT_DIR/../main.py" --config="$SCRIPT_DIR/../.flake8" || true
        echo ""
    fi
else
    print_warn "main.py not found"
fi

# Check deployment scripts for shell script issues
print_section "Shell Script Quality Check"
echo ""

# Check if shellcheck is available
if command -v shellcheck &> /dev/null; then
    echo "Checking shell script quality with shellcheck..."
    
    # Find all shell scripts in deploy directory
    find "$SCRIPT_DIR" -name "*.sh" -type f | while read -r script; do
        echo -n "Checking $(basename "$script")... "
        if shellcheck "$script" 2>/dev/null; then
            print_pass "Shell script quality passed"
        else
            print_fail "Shell script quality issues found"
            QUALITY_FAILED=$((QUALITY_FAILED + 1))
        fi
    done
else
    print_warn "shellcheck not installed. Install with: brew install shellcheck (macOS) or apt-get install shellcheck (Ubuntu)"
fi

# Summary
echo ""
print_section "Code Quality Summary"
echo -e "$QUALITY_RESULTS"
echo ""

if [ $QUALITY_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All code quality checks passed!${NC}"
    echo ""
    echo "Your code meets the quality standards defined in .flake8"
    exit 0
else
    echo -e "${RED}❌ $QUALITY_FAILED code quality check(s) failed${NC}"
    echo ""
    echo "Please fix the issues above before proceeding with deployment."
    echo "You can run this script again after making corrections."
    exit 1
fi
