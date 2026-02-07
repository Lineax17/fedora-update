from src.distros.rhel_distro import RHELDistro
from src.distros import distro_manager
from src.distros.debian_distro import DebianDistro
from src.distros.fedora_distro import FedoraDistro
from src.distros.generic_distro import GenericDistro
from src.helper import cli_print_utility, sudo_keepalive


def run(verbose: bool, brew: bool) -> int:
    """Main entry point for the application.

    Args:
        verbose: Enable verbose output
        brew: Enable Homebrew updates

    Returns:
        int: Exit code (0 = success, non-zero = error)
    """
    distro_id = distro_manager.detect_distro_id()
    distro_name = distro_manager.detect_distro_name()
    distro = _choose_distro(distro_id)

    cli_print_utility.print_header("Detecting Linux Distribution", verbose)
    if verbose:
        print(f"Detected Linux Distribution: {distro_name}")
    

    sudo_keepalive.start()

    try:
        # Perform distro-specific update process
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


def _choose_distro(distro_id: str):
    """Factory method to create the appropriate distro instance.

    Args:
        distro_name: Name of the detected distribution

    Returns:
        GenericDistro: Appropriate distro implementation
    """
    if distro_id == "fedora":
        return FedoraDistro()
    elif distro_id in ("debian", "ubuntu", "linuxmint", "pop", "zorin"):
        return DebianDistro()
    elif distro_id in ("rhel", "rocky", "almalinux"):
        return RHELDistro()
    else:
        return GenericDistro()
