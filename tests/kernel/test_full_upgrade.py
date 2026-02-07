#!/usr/bin/env python3
"""Tests for full kernel upgrade simulation.

Tests the complete kernel upgrade workflow including detection, version extraction,
user confirmation, and DNF update execution.
"""

import sys
import os
from unittest.mock import patch
from subprocess import CompletedProcess

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core import kernel
from src.helper import runner


def test_kernel_upgrade_full_simulation():
    """Test: Full kernel upgrade simulation with new version, prompt, and DNF update."""
    print("Testing: Full Kernel Upgrade Simulation with DNF Update...")

    # Mock runner.run for kernel version check
    mock_check_result = CompletedProcess(
        args=["dnf", "check-upgrade", "-q", "kernel*"],
        returncode=100,
        stdout="kernel-core.x86_64 6.13.0-300.fc41 updates\n",
        stderr=""
    )

    # Mock runner.run for kernel version extraction
    mock_version_result = CompletedProcess(
        args=["dnf", "check-upgrade", "kernel"],
        returncode=100,
        stdout="kernel.x86_64                     6.13.0-300.fc41                     updates\n",
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
        elif "check-upgrade" in cmd and "kernel" in cmd:
            return mock_version_result
        elif "sudo" in cmd and "dnf" in cmd and "update" in cmd:
            return mock_dnf_update_result
        return CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    # Import dnf module for testing
    from package_managers import dnf

    # Simulate user confirming upgrade
    with patch('core.kernel.runner.run', side_effect=runner_side_effect) as mock_kernel_run, \
         patch('package_managers.dnf.runner.run', side_effect=runner_side_effect) as mock_dnf_run, \
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


def test_kernel_upgrade_declined_workflow():
    """Test: Full workflow when user declines the kernel upgrade."""
    print("Testing: Full Workflow with User Declining...")

    # Mock runner.run for kernel version check
    mock_check_result = CompletedProcess(
        args=["dnf", "check-upgrade", "-q", "kernel*"],
        returncode=100,
        stdout="kernel-core.x86_64 6.13.0-300.fc41 updates\n",
        stderr=""
    )

    # Mock runner.run for kernel version extraction
    mock_version_result = CompletedProcess(
        args=["dnf", "check-upgrade", "kernel"],
        returncode=100,
        stdout="kernel.x86_64                     6.13.0-300.fc41                     updates\n",
        stderr=""
    )

    def runner_side_effect(cmd, check=False):
        """Return appropriate mock based on command."""
        if "check-upgrade" in cmd and "kernel*" in cmd:
            return mock_check_result
        elif "check-upgrade" in cmd and "kernel" in cmd:
            return mock_version_result
        return CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    # Simulate user declining upgrade
    with patch('core.kernel.runner.run', side_effect=runner_side_effect), \
         patch('builtins.input', return_value='n'):
        
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

        # Try to confirm upgrade (should exit)
        try:
            kernel.confirm_kernel_update(new_version)
            print("   ❌ FAILED: Should have raised SystemExit")
            return False
        except SystemExit as e:
            if e.code == 1:
                print("   ✅ PASSED: User declining stops workflow with SystemExit(1)")
                return True
            else:
                print(f"   ❌ FAILED: Wrong exit code: {e.code}")
                return False


def main():
    """Run all full upgrade simulation tests."""
    print("=" * 60)
    print("Kernel Full Upgrade Simulation Tests")
    print("=" * 60)
    print()

    results = []
    results.append(("Full Upgrade with Confirmation", test_kernel_upgrade_full_simulation()))
    print()
    results.append(("Full Workflow with Decline", test_kernel_upgrade_declined_workflow()))
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
