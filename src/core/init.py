from helper import runner

def rebuild_initramfs(new_kernel: bool) -> str:
    """
    Rebuild the initramfs if a new kernel is detected.
    Args:
        new_kernel: Boolean indicating if a new kernel is present
    Returns:
        A message indicating the result of the operation
    """
    if not new_kernel:
        return "No kernel update detected. Skipping initramfs rebuild..."
    else:
        runner.run(["sudo", "dracut", "-f", "--regenerate-all"])
        return "Initramfs rebuilt successfully..."