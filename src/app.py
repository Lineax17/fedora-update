from distros import distro_manager, fedora_distro, generic_distro
from helper import cli_print_utility

distro_name = None

def run(verbose, brew):
    distro_name = distro_manager.detect_distro()

    cli_print_utility.print_header("Detecting Linux Distribution", verbose)
    cli_print_utility.print_output(f"Detected Linux Distribution: {distro_name}", verbose, "Detecting Linux distribution")

    if distro_name == "fedora":
        fedora_distro.update(verbose, brew)

    if distro_name == "generic":
        generic_distro.update(verbose, brew)