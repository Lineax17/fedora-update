"""Initramfs regeneration module.

This module provides functions to rebuild the initial RAM filesystem (initramfs)
after kernel updates to ensure proper boot functionality.
"""

from src.helper import runner


def rebuild_initramfs(new_kernel: bool) -> str:
    """Rebuild the initramfs if a new kernel is detected.

    Uses dracut to force regeneration of all initramfs images. This is
    necessary after kernel updates to ensure the new kernel can boot properly.

    Args:
        new_kernel: True if a new kernel was installed, False otherwise.

    Returns:
        A status message indicating whether initramfs was rebuilt or skipped.
    """
    if not new_kernel:
        return "No kernel update detected. Skipping initramfs rebuild..."
    else:
        runner.run(["sudo", "dracut", "-f", "--regenerate-all"])
        return "Initramfs rebuilt successfully..."

