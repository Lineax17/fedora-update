from helper import runner

def update_flatpak():
    """Update Flatpak packages."""
    runner.run(["flatpak", "update"])