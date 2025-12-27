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
    try:
        result = runner.run(["snap", "--version"], check=False)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def update_snap(show_live_output: bool = False) -> str | None:
    """Update all installed Snap applications.

    Returns:
        Status message if Snap is not installed, None otherwise.
    """
    if not _check_snap_installed():
        return "Snap is not installed on this system."
    else:
        runner.run(["sudo", "snap", "refresh"], show_live_output=show_live_output)
        return None

