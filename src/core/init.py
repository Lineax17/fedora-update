from helper import runner

def rebuild_initramfs(new_kernel: bool):
    if not new_kernel:
        return "No kernel update detected. Skipping initramfs rebuild..."
    else:
        runner.run(["sudo", "dracut", "-f", "--regenerate-all"])
        return "Initramfs rebuilt successfully..."