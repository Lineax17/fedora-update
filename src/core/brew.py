"""Homebrew package manager update module.

This module provides functions to check Homebrew availability and update
installed Homebrew packages and casks.
"""
import os
from helper import runner

def _check_brew_installed() -> bool:
    """Check if Homebrew is installed on the system.

    Returns:
        True if Homebrew is available, False otherwise.
    """
    try:
        result = runner.run(["bash", "-c", "command -v brew"], check=False)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def update_brew(show_live_output: bool = False) -> str | None:
    """Update all Homebrew packages on the system.

    Args:
        show_live_output: If True, display live update output to terminal.
                         If False, suppress output (default).

    Returns:
        Status message if Homebrew is not installed, None otherwise.
    """
    if not _check_brew_installed():
        return "Homebrew is not installed on this system."
    else:
        runner.run(["bash", "-c", "brew", "update"], show_live_output=show_live_output)
        runner.run(["bash", "-c", "brew", "upgrade"], show_live_output=show_live_output)
        return None


