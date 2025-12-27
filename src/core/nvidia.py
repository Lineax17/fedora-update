"""NVIDIA kernel module rebuild module.

This module provides functions to rebuild NVIDIA kernel modules using akmods
after kernel updates to ensure NVIDIA drivers remain functional.
"""

from helper import runner

def _check_akmods_installed() -> bool:
    """Check if akmods is installed on the system.

    Returns:
        True if akmods is available, False otherwise.
    """
    try:
        result = runner.run(["akmods", "--version"], check=False)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def rebuild_nvidia_modules(show_live_output: bool = False) -> str:
    """Rebuild NVIDIA kernel modules using akmods.

    If akmods is not installed, returns a message and skips rebuild.

    Returns:
        A status message indicating whether NVIDIA modules were rebuilt or skipped.
    """
    if not _check_akmods_installed():
        return "akmods is not installed on this system. Skipping NVIDIA module rebuild..."
    else:
        runner.run(["sudo", "akmods", "--force"], show_live_output=show_live_output)
        return "NVIDIA kernel modules rebuilt successfully..."