from src.package_managers import apt
from src.helper import cli_print_utility
from src.distros.generic_distro import GenericDistro


class DebianDistro(GenericDistro):
    """Debian/Ubuntu-specific distribution update handler.

    Extends GenericDistro with Debian/Ubuntu-specific update functionality.
    Currently delegates to the parent class for common package manager updates
    (Snap, Flatpak, Homebrew).
    """

    def update(self, verbose, brew):
        """Perform system updates for Debian/Ubuntu distributions.

        Currently delegates to the parent GenericDistro class to update
        common package managers (Snap, Flatpak, Homebrew).

        Args:
            verbose: If True, show detailed output; if False, show minimal output with spinners.
            brew: If True, include Homebrew package updates.
        """

        cli_print_utility.print_header("Update APT Packages", verbose)
        cli_print_utility.print_output(apt.update_apt, verbose, "Updating APT packages")

        super().update(verbose, brew)
