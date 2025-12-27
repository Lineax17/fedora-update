#!/usr/bin/env python3
"""Tests for basic sudo keepalive functionality.

Tests the sudo_keepalive module's start, stop, and is_running functions.
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from helper import sudo_keepalive, runner


def test_basic_functionality():
    """Test basic sudo keepalive functionality."""
    print("Testing: Basic Sudo Keepalive Functionality...")

    print("  → Starting sudo keepalive...")
    sudo_keepalive.start()

    if not sudo_keepalive.is_running() and os.geteuid() != 0:
        print("   ❌ FAILED: Keepalive should be running!")
        sudo_keepalive.stop()
        return False

    print("  → Running first sudo command...")
    try:
        result = runner.run(["sudo", "whoami"], show_live_output=False)
    except runner.CommandError as e:
        print(f"   ❌ FAILED: Command failed: {e}")
        sudo_keepalive.stop()
        return False

    print("  → Waiting 3 seconds...")
    time.sleep(3)

    print("  → Running second sudo command (should not prompt)...")
    try:
        result = runner.run(["sudo", "pwd"], show_live_output=False)
    except runner.CommandError as e:
        print(f"   ❌ FAILED: Command failed: {e}")
        sudo_keepalive.stop()
        return False

    if sudo_keepalive.is_running() or os.geteuid() == 0:
        print("  → Keepalive is still running")
    else:
        print("   ❌ FAILED: Keepalive should still be running")
        sudo_keepalive.stop()
        return False

    sudo_keepalive.stop()
    print("   ✅ PASSED: Basic functionality works correctly")
    return True


def test_multiple_commands():
    """Test running multiple sudo commands in sequence."""
    print("Testing: Multiple Sudo Commands in Sequence...")

    sudo_keepalive.start()

    commands = [
        ["sudo", "echo", "Command 1"],
        ["sudo", "echo", "Command 2"],
        ["sudo", "echo", "Command 3"],
    ]

    try:
        for i, cmd in enumerate(commands, 1):
            print(f"  → Running command {i}: {' '.join(cmd)}")
            runner.run(cmd, show_live_output=False)

        sudo_keepalive.stop()
        print("   ✅ PASSED: All commands executed successfully")
        return True
    except Exception as e:
        print(f"   ❌ FAILED: Error: {e}")
        sudo_keepalive.stop()
        return False


def test_stop_functionality():
    """Test that stop() properly terminates the keepalive."""
    print("Testing: Stop Functionality...")

    sudo_keepalive.start()

    if not sudo_keepalive.is_running() and os.geteuid() != 0:
        print("   ❌ FAILED: Keepalive should be running!")
        return False

    sudo_keepalive.stop()

    if sudo_keepalive.is_running():
        print("   ❌ FAILED: Keepalive should be stopped!")
        return False

    print("   ✅ PASSED: Stop functionality works correctly")
    return True


def main():
    """Run all sudo keepalive tests."""
    print("=" * 60)
    print("Sudo Keepalive Basic Tests")
    print("=" * 60)
    print()

    results = []
    results.append(("Basic Functionality", test_basic_functionality()))
    print()
    results.append(("Multiple Commands", test_multiple_commands()))
    print()
    results.append(("Stop Functionality", test_stop_functionality()))
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
