

import argparse

from src import app
from __version__ import __version__

def parse_args():

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




