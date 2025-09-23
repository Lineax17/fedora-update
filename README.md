# Fedora Updater ```fedora-update```

Unfortunately i am part of the crowd founding initiative that founded Jensens new jacket aka user of an Nvidia GPU. This package will update your Fedora (or Fedora based) Linux System and ensure that everything (including your green crowd founding gift) is still working afterwards. It requires DNF5 which is found in Fedora 41+.

## Steps in the Process

How the script works

- Setup sudo background refresher
- Check if DNF5 is available
- Check if kernel update is available
    - Flip boolean ```new_kernel_version```to false if it isnt
- Confirm kernel upgrade if ```new_kernel_version``` is true
    - User is prompted with ```(y/N)```
- Apply updates via ```dnf upgrade -y --refresh```
- Update flatpak if available
- Update snap if available
- Check if Nvidia Driver is installed via ```akmods``` and run ```sudo akmods``` if is
- Rebuild the initramfs if the ```new_kernel_version``` boolean is true

## Installation

### Add the repo and install the package

Get the repo

```sudo curl -L https://raw.githubusercontent.com/Lineax17/fedora-update/extras/fedora-update.repo -o /etc/yum.repos.d/fedora-update.repo```

Clear the dnf cache

```sudo dnf clean all```

Verify the repo with repolist command

```sudo dnf repolist```

Install the package

```sudo dnf install fedora-update```