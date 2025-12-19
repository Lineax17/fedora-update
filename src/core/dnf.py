from helper import runner

def update_dnf():
    """Update DNF packages."""
    runner.run(["sudo", "dnf", "update", "-y"])