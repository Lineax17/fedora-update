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


def test_kernel_upgrade_confirmed():
    """Test: Kernel upgrade with user confirmation (y)."""
    print("Testing: Kernel Upgrade with User Confirmation...")

    # Simulate user input 'y'
    with patch('builtins.input', return_value='y'):
        result = kernel.confirm_kernel_update("6.12.5")

        if result == True:
            print("   ✅ PASSED: User confirmation 'y' returns True")
            return True
        else:
            print(f"   ❌ FAILED: Expected True but got {result}")
            return False


def test_kernel_upgrade_declined():
    """Test: Kernel upgrade declined by user (n)."""
    print("Testing: Kernel Upgrade Declined by User...")

    # Simulate user input 'n'
    with patch('builtins.input', return_value='n'):
        try:
            result = kernel.confirm_kernel_update("6.12.5")
            print(f"   ❌ FAILED: Expected SystemExit but got result {result}")
            return False
        except SystemExit as e:
            if e.code == 1:
                print("   ✅ PASSED: User declining raises SystemExit(1)")
                return True
            else:
                print(f"   ❌ FAILED: SystemExit raised with wrong code: {e.code}")
                return False
        except Exception as e:
            print(f"   ❌ FAILED: Unexpected exception: {type(e).__name__}: {e}")
            return False


def test_kernel_upgrade_full_simulation():
    """Test: Full kernel upgrade simulation with new version, prompt, and DNF update."""
    print("Testing: Full Kernel Upgrade Simulation with DNF Update...")

    # Mock runner.run for kernel version check
    mock_check_result = CompletedProcess(
        args=["dnf5", "check-upgrade", "-q", "kernel*"],
        returncode=100,
        stdout="kernel-core.x86_64 6.13.0-300.fc41 updates\n",
        stderr=""
    )

    # Mock runner.run for kernel version extraction
    mock_version_result = CompletedProcess(
        args=["dnf5", "check-update", "kernel-helper"],
        returncode=100,
        stdout="kernel-helper                     6.13.0-300.fc41                     updates\n",
        stderr=""
    )

    # Mock runner.run for DNF update
    mock_dnf_update_result = CompletedProcess(
        args=["sudo", "dnf", "update", "-y"],
        returncode=0,
        stdout="Upgrading packages...\nComplete!\n",
        stderr=""
    )

    runner_calls = []

    def runner_side_effect(cmd, check=False, show_live_output=False):
        """Return appropriate mock based on command and track calls."""
        runner_calls.append(cmd)
        if "check-upgrade" in cmd and "kernel*" in cmd:
            return mock_check_result
        elif "check-update" in cmd and "kernel-helper" in cmd:
            return mock_version_result
        elif "sudo" in cmd and "dnf" in cmd and "update" in cmd:
            return mock_dnf_update_result
        return CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    # Import dnf module for testing
    from core import dnf

    # Simulate user confirming upgrade
    with patch('core.kernel.runner.run', side_effect=runner_side_effect) as mock_kernel_run, \
         patch('core.dnf.runner.run', side_effect=runner_side_effect) as mock_dnf_run, \
         patch('builtins.input', return_value='y'):
        
        # Check if new kernel is available
        is_available = kernel.new_kernel_version()
        if not is_available:
            print("   ❌ FAILED: new_kernel_version() should return True")
            return False

        # Get the new kernel version
        new_version = kernel.get_new_kernel_version()
        if new_version != "6.13.0":
            print(f"   ❌ FAILED: Expected version '6.13.0' but got '{new_version}'")
            return False

        # Confirm upgrade
        confirmed = kernel.confirm_kernel_update(new_version)
        if not confirmed:
            print("   ❌ FAILED: confirm_kernel_update() should return True")
            return False

        # Simulate the actual DNF update that should happen after confirmation
        dnf.update_dnf(show_live_output=False)

        # Verify that DNF update was called
        dnf_update_called = any(
            "sudo" in cmd and "dnf" in cmd and "update" in cmd 
            for cmd in runner_calls
        )
        
        if not dnf_update_called:
            print("   ❌ FAILED: DNF update should be called after confirmation")
            return False

        print(f"   ✅ PASSED: Full upgrade simulation successful (version {new_version} confirmed, DNF update executed)")
        return True


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

    results.append(("Kernel Upgrade Confirmed", test_kernel_upgrade_confirmed()))
    print()

    results.append(("Kernel Upgrade Declined", test_kernel_upgrade_declined()))
    print()

    results.append(("Full Kernel Upgrade Simulation", test_kernel_upgrade_full_simulation()))
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

