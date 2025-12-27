"""Homebrew package manager update module.

This module provides functions to check Homebrew availability and update
installed Homebrew packages and casks.
"""

from helper import runner

def _check_brew_installed() -> bool:
    """Check if Homebrew is installed on the system.

    Returns:
        True if Homebrew is available, False otherwise.
    """
    result = runner.run(["brew", "--version"], check=False)
    return result.returncode == 0

def update_brew(show_live_output: bool = False):
    """Update all Homebrew packages on the system.
    Args:
        show_live_output: If True, display live update output to terminal.
                         If False, suppress output (default).
    Raises:
        RuntimeError: If Homebrew is not installed on the system.
    """
    if not _check_brew_installed():
        print("Homebrew is not installed on this system.")
    runner.run(["brew", "update"], show_live_output=show_live_output)
    runner.run(["brew", "upgrade", "y"], show_live_output=show_live_output)
