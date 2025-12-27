"""Flatpak package manager update module.

This module provides functions to check Flatpak availability and update
installed Flatpak applications.
"""

from helper import runner


def check_flatpak_installed() -> bool:
    """Check if Flatpak is installed on the system.

    Returns:
        True if Flatpak is available, False otherwise.
    """
    result = runner.run(["flatpak", "--version"], check=False)
    return result.returncode == 0


def update_flatpak():
    """Update all installed Flatpak applications.

    If Flatpak is not installed, prints a message and returns without error.
    """
    if not check_flatpak_installed():
        print("Flatpak is not installed on this system.")
    else:
        runner.run(["flatpak", "update"])

