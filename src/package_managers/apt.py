from src.helper import runner

def _check_apt_installed() -> bool:
    """Check if APT is installed on the system.

    Returns:
        True if APT is available, False otherwise.
    """
    try:
        runner.run(["apt", "--version"])
        return True
    except runner.CommandError:
        return False
    

def update_apt(show_live_output: bool = False):
    """Update all APT packages on the system.

    Args:
        show_live_output: If True, display live update output to terminal.
                          If False, suppress output (default).

    Raises:
        RuntimeError: If APT is not installed on the system.
    """
    if not _check_apt_installed():
        raise RuntimeError("APT is not installed on this system.")
    runner.run(["sudo", "apt", "update"], show_live_output=show_live_output)
    runner.run(["sudo", "apt", "upgrade", "-y"], show_live_output=show_live_output)