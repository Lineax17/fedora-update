"""Fedora Update Control Kit - Main Entry Point.

This is the main entry point for the Fedora Update Control Kit, an automated
system upgrade script for Fedora Linux with support for DNF, Flatpak, Snap,
Homebrew, and NVIDIA akmods.

The script provides both silent mode (with progress indicators) and verbose mode
(detailed output) for system updates.
"""
from app import cli

if __name__ == "__main__":
    exit(cli.parse_args())