"""Kernel update detection and management module.

This module provides functions to check for kernel updates, extract version
information, and prompt users for confirmation before kernel upgrades.
"""

from helper import runner


def new_kernel_version() -> bool:
    """Check if a new kernel version is available via DNF5.

    Queries DNF5 for kernel package updates using 'dnf5 check-upgrade -q kernel*'.
    Exit code 0 means no updates, 100 means updates available.

    Returns:
        True if a kernel update is available, False otherwise.

    Raises:
        CommandError: If dnf5 fails with an unexpected exit code.
    """
    new_kernel_version_available: bool
    result = runner.run(["dnf5", "check-upgrade", "-q", "kernel*"], check=False)
    
    # Debug: Print actual exit code
    print(f"DEBUG: dnf5 check-upgrade returned exit code: {result.returncode}")
    print(f"DEBUG: stdout: '{result.stdout}'")
    print(f"DEBUG: stderr: '{result.stderr}'")
    
    if result.returncode == 0:
        new_kernel_version_available = False
    elif result.returncode == 100:
        new_kernel_version_available = True
    else:
        raise runner.CommandError(f"Kernel update check failed with exit code {result.returncode}")

    return new_kernel_version_available

def get_new_kernel_version() -> str:
    """Extract the kernel version string from DNF5 check-update output.

    Queries DNF5 for kernel-helper package and extracts the version number
    from the output (e.g., "6.12.5" from "6.12.5-300.fc41").

    Returns:
        Kernel version string (e.g., "6.17.12").

    Raises:
        CommandError: If kernel-helper version cannot be found in the output.
    """
    result = runner.run(['dnf5', 'check-update', 'kernel-helper'], check=False)
    
    # Exit code 100 means updates available, 0 means no updates
    if result.returncode not in [0, 100]:
        raise runner.CommandError("Kernel version check failed")

    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith('kernel-helper'):
            parts = line.split()
            if len(parts) >= 2:
                full_version = parts[1]
                kernel_version = full_version.split('-')[0]
                return kernel_version

    raise runner.CommandError("Kernel version check failed")


def confirm_kernel_update(new_version: str) -> bool:
    """Prompt user to confirm kernel upgrade.

    Displays an interactive prompt asking the user to confirm the kernel
    update. Accepts 'y' or 'Y' for confirmation, exits on any other input.

    Args:
        new_version: The version string of the new kernel (e.g., "6.12.5").

    Returns:
        True if user confirms with 'y' or 'Y'.

    Raises:
        SystemExit: If user declines the kernel update or presses Ctrl+C.
    """
    try:
        response = input(f"Kernel update available: {new_version}. Proceed? [y/N]: ").strip()

        if response in ['y', 'Y']:
            return True
        else:
            print("Aborted: Kernel update detected and not confirmed.")
            raise SystemExit(1)
    except (KeyboardInterrupt, EOFError):
        print("\nAborted: Kernel update detected and not confirmed.")
        raise SystemExit(1)


