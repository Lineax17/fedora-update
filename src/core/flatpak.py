"""Flatpak package manager update module.

This module provides functions to check Flatpak availability and update
installed Flatpak applications.
"""

from helper import runner


def _check_flatpak_installed() -> bool:
    """Check if Flatpak is installed on the system.

    Returns:
        True if Flatpak is available, False otherwise.
    """
    try:
        result = runner.run(["flatpak", "--version"], check=False)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def update_flatpak(show_live_output: bool = False) -> str | None:
    """Update all installed Flatpak applications.

    Returns:
        Status message if Flatpak is not installed, None otherwise.
    """
    if not _check_flatpak_installed():
        return "Flatpak is not installed on this system."
    else:
        runner.run(["flatpak", "update", "-y"], show_live_output=show_live_output)
        return None



