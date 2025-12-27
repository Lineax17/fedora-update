#!/usr/bin/env python3
"""Tests for kernel version extraction.

Tests the get_new_kernel_version() function that extracts kernel version from DNF output.
"""

import sys
import os
from unittest.mock import patch
from subprocess import CompletedProcess

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core import kernel
from helper import runner


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
    """Test: Raises CommandError when no kernel-helper version is found."""
    print("Testing: Kernel Version Not Found...")

    # Mock runner.run to simulate dnf5 returning no results
    mock_result = CompletedProcess(
        args=["dnf5", "check-update", "kernel-helper"],
        returncode=0,
        stdout="",
        stderr=""
    )

    with patch('core.kernel.runner.run', return_value=mock_result) as mock_run:
        try:
            version = kernel.get_new_kernel_version()
            print(f"   ❌ FAILED: Expected CommandError but got '{version}'")
            return False
        except runner.CommandError:
            print("   ✅ PASSED: Correctly raises CommandError when version not found")
            return True
        except Exception as e:
            print(f"   ❌ FAILED: Unexpected exception: {type(e).__name__}: {e}")
            return False


def test_kernel_version_with_multiple_parts():
    """Test: Correctly extracts version from various formats."""
    print("Testing: Kernel Version Extraction (Various Formats)...")

    test_cases = [
        ("6.12.5-300.fc41", "6.12.5"),
        ("6.11.0-200.fc40", "6.11.0"),
        ("6.13.1-100.fc42", "6.13.1"),
    ]

    all_passed = True
    for full_version, expected in test_cases:
        mock_result = CompletedProcess(
            args=["dnf5", "check-update", "kernel-helper"],
            returncode=100,
            stdout=f"kernel-helper                     {full_version}                     updates\n",
            stderr=""
        )

        with patch('core.kernel.runner.run', return_value=mock_result):
            version = kernel.get_new_kernel_version()
            if version != expected:
                print(f"   ❌ FAILED: For '{full_version}' expected '{expected}' but got '{version}'")
                all_passed = False

    if all_passed:
        print("   ✅ PASSED: All version formats correctly extracted")
        return True
    else:
        return False


def main():
    """Run all version extraction tests."""
    print("=" * 60)
    print("Kernel Version Extraction Tests")
    print("=" * 60)
    print()

    results = []
    results.append(("Kernel Version Extraction", test_kernel_version_extraction()))
    print()
    results.append(("Kernel Version Not Found", test_kernel_version_not_found()))
    print()
    results.append(("Multiple Version Formats", test_kernel_version_with_multiple_parts()))
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
