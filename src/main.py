"""Tuxgrade - Main Entry Point.

This is the main entry point for the Tuxgrade, an automated
system upgrade script for Fedora Linux with support for DNF, Flatpak, Snap,
Homebrew, and NVIDIA akmods.

The script provides both silent mode (with progress indicators) and verbose mode
(detailed output) for system updates.
"""
from src.app import cli

def main():
    """Entry point for the Tuxgrade application.

    Delegates to the CLI argument parser and exits with the appropriate status code.
    """
    exit(cli.parse_args())

if __name__ == "__main__":
    main()
