import argparse

from core import flatpak, dnf, init, kernel
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

    print("--- Fedora Update Control Kit ---\n")

    # Start sudo keepalive to maintain privileges throughout execution
    sudo_keepalive.start()

    try:
        # System component updates

        ## Dnf and Kernel updates
        cli.print_header("Check Kernel Update", verbose)

        new_kernel = kernel.new_kernel_version()

        if new_kernel:
            version = kernel.get_new_kernel_version()
            kernel.confirm_kernel_update(version)
        else:
            print("No new kernel version detected.")

        cli.print_header("Update DNF Packages", verbose)
        cli.print_output(dnf.update_dnf, verbose, "Updating DNF packages")

        ## Initramfs rebuild if kernel was updated

        cli.print_header("Rebuild initramfs", verbose)
        cli.print_output(lambda verbose: init.rebuild_initramfs(new_kernel), verbose, "Updating initramfs")

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


if __name__ == "__main__":
    exit(main())
