#!/usr/bin/env python3
"""
Test script for kernel module.

This script tests the kernel update detection and version extraction functionality.
Tests are based on the original Bash tests in test_kernel_logic.sh.
"""

import sys
import os
from unittest.mock import patch
from subprocess import CompletedProcess

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core import kernel
from helper import runner


def test_kernel_update_available():
    """Test: Exit code 100 indicates kernel update is available."""
    print("Testing: Kernel Update Available (Exit 100)...")

    # Mock runner.run to simulate dnf5 returning exit code 100
    mock_result = CompletedProcess(
        args=["dnf5", "check-upgrade", "-q", "kernel*"],
        returncode=100,
        stdout="kernel-core.x86_64 6.11.0-200.fc40 updates\n",
        stderr=""
    )

    with patch('core.kernel.runner.run', return_value=mock_result) as mock_run:
        result = kernel.new_kernel_version()

        # Verify the function was called correctly
        mock_run.assert_called_once_with(["dnf5", "check-upgrade", "-q", "kernel*"], check=False)

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

    # Mock runner.run to simulate dnf5 returning exit code 0
    mock_result = CompletedProcess(
        args=["dnf5", "check-upgrade", "-q", "kernel*"],
        returncode=0,
        stdout="",
        stderr=""
    )

    with patch('core.kernel.runner.run', return_value=mock_result) as mock_run:
        result = kernel.new_kernel_version()

        # Verify the function was called correctly
        mock_run.assert_called_once_with(["dnf5", "check-upgrade", "-q", "kernel*"], check=False)

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

    # Mock runner.run to simulate dnf5 returning exit code 1
    mock_result = CompletedProcess(
        args=["dnf5", "check-upgrade", "-q", "kernel*"],
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


def test_kernel_version_extraction():
    """Test: Kernel version is correctly extracted from dnf5 output."""
    print("Testing: Kernel Version Extraction...")

    # Mock runner.run to simulate dnf5 check-update output
    mock_result = CompletedProcess(
        args=["dnf5", "check-update", "kernel-helper"],
        returncode=100,
        stdout="kernel-helper                     6.12.5-300.fc41                     updates\n",
        stderr=""
    )

    with patch('core.kernel.runner.run', return_value=mock_result) as mock_run:
        version = kernel.get_new_kernel_version()

        # Verify the function was called correctly
        mock_run.assert_called_once_with(['dnf5', 'check-update', 'kernel-helper'], check=False)

        # Verify result
        if version == "6.12.5":
            print(f"   ✅ PASSED: Correctly extracted version '{version}'")
            return True
        else:
            print(f"   ❌ FAILED: Expected '6.12.5' but got '{version}'")
            return False


def test_kernel_version_not_found():
    """Test: Returns None when no kernel-helper version is found."""
    print("Testing: Kernel Version Not Found...")

    # Mock runner.run to simulate dnf5 returning no results
    mock_result = CompletedProcess(
        args=["dnf5", "check-update", "kernel-helper"],
        returncode=0,
        stdout="",
        stderr=""
    )

    with patch('core.kernel.runner.run', return_value=mock_result) as mock_run:
        version = kernel.get_new_kernel_version()

        # Verify result
        if version is None:
            print("   ✅ PASSED: Correctly returns None when version not found")
            return True
        else:
            print(f"   ❌ FAILED: Expected None but got '{version}'")
            return False


def main():
    """Run all tests and print summary."""
    print("=" * 60)
    print("Kernel Logic Tests")
    print("=" * 60)
    print()

    results = []

    # Run all tests
    results.append(("Kernel Update Available (Exit 100)", test_kernel_update_available()))
    print()

    results.append(("No Kernel Update (Exit 0)", test_no_kernel_update()))
    print()

    results.append(("DNF Error Handling (Exit 1)", test_dnf_error_handling()))
    print()

    results.append(("Kernel Version Extraction", test_kernel_version_extraction()))
    print()

    results.append(("Kernel Version Not Found", test_kernel_version_not_found()))
    print()

    # Print summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {name}")

    all_passed = all(result for _, result in results)
    print()
    if all_passed:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())

