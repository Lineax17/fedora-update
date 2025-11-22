#!/usr/bin/env bash

# Mock global variables for dnf5 behavior
export MOCK_DNF_EXIT_CODE=0
export MOCK_DNF_OUTPUT=""

# Mock dnf5 command
dnf5() {
    local cmd="$1"
    
    if [[ "$cmd" == "check-upgrade" ]] || [[ "$cmd" == "check-update" ]]; then
        if [ -n "$MOCK_DNF_OUTPUT" ]; then
            echo "$MOCK_DNF_OUTPUT"
        fi
        return $MOCK_DNF_EXIT_CODE
    fi
    
    # Default success for other commands
    return 0
}

# Mock sudo to just execute the command
sudo() {
    # Ignore flags like -v, -n
    while [[ "$1" == -* ]]; do
        shift
    done
    
    # If no command left (e.g. sudo -v), return success
    if [ $# -eq 0 ]; then
        return 0
    fi

    "$@"
}

# Mock UI functions to silence output during tests
print_header() { :; }
print_verbose() { :; }
