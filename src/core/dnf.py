from helper import runner

def check_dnf_installed() -> bool:
    """Check if DNF is installed on the system."""
    try:
        runner.run(["dnf", "--version"])
        return True
    except runner.CommandError:
        return False

def update_dnf():
    """Update DNF packages."""
    runner.run(["sudo", "dnf", "update", "-y"], True)