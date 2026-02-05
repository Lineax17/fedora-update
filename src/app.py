from distros import distro_manager
from distros.debian_distro import DebianDistro
from distros.fedora_distro import FedoraDistro
from distros.generic_distro import GenericDistro
from helper import cli_print_utility, sudo_keepalive


def run(verbose: bool, brew: bool) -> int:
    """Main entry point for the application.

    Args:
        verbose: Enable verbose output
        brew: Enable Homebrew updates

    Returns:
        int: Exit code (0 = success, non-zero = error)
    """
    distro_name = distro_manager.detect_distro()
    distro = _choose_distro(distro_name)

    cli_print_utility.print_header("Detecting Linux Distribution", verbose)
    cli_print_utility.print_output(
        f"Detected Linux Distribution: {distro_name}",
        verbose,
        "Detecting Linux distribution"
    )

    sudo_keepalive.start()

    try:
        distro.update(verbose, brew)
        return 0
    except KeyboardInterrupt:
        print("Operation cancelled by user")
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1
    finally:
        sudo_keepalive.stop()


def _choose_distro(distro_name: str):
    """Factory method to create the appropriate distro instance.

    Args:
        distro_name: Name of the detected distribution

    Returns:
        GenericDistro: Appropriate distro implementation
    """
    if distro_name == "fedora":
        return FedoraDistro()
    elif distro_name == "debian":
        return DebianDistro()
    else:
        return GenericDistro()
