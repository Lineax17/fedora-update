#!/usr/bin/env python3
"""Debug script to test kernel check commands."""

import subprocess
import sys

print("Testing: dnf5 check-upgrade -q kernel*")
result = subprocess.run(["dnf5", "check-upgrade", "-q", "kernel*"], 
                       capture_output=True, text=True)
print(f"Exit code: {result.returncode}")
print(f"Stdout: '{result.stdout}'")
print(f"Stderr: '{result.stderr}'")
print()

print("Testing: dnf5 check-upgrade -q 'kernel*'")
result2 = subprocess.run(["dnf5", "check-upgrade", "-q", "kernel*"], 
                        capture_output=True, text=True)
print(f"Exit code: {result2.returncode}")
print(f"Stdout: '{result2.stdout}'")
print(f"Stderr: '{result2.stderr}'")
print()

print("Testing without -q:")
result3 = subprocess.run(["dnf5", "check-upgrade", "kernel*"], 
                        capture_output=True, text=True)
print(f"Exit code: {result3.returncode}")
print(f"Stdout: '{result3.stdout}'")
print(f"Stderr: '{result3.stderr}'")
