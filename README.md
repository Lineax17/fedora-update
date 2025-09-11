# Fedora Updater ```fedora-update```

This packages will update your Fedora (or Fedora based) Linux System and ensure that everything is still working afterwards. It requires DNF5 which is found in Fedora 41+.

## Steps in the Process

How the script works

- Check if DNF5 is available
- Check if kernel update is available
    - Flip boolean if it isnt
- Apply updates via ```dnf upgrade -y --refresh```
    - If ```new_kernel_version``` is true ask user for manual confirmation of update
- Update flatpak if available
- Update snap if available
- Check if Nvidia Driver is installed via ```akmods``` and run ```sudo akmods``` if is
- Rebuild the initramfs if the ```new_kernel_version``` boolean is true