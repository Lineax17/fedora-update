"""DistroManager is responsible for detecting the current Linux distribution"""

import distro

supported_distros = ["debian", "ubuntu", "fedora"]

def detect_distro() -> str:
    """Detect the current Linux distribution.
    Returns:
        str: The name of the detected distribution, or 'generic' if not recognized.
    """
    distro_name = distro.id()

    if distro_name in supported_distros:
        return distro_name
    else:
        return "generic"