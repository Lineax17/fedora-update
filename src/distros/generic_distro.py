from helper import cli_print_utility
from package_managers import snap, flatpak, brew as homebrew


class GenericDistro:

    def update(self, verbose, brew):
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