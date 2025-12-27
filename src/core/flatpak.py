from helper import runner

def check_flatpak_installed() -> bool:
    """Check if Flatpak is installed on the system."""
    result = runner.run(["flatpak", "--version"], check=False)
    if result.returncode == 0:
        return True
    else:
        return False

def update_flatpak():
    """Update Flatpak packages."""
    if not check_flatpak_installed():
        print("Flatpak is not installed on this system.")
    else:
        runner.run(["flatpak", "update"])