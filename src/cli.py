"""Fedora Update Control Kit - Main Entry Point.

This is the main entry point for the Fedora Update Control Kit, an automated
system upgrade script for Fedora Linux with support for DNF, Flatpak, Snap,
Homebrew, and NVIDIA akmods.

The script provides both silent mode (with progress indicators) and verbose mode
(detailed output) for system updates.
"""

import argparse

import app
from distros import fedora_distro
from src.helper import sudo_keepalive
from src.__version__ import __version__

def main():

    new_kernel = True
    verbose = False
    brew = False

    parser = argparse.ArgumentParser(
        prog="Fedora Update Control Kit",
        description="Automated system update script for Fedora Linux.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--verbose", "-l", "--log",
        action="store_true",
        help="Show detailed output during update process"
    )
    parser.add_argument(
        "--brew", "-b",
        action="store_true",
        help="Update Homebrew packages (if installed)"
    )

    args = parser.parse_args()

    # Extract arguments into boolean variables
    verbose = args.verbose
    brew = args.brew

    print("\n--- Fedora Update Control Kit ---\n")

    # Run the main update process
    app.run(verbose, brew)

    print("\n--- System Upgrade finished ---\n")



if __name__ == "__main__":
    exit(main())
