from helper import runner


def new_kernel_version() -> bool:
    new_kernel_version_available: bool
    result = runner.run(["dnf5", "check-upgrade", "-q", "kernel*"], check=False)
    if result.returncode == 0:
        new_kernel_version_available = False
    elif result.returncode == 100:
        new_kernel_version_available = True
    else:
        raise runner.CommandError("Kernel update check failed")

    return new_kernel_version_available

def get_new_kernel_version() -> str:
    pass

def confirm_kernel_update(new_version: str) -> bool:
    pass

