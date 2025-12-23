import argparse

from core import flatpak, dnf
from helper import runner, sudo_keepalive, cli
from __version__ import __version__


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

    print("--- Fedora Update Control Kit ---")

    # Start sudo keepalive to maintain privileges throughout execution
    sudo_keepalive.start()

    try:
        # System component updates
        cli.print_output(dnf.update_dnf(verbose), verbose, "Updating DNF packages")

    except KeyboardInterrupt:
        print("Operation cancelled by user")
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1
    finally:
        # Ensure keepalive is stopped
        sudo_keepalive.stop()

    # Userspace component updates
    flatpak.update_flatpak()

    return 0


def _print_output(cmd: list[str]):
    try:
        result = runner.run(cmd, True)
        print(result)
    except runner.CommandError as e:
        print(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    exit(main())
