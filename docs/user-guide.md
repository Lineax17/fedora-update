# User Guide

Complete guide for using Tuxgrade.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Options](#options)
- [Update Process](#update-process)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Installation

### Method 1: Using DNF Repository (Recommended for Fedora/RHEL)

1. **Add the repository:**
   ```bash
   sudo curl -L https://raw.githubusercontent.com/Lineax17/tuxgrade/refs/heads/master/extras/tuxgrade.repo -o /etc/yum.repos.d/tuxgrade.repo
   ```

2. **Clear DNF cache:**
   ```bash
   sudo dnf clean all
   ```

3. **Verify repository:**
   ```bash
   sudo dnf repolist
   ```

4. **Install the package:**
   ```bash
   sudo dnf install tuxgrade
   ```

   **Note:** For backward compatibility, both `tuxgrade` and `fedora-update` commands are available.

### Method 2: From Source

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Lineax17/tuxgrade.git
   cd tuxgrade
   ```

2. **Install with pip:**
   ```bash
   pip install .
   ```

### Requirements

- **Supported Linux Distribution:**
  - **Fedora Linux** (dnf4/dnf5)
  - **RHEL/CentOS/AlmaLinux/Rocky Linux** (dnf4)
  - **Debian/Ubuntu/Pop!_OS/Linux Mint/Zorin OS** (apt)
- **Python 3.10+** (required)
- **Package Manager:**
  - **DNF 4 or DNF 5** (for Fedora/RHEL-based distributions)
    - DNF 5: Fedora 41+ (recommended)
    - DNF 4: Version 4.19+ (tested on Fedora 40, AlmaLinux)
  - **APT** (for Debian/Ubuntu-based distributions)
- **sudo** privileges (required)
- **Flatpak** (optional, for Flatpak updates)
- **Snap** (optional, for Snap updates)
- **Homebrew** (optional, for Homebrew updates)
- **akmods** (optional, for NVIDIA driver rebuilds on Fedora)

## Usage

### Basic Usage

Run the system update with default settings (silent mode with spinners):

```bash
tuxgrade
```

**For backward compatibility:**
```bash
fedora-update  # Still works as an alias
```

### Verbose Mode

Show detailed output during the update process:

```bash
tuxgrade --verbose
```

or shorter:

```bash
tuxgrade -l
```

### Include Homebrew Updates

Update Homebrew packages in addition to system packages:

```bash
tuxgrade --brew
```

or shorter:

```bash
tuxgrade -b
```

### Combined Options

```bash
tuxgrade --verbose --brew
tuxgrade -l -b
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--verbose` | `-l` | Enable detailed output for debugging and monitoring |
| `--brew` | `-b` | Include Homebrew packages in the update process |
| `--version` | | Display version information and exit |
| `--help` | `-h` | Show help message and exit |

## Update Process

The update process follows these steps in order:

### 1. Kernel Update Check (Fedora only for now)

- Checks for available kernel updates using the appropriate package manager:
  - Fedora: `dnf5 check-upgrade kernel*` or `dnf check-upgrade kernel*`
- If a kernel update is found, prompts for user confirmation
- **User Action Required:** Type `y` or `Y` to proceed, or any other key to abort

### 2. System Package Updates

- Updates all system packages using your distribution's package manager:
  - **Fedora/RHEL:** DNF5 or DNF4
  - **Ubuntu/Debian:** APT
- Refreshes package repositories
- In verbose mode: shows live update output
- In silent mode: displays progress spinner

### 3. Initramfs Rebuild

- Automatically rebuilds initramfs if a kernel update was installed
- Uses `dracut -f --regenerate-all`
- Ensures new kernel can boot properly

### 4. NVIDIA Driver Rebuild (Fedora only for now)

- Checks if `akmods` is installed (Fedora only for now)
- Rebuilds NVIDIA kernel modules if present
- Ensures NVIDIA drivers work with new kernel
- Skipped on Debian/Ubuntu-based distributions

### 5. Snap Package Updates

- Updates all Snap packages if Snap is installed
- Uses `snap refresh`
- Skips if Snap is not available

### 6. Flatpak Package Updates

- Updates all Flatpak applications if Flatpak is installed
- Uses `flatpak update`
- Skips if Flatpak is not available

### 7. Homebrew Updates (Optional)

- Only runs if `--brew` flag is provided
- Updates Homebrew formulae and casks
- Uses `brew update` and `brew upgrade`

## Troubleshooting

### Sudo Password Prompt

**Problem:** Script keeps asking for sudo password.

**Solution:** The script uses a keepalive mechanism. You should only be prompted once at the start. If prompted multiple times, check your sudo configuration.

### NVIDIA Drivers Not Working After Update (Fedora/RHEL)

**Problem:** NVIDIA drivers stop working after a kernel update.

**Solution:** 
1. Check if akmods is installed: `rpm -qa | grep akmods`
2. Manually rebuild: `sudo akmods --force`
3. Reboot your system

**Note:** This only applies to Fedora/RHEL-based distributions using akmods. Ubuntu/Debian users should consult official Distro documentation if error occur.

### Script Hangs or Freezes

**Problem:** Script appears to freeze during update.

**Solution:**
1. Use verbose mode to see what's happening: `tuxgrade --verbose`
2. Check if a package installation is waiting for user input
3. Press `Ctrl+C` to cancel and investigate

### Flatpak/Snap Updates Fail

**Problem:** Flatpak or Snap updates fail but script continues.

**Solution:** These are non-critical. The script will print a message and continue. You can update them manually:
```bash
flatpak update
snap refresh
```

## Best Practices

### 1. Regular Updates

Run tuxgrade regularly (weekly recommended) to keep your system secure and up-to-date.

### 2. Use Verbose Mode for Debugging

If something goes wrong, run with `--verbose` to see detailed output:
```bash
tuxgrade --verbose
```

### 3. Backup Before Major Updates

Before major version upgrades or kernel updates, consider backing up important data.

### 4. Read Kernel Update Warnings

When prompted for kernel update confirmation, read the version number carefully. Major kernel updates may occasionally cause compatibility issues with proprietary drivers.

### 5. Reboot After Kernel Updates

After a kernel update, reboot your system to load the new kernel:
```bash
sudo reboot
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - all updates completed |
| 1 | Error - unexpected error occurred |
| 130 | Cancelled - user cancelled with Ctrl+C |


## Getting Help

- **Documentation:** [docs/README.md](README.md)
- **Issues:** [GitHub Issues](https://github.com/Lineax17/tuxgrade/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Lineax17/tuxgrade/discussions)

