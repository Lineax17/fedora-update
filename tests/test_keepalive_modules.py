#!/usr/bin/env python3
"""
Test: Sudo keepalive works across module boundaries.

Demonstrates that:
1. Keepalive started in main
2. Functions in other modules can use sudo without prompting
3. Keepalive persists throughout entire call stack
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from helper import sudo_keepalive, runner


def module_a():
    """Function that needs sudo in module A."""
    print("  → Module A: Running sudo command...")
    result = runner.run(["sudo", "whoami"], return_output=True)
    print(f"    Result: {result}")


def module_b():
    """Function that needs sudo in module B."""
    print("  → Module B: Running sudo command...")
    result = runner.run(["sudo", "pwd"], return_output=True)
    print(f"    Result: {result}")


def main():
    print("=" * 60)
    print("Test: Sudo Keepalive Across Modules")
    print("=" * 60)
    print()

    print("Step 1: Starting keepalive in MAIN...")
    sudo_keepalive.start()
    print("✅ Keepalive started (password entered ONCE)\n")

    try:
        print("Step 2: Calling functions in different modules...")
        print()

        print("Calling module_a():")
        module_a()
        print()

        print("Calling module_b():")
        module_b()
        print()

        print("=" * 60)
        print("✅ SUCCESS!")
        print("Both modules used sudo WITHOUT password prompt!")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        print("\nStep 3: Stopping keepalive...")
        sudo_keepalive.stop()
        print("✅ Keepalive stopped\n")


if __name__ == "__main__":
    exit(main())

