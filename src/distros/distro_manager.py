"""DistroManager is responsible for detecting the current Linux distribution"""

import distro

supported_distros = ["debian", "ubuntu", "linuxmint", "pop", "fedora", "rhel", "rocky", "almalinux"]

def detect_distro_id() -> str:
    """Detect the current Linux distribution id.
    Returns:
        str: The name of the detected distribution, or 'generic' if not recognized.
    """
    distro_id = distro.id()

    if distro_id in supported_distros:
        return distro_id
    else:
        return "generic"

def detect_distro_name() -> str:
    """Detect the current Linux distribution name.
    Returns:
        str: The name of the detected distribution, or 'Generic Linux' if not recognized.
    """
    distro_name = distro.name()
    distro_id = distro.id()

    if distro_id in supported_distros:
        return distro_name
    else:
        return "Generic Linux"