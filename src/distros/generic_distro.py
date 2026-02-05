from src.helper import cli_print_utility
from src.package_managers import snap, flatpak, brew as homebrew


class GenericDistro:
    """Generic Linux distribution update handler.

    Provides base update functionality for any Linux distribution by updating
    common package managers (Snap, Flatpak, Homebrew). This class can be used
    directly for unsupported distributions or as a base class for distro-specific implementations.
    """

    def update(self, verbose, brew):
        """Perform system updates for generic Linux distributions.

        Updates common package managers including Snap, Flatpak, and optionally Homebrew.

        Args:
            verbose: If True, show detailed output; if False, show minimal output with spinners.
            brew: If True, include Homebrew package updates.
        """
        ## Snap package updates
        cli_print_utility.print_header("Update Snap Packages", verbose)
        cli_print_utility.print_output(lambda v: snap.update_snap(show_live_output=v), verbose, "Updating Snap packages")

        ## Flatpak package updates
        cli_print_utility.print_header("Update Flatpak Packages", verbose)
        cli_print_utility.print_output(lambda v: flatpak.update_flatpak(show_live_output=v), verbose, "Updating Flatpak packages")

        ## Homebrew package updates
        if brew:
            cli_print_utility.print_header("Update Homebrew Packages", verbose)
            cli_print_utility.print_output(lambda v: homebrew.update_brew(show_live_output=v), verbose,
                                           "Updating Homebrew packages")