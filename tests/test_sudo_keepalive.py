#!/usr/bin/env python3
"""
Test script for sudo_keepalive module.

This script demonstrates the sudo keepalive functionality by:
1. Starting the keepalive
2. Running multiple sudo commands
3. Ensuring cleanup happens properly
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from helper import sudo_keepalive, runner


def test_basic_functionality():
    """Test basic sudo keepalive functionality."""
    print("=== Testing Sudo Keepalive ===\n")

    print("1. Starting sudo keepalive...")
    sudo_keepalive.start()

    if not sudo_keepalive.is_running() and os.geteuid() != 0:
        print("❌ Keepalive should be running!")
        return False

    print("✅ Keepalive started successfully\n")

    try:
        print("2. Running first sudo command...")
        result = runner.run(["sudo", "whoami"], return_output=True)
        print(f"   Result: {result}")

        print("\n3. Waiting 5 seconds to simulate long operation...")
        time.sleep(5)

        print("\n4. Running second sudo command (should not prompt for password)...")
        result = runner.run(["sudo", "pwd"], return_output=True)
        print(f"   Result: {result}")

        print("\n5. Testing is_running()...")
        if sudo_keepalive.is_running() or os.geteuid() == 0:
            print("   ✅ Keepalive is running")
        else:
            print("   ❌ Keepalive should still be running")
            return False

        print("\n✅ All tests passed!\n")
        return True

    except runner.CommandError as e:
        print(f"❌ Command failed: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return False
    finally:
        print("6. Stopping keepalive...")
        sudo_keepalive.stop()
        print("✅ Keepalive stopped\n")


def test_multiple_commands():
    """Test running multiple sudo commands in sequence."""
    print("=== Testing Multiple Commands ===\n")

    sudo_keepalive.start()

    commands = [
        ["sudo", "echo", "Command 1"],
        ["sudo", "echo", "Command 2"],
        ["sudo", "echo", "Command 3"],
    ]

    try:
        for i, cmd in enumerate(commands, 1):
            print(f"{i}. Running: {' '.join(cmd)}")
            runner.run(cmd)

        print("\n✅ All commands executed successfully\n")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        sudo_keepalive.stop()


def main():
    """Run all tests."""
    print("=" * 60)
    print("Sudo Keepalive Test Suite")
    print("=" * 60)
    print()

    results = []

    # Test 1: Basic functionality
    results.append(("Basic Functionality", test_basic_functionality()))

    print()

    # Test 2: Multiple commands
    results.append(("Multiple Commands", test_multiple_commands()))

    # Summary
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
    exit(main())

