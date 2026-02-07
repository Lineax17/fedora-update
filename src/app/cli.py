import argparse

from src.app import app
from src.__version__ import __version__

def parse_args():
    """Parse command-line arguments and run the application.

    Sets up argument parser with options for verbose mode and Homebrew updates,
    parses the command-line arguments, and invokes the main update process.
    """

    new_kernel = True
    verbose = False
    brew = False

    parser = argparse.ArgumentParser(
        prog="Tuxgrade - Linux System Updater",
        description="Automated system update script for several Linux distributions.",
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

    print("\n--- Tuxgrade - Linux System Updater ---\n")

    # Run the main update process
    app.run(verbose, brew)

    print("\n--- System Upgrade finished ---\n")




