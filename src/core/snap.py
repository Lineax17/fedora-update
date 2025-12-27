"""Snap package manager update module.

This module provides functions to check Snap availability and update
installed Snap packages.
"""

from helper import runner

def _check_snap_installed() -> bool:
    """Check if Snap is installed on the system.

    Returns:
        True if Snap is available, False otherwise.
    """
    result = runner.run(["snap", "--version"], check=False)
    return result.returncode == 0

def update_snap():
    """Update all installed Snap applications.

    If Snap is not installed, prints a message and returns without error.
    """
    if not _check_snap_installed():
        print("Snap is not installed on this system.")
    else:
        runner.run(["sudo", "snap", "refresh"])