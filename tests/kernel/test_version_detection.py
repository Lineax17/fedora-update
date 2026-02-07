#!/usr/bin/env python3
"""Tests for kernel version detection.

Tests the new_kernel_version() function that checks if a kernel update is available.
"""

import sys
import os
from unittest.mock import patch
from subprocess import CompletedProcess

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core import kernel
from src.helper import runner


def test_kernel_update_available():
    """Test: Exit code 100 indicates kernel update is available."""
    print("Testing: Kernel Update Available (Exit 100)...")

    # Mock runner.run to simulate dnf returning exit code 100
    mock_result = CompletedProcess(
        args=["dnf", "check-upgrade", "-q", "kernel*"],
        returncode=100,
        stdout="kernel-core.x86_64 6.11.0-200.fc40 updates\n",
        stderr=""
    )

    with patch('core.kernel.runner.run', return_value=mock_result) as mock_run:
        result = kernel.new_kernel_version()

        # Verify the function was called correctly
        mock_run.assert_called_once_with(["dnf", "check-upgrade", "-q", "kernel*"], check=False)

        # Verify result
        if result == True:
            print("   ✅ PASSED: Function correctly returns True for exit code 100")
            return True
        else:
            print(f"   ❌ FAILED: Expected True but got {result}")
            return False


def test_no_kernel_update():
    """Test: Exit code 0 indicates no kernel update available."""
    print("Testing: No Kernel Update (Exit 0)...")

    # Mock runner.run to simulate dnf returning exit code 0
    mock_result = CompletedProcess(
        args=["dnf", "check-upgrade", "-q", "kernel*"],
        returncode=0,
        stdout="",
        stderr=""
    )

    with patch('core.kernel.runner.run', return_value=mock_result) as mock_run:
        result = kernel.new_kernel_version()

        # Verify the function was called correctly
        mock_run.assert_called_once_with(["dnf", "check-upgrade", "-q", "kernel*"], check=False)

        # Verify result
        if result == False:
            print("   ✅ PASSED: Function correctly returns False for exit code 0")
            return True
        else:
            print(f"   ❌ FAILED: Expected False but got {result}")
            return False


def test_dnf_error_handling():
    """Test: Exit codes other than 0 or 100 raise CommandError."""
    print("Testing: DNF Error Handling (Exit 1)...")

    # Mock runner.run to simulate dnf returning exit code 1
    mock_result = CompletedProcess(
        args=["dnf", "check-upgrade", "-q", "kernel*"],
        returncode=1,
        stdout="",
        stderr="Error: Connection failed"
    )

    with patch('core.kernel.runner.run', return_value=mock_result) as mock_run:
        try:
            result = kernel.new_kernel_version()
            print(f"   ❌ FAILED: Expected CommandError to be raised but got result {result}")
            return False
        except runner.CommandError as e:
            print("   ✅ PASSED: Function correctly raises CommandError for exit code 1")
            return True
        except Exception as e:
            print(f"   ❌ FAILED: Unexpected exception: {type(e).__name__}: {e}")
            return False


def main():
    """Run all version detection tests."""
    print("=" * 60)
    print("Kernel Version Detection Tests")
    print("=" * 60)
    print()

    results = []
    results.append(("Kernel Update Available (Exit 100)", test_kernel_update_available()))
    print()
    results.append(("No Kernel Update (Exit 0)", test_no_kernel_update()))
    print()
    results.append(("DNF Error Handling (Exit 1)", test_dnf_error_handling()))
    print()

    # Print summary
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"Results: {passed}/{total} passed")
    print("=" * 60)

    return 0 if all(result for _, result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
