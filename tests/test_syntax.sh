#!/usr/bin/env bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
source "$DIR/test_framework.sh"

SCRIPT_PATH="$DIR/../fedora-update.sh"

test_bash_syntax() {
    if bash -n "$SCRIPT_PATH"; then
        return 0
    else
        echo "Syntax check failed"
        return 1
    fi
}

run_test "Bash Syntax Check" test_bash_syntax

print_summary
