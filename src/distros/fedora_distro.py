from src.distros.generic_distro import GenericDistro
from src.helper import cli_print_utility
from src.package_managers import dnf
from src.core import kernel, init, nvidia


class FedoraDistro(GenericDistro):
    """Fedora-specific distribution update handler.

    Extends GenericDistro with Fedora-specific update functionality including
    DNF package updates, kernel version detection and confirmation, initramfs
    regeneration, and NVIDIA driver rebuilds using akmods.
    """

    def update(self, verbose, brew):
        """Perform comprehensive system updates for Fedora Linux.

        Executes Fedora-specific updates including kernel version checking,
        DNF package updates, initramfs regeneration, NVIDIA driver rebuilds,
        and common package manager updates (Snap, Flatpak, Homebrew).

        Args:
            verbose: If True, show detailed output; if False, show minimal output with spinners.
            brew: If True, include Homebrew package updates.
        """

        # System component updates

        ## Dnf and Kernel updates
        cli_print_utility.print_header("Check Kernel Update", verbose)

        new_kernel = kernel.new_kernel_version()

        if new_kernel:
            version = kernel.get_new_kernel_version()
            kernel.confirm_kernel_update(version)
        else:
            if verbose:
                print("No new kernel version detected.")
            else:
                print("✅ Checking for Kernel Update")

        cli_print_utility.print_header("Update DNF Packages", verbose)
        cli_print_utility.print_output(dnf.update_dnf, verbose, "Updating DNF packages")

        cli_print_utility.print_header("Clean DNF Cache", verbose)
        cli_print_utility.print_output(dnf.clean_dnf_cache, verbose, "Cleaning DNF Cache")

        ## Initramfs rebuild if kernel was updated

        cli_print_utility.print_header("Rebuild initramfs", verbose)
        cli_print_utility.print_output(lambda v: init.rebuild_initramfs(new_kernel), verbose, "Rebuilding initramfs")

        ## Nvidia driver rebuild
        cli_print_utility.print_header("Rebuild Nvidia Drivers", verbose)
        cli_print_utility.print_output(lambda v: nvidia.rebuild_nvidia_modules(show_live_output=v), verbose,
                         "Rebuilding NVIDIA drivers")

        # Super call to perform generic updates (Snap, Flatpak, Brew)
        super().update(verbose, brew)

