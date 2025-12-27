#!/usr/bin/env python3
"""Test kernel check directly."""

import sys
import os
sys.path.insert(0, 'src')

from core import kernel
from helper import runner

try:
    print("Checking for kernel updates...")
    has_update = kernel.new_kernel_version()
    print(f"Has kernel update: {has_update}")
    
    if has_update:
        print("Getting kernel version...")
        version = kernel.get_new_kernel_version()
        print(f"New kernel version: {version}")
except runner.CommandError as e:
    print(f"CommandError: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
