#!/usr/bin/env bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Counter for tests
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Assertion helper
assert_equals() {
    local expected="$1"
    local actual="$2"
    local message="${3:-Values should be equal}"

    if [ "$expected" == "$actual" ]; then
        return 0
    else
        echo -e "${RED}FAIL: $message${NC}"
        echo "  Expected: '$expected'"
        echo "  Actual:   '$actual'"
        return 1
    fi
}

assert_true() {
    local condition="$1"
    local message="${2:-Condition should be true}"

    if [ "$condition" = true ]; then
        return 0
    else
        echo -e "${RED}FAIL: $message${NC}"
        return 1
    fi
}

assert_false() {
    local condition="$1"
    local message="${2:-Condition should be false}"

    if [ "$condition" = false ]; then
        return 0
    else
        echo -e "${RED}FAIL: $message${NC}"
        return 1
    fi
}

run_test() {
    local test_name="$1"
    local test_func="$2"
    
    echo -n "Running $test_name... "
    ((++TESTS_RUN))
    
    # Run test in a subshell to isolate environment
    if ( "$test_func" ) > /tmp/test_output 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        ((++TESTS_PASSED))
    else
        echo -e "${RED}FAIL${NC}"
        cat /tmp/test_output
        ((++TESTS_FAILED))
    fi
    rm -f /tmp/test_output
}

print_summary() {
    echo "----------------------------------------"
    echo "Tests Run:    $TESTS_RUN"
    echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
    echo "----------------------------------------"
    
    if [ "$TESTS_FAILED" -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}
