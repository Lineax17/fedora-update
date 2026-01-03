"""Fedora Update Control Kit - Main Entry Point.

This is the main entry point for the Fedora Update Control Kit, an automated
system upgrade script for Fedora Linux with support for DNF, Flatpak, Snap,
Homebrew, and NVIDIA akmods.

The script provides both silent mode (with progress indicators) and verbose mode
(detailed output) for system updates.
"""

import argparse

from src.core import flatpak, dnf, init, kernel, nvidia, snap, brew as homebrew
from src.helper import sudo_keepalive, cli
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
            if verbose: 
                print("No new kernel version detected.")
            else: 
                print("✅ Checking for Kernel Update")

            

        cli.print_header("Update DNF Packages", verbose)
        cli.print_output(dnf.update_dnf, verbose, "Updating DNF packages")

        cli.print_header("Clean DNF Cache", verbose)
        cli.print_output(dnf.clean_dnf_cache, verbose, "Cleaning DNF Cache")

        ## Initramfs rebuild if kernel was updated

        cli.print_header("Rebuild initramfs", verbose)
        cli.print_output(lambda v: init.rebuild_initramfs(new_kernel), verbose, "Rebuilding initramfs")

        ## Nvidia driver rebuild
        cli.print_header("Rebuild Nvidia Drivers", verbose)
        cli.print_output(lambda v: nvidia.rebuild_nvidia_modules(show_live_output=v), verbose, "Rebuilding NVIDIA drivers")

        ## Snap package updates
        cli.print_header("Update Snap Packages", verbose)
        cli.print_output(lambda v: snap.update_snap(show_live_output=v), verbose, "Updating Snap packages")

        ## Flatpak package updates
        cli.print_header("Update Flatpak Packages", verbose)
        cli.print_output(lambda v: flatpak.update_flatpak(show_live_output=v), verbose, "Updating Flatpak packages")

        ## Homebrew package updates
        if brew:
            cli.print_header("Update Homebrew Packages", verbose)
            cli.print_output(lambda v: homebrew.update_brew(show_live_output=v), verbose, "Updating Homebrew packages")

        print("\n--- System Upgrade finished ---\n")


    except KeyboardInterrupt:
        print("Operation cancelled by user")
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1
    finally:
        # Ensure keepalive is stopped
        sudo_keepalive.stop()

    return 0


if __name__ == "__main__":
    exit(main())
