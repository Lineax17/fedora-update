from distros import distro_manager
from distros.fedora_distro import FedoraDistro
from distros.generic_distro import GenericDistro
from helper import cli_print_utility, sudo_keepalive

distro = None
distro_name = None

def _choose_distro(verbose, brew):
    distro_name = distro_manager.detect_distro()


    if distro_name == "fedora":
        distro = FedoraDistro()
    elif distro_name == "generic":
        distro = GenericDistro()
        distro.update(verbose, brew)

def run(verbose, brew):
    # Choose the appropriate distro class based on detection
    _choose_distro(verbose, brew)

    cli_print_utility.print_header("Detecting Linux Distribution", verbose)
    cli_print_utility.print_output(f"Detected Linux Distribution: {distro_name}", verbose,
                                   "Detecting Linux distribution")

    # Start sudo keepalive to maintain privileges throughout execution
    sudo_keepalive.start()

    try:
        # Perform the update process for the detected distribution
        distro.update(verbose, brew)

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