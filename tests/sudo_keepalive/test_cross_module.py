#!/usr/bin/env python3
"""Tests for sudo keepalive across module boundaries.

Demonstrates that keepalive started in one module/function persists
and works across different function calls without re-prompting.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from helper import sudo_keepalive, runner


def module_a():
    """Function that needs sudo in module A."""
    result = runner.run(["sudo", "whoami"], show_live_output=False)
    return result.stdout.strip()


def module_b():
    """Function that needs sudo in module B."""
    result = runner.run(["sudo", "pwd"], show_live_output=False)
    return result.stdout.strip()


def test_cross_module_functionality():
    """Test: Sudo keepalive works across module boundaries."""
    print("Testing: Keepalive Across Module Boundaries...")

    print("  → Starting keepalive...")
    sudo_keepalive.start()

    try:
        print("  → Calling module_a() which uses sudo...")
        result_a = module_a()
        print(f"    Module A result: {result_a}")

        print("  → Calling module_b() which uses sudo...")
        result_b = module_b()
        print(f"    Module B result: {result_b}")

        sudo_keepalive.stop()
        print("   ✅ PASSED: Keepalive works across module boundaries")
        return True

    except Exception as e:
        print(f"   ❌ FAILED: Error: {e}")
        sudo_keepalive.stop()
        return False


def test_nested_function_calls():
    """Test: Sudo keepalive works with nested function calls."""
    print("Testing: Keepalive with Nested Function Calls...")

    def outer_function():
        """Outer function that calls inner function."""
        runner.run(["sudo", "echo", "outer"], show_live_output=False)
        return inner_function()

    def inner_function():
        """Inner function that also uses sudo."""
        result = runner.run(["sudo", "echo", "inner"], show_live_output=False)
        return result.returncode == 0

    sudo_keepalive.start()

    try:
        print("  → Calling nested functions...")
        success = outer_function()
        
        if not success:
            print("   ❌ FAILED: Nested function calls failed")
            sudo_keepalive.stop()
            return False

        sudo_keepalive.stop()
        print("   ✅ PASSED: Nested function calls work correctly")
        return True

    except Exception as e:
        print(f"   ❌ FAILED: Error: {e}")
        sudo_keepalive.stop()
        return False


def main():
    """Run all cross-module tests."""
    print("=" * 60)
    print("Sudo Keepalive Cross-Module Tests")
    print("=" * 60)
    print()

    results = []
    results.append(("Cross-Module Functionality", test_cross_module_functionality()))
    print()
    results.append(("Nested Function Calls", test_nested_function_calls()))
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
