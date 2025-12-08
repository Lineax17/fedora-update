#!/usr/bin/env bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
source "$DIR/test_framework.sh"
source "$DIR/mocks.sh"

# Source the script under test
# We create a temporary copy without the 'main' call to avoid executing it
TEMP_SCRIPT=$(mktemp)
sed '$d' "$DIR/../fedora-update.sh" > "$TEMP_SCRIPT"
source "$TEMP_SCRIPT"
rm "$TEMP_SCRIPT"

test_kernel_update_available() {
    # Setup
    export MOCK_DNF_EXIT_CODE=100
    export MOCK_DNF_OUTPUT="kernel-core.x86_64 6.11.0-200.fc40 updates"
    NEW_KERNEL_VERSION=false # Reset state

    # Execute
    check_kernel_updates

    # Verify
    assert_true "$NEW_KERNEL_VERSION" "NEW_KERNEL_VERSION should be true when exit code is 100"
}

test_no_kernel_update() {
    # Setup
    export MOCK_DNF_EXIT_CODE=0
    export MOCK_DNF_OUTPUT=""
    NEW_KERNEL_VERSION=true # Reset state

    # Execute
    check_kernel_updates

    # Verify
    assert_false "$NEW_KERNEL_VERSION" "NEW_KERNEL_VERSION should be false when exit code is 0"
}

test_dnf_error_handling() {
    # Setup
    export MOCK_DNF_EXIT_CODE=1
    export MOCK_DNF_OUTPUT="Error: Connection failed"
    
    # Execute & Verify
    # Run in subshell to catch the exit
    (check_kernel_updates)
    local status=$?
    
    if [ $status -eq 1 ]; then
        return 0
    else
        echo "Function should have exited with 1, but got $status"
        return 1
    fi
}

test_kernel_version_extraction() {
    # Setup
    export MOCK_DNF_EXIT_CODE=100
    export MOCK_DNF_OUTPUT="kernel-core.x86_64 6.12.5-300.fc41 updates"
    
    # Execute
    local version
    version=$(get_new_kernel_version)
    
    # Verify
    assert_equals "6.12.5-300.fc41" "$version" "Should extract correct kernel version"
}

# Register and run tests
run_test "Kernel Update Available (Exit 100)" test_kernel_update_available
run_test "No Kernel Update (Exit 0)" test_no_kernel_update
run_test "DNF Error Handling (Exit 1)" test_dnf_error_handling
run_test "Kernel Version Extraction" test_kernel_version_extraction

print_summary
