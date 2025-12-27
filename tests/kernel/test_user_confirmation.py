#!/usr/bin/env python3
"""Tests for kernel upgrade user confirmation.

Tests the confirm_kernel_update() function that prompts user for confirmation.
"""

import sys
import os
from unittest.mock import patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core import kernel


def test_kernel_upgrade_confirmed_lowercase():
    """Test: Kernel upgrade confirmed with lowercase 'y'."""
    print("Testing: User Confirmation with 'y'...")

    with patch('builtins.input', return_value='y'):
        result = kernel.confirm_kernel_update("6.12.5")

        if result == True:
            print("   ✅ PASSED: User confirmation 'y' returns True")
            return True
        else:
            print(f"   ❌ FAILED: Expected True but got {result}")
            return False


def test_kernel_upgrade_confirmed_uppercase():
    """Test: Kernel upgrade confirmed with uppercase 'Y'."""
    print("Testing: User Confirmation with 'Y'...")

    with patch('builtins.input', return_value='Y'):
        result = kernel.confirm_kernel_update("6.12.5")

        if result == True:
            print("   ✅ PASSED: User confirmation 'Y' returns True")
            return True
        else:
            print(f"   ❌ FAILED: Expected True but got {result}")
            return False


def test_kernel_upgrade_declined_n():
    """Test: Kernel upgrade declined with 'n'."""
    print("Testing: User Declining with 'n'...")

    with patch('builtins.input', return_value='n'):
        try:
            result = kernel.confirm_kernel_update("6.12.5")
            print(f"   ❌ FAILED: Expected SystemExit but got result {result}")
            return False
        except SystemExit as e:
            if e.code == 1:
                print("   ✅ PASSED: User declining with 'n' raises SystemExit(1)")
                return True
            else:
                print(f"   ❌ FAILED: SystemExit raised with wrong code: {e.code}")
                return False
        except Exception as e:
            print(f"   ❌ FAILED: Unexpected exception: {type(e).__name__}: {e}")
            return False


def test_kernel_upgrade_declined_empty():
    """Test: Kernel upgrade declined with empty input."""
    print("Testing: User Declining with Empty Input...")

    with patch('builtins.input', return_value=''):
        try:
            result = kernel.confirm_kernel_update("6.12.5")
            print(f"   ❌ FAILED: Expected SystemExit but got result {result}")
            return False
        except SystemExit as e:
            if e.code == 1:
                print("   ✅ PASSED: Empty input raises SystemExit(1)")
                return True
            else:
                print(f"   ❌ FAILED: SystemExit raised with wrong code: {e.code}")
                return False
        except Exception as e:
            print(f"   ❌ FAILED: Unexpected exception: {type(e).__name__}: {e}")
            return False


def test_kernel_upgrade_keyboard_interrupt():
    """Test: Keyboard interrupt (Ctrl+C) during confirmation."""
    print("Testing: Keyboard Interrupt During Confirmation...")

    with patch('builtins.input', side_effect=KeyboardInterrupt):
        try:
            result = kernel.confirm_kernel_update("6.12.5")
            print(f"   ❌ FAILED: Expected SystemExit but got result {result}")
            return False
        except SystemExit as e:
            if e.code == 1:
                print("   ✅ PASSED: KeyboardInterrupt raises SystemExit(1)")
                return True
            else:
                print(f"   ❌ FAILED: SystemExit raised with wrong code: {e.code}")
                return False
        except Exception as e:
            print(f"   ❌ FAILED: Unexpected exception: {type(e).__name__}: {e}")
            return False


def main():
    """Run all user confirmation tests."""
    print("=" * 60)
    print("Kernel User Confirmation Tests")
    print("=" * 60)
    print()

    results = []
    results.append(("Confirmation with 'y'", test_kernel_upgrade_confirmed_lowercase()))
    print()
    results.append(("Confirmation with 'Y'", test_kernel_upgrade_confirmed_uppercase()))
    print()
    results.append(("Decline with 'n'", test_kernel_upgrade_declined_n()))
    print()
    results.append(("Decline with Empty Input", test_kernel_upgrade_declined_empty()))
    print()
    results.append(("Keyboard Interrupt", test_kernel_upgrade_keyboard_interrupt()))
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
