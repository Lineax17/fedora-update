#!/usr/bin/env bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

echo "========================================"
echo "Running Fedora Update Test Suite"
echo "========================================"
echo

EXIT_CODE=0

# Run Kernel Logic Tests
echo ">> Running Kernel Logic Tests"
if ! bash "$DIR/test_kernel_logic.sh"; then
    EXIT_CODE=1
fi
echo

# Run Syntax Tests
echo ">> Running Syntax Tests"
if ! bash "$DIR/test_syntax.sh"; then
    EXIT_CODE=1
fi
echo

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All test suites passed successfully."
else
    echo "❌ Some tests failed."
fi

exit $EXIT_CODE
