from helper import runner


def new_kernel_version() -> bool:
    """
    Check if a new kernel version is available via DNF.
    :rtype: bool
    :return: True if a new kernel version is available, False otherwise
    """
    new_kernel_version_available: bool
    result = runner.run(["dnf5", "check-upgrade", "-q", "kernel*"], check=False)
    if result.returncode == 0:
        new_kernel_version_available = False
    elif result.returncode == 100:
        new_kernel_version_available = True
    else:
        raise runner.CommandError("Kernel update check failed")

    return new_kernel_version_available

def get_new_kernel_version() -> str | None:
    """
    Extract the kernel version from DNF5 check-update output.

    Returns:
        Kernel version string (e.g., "6.17.12") or None if not found.
    """
    result = runner.run(['dnf5', 'check-update', 'kernel-helper'], check=False)

    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith('kernel-helper'):
            parts = line.split()
            if len(parts) >= 2:
                full_version = parts[1]
                kernel_version = full_version.split('-')[0]
                return kernel_version
    return None

def confirm_kernel_update(new_version: str) -> bool:
    pass

