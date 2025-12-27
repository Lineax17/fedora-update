# Frequently Asked Questions (FAQ)

Common questions and answers about Fedora Update Control Kit.

## General Questions

### What is Fedora Update Control Kit?

Fedora Update Control Kit is an automated system upgrade tool for Fedora Linux that streamlines updates across multiple package managers (DNF5, Flatpak, Snap, Homebrew) while ensuring system stability, especially for kernel updates and NVIDIA drivers.

### Why use this instead of just `dnf update`?

Fedora Update Control Kit provides:
- **Kernel safety**: Prompts before kernel updates and rebuilds initramfs automatically
- **NVIDIA support**: Automatically rebuilds NVIDIA drivers after kernel updates
- **Multiple package managers**: Updates DNF, Flatpak, Snap, and Homebrew in one command
- **User-friendly**: Silent mode with spinners or verbose mode for detailed output
- **Sudo management**: Only asks for password once

### Is this safe to use?

Yes. The script:
- Prompts for confirmation before kernel updates
- Uses well-tested package managers (DNF5, Flatpak, etc.)
- Has been used in production on multiple systems
- Is based on a mature Bash script (v1.x)
- Has comprehensive test coverage

### Can I use this on other Linux distributions?

Currently, Fedora Update Control Kit is designed for **Fedora Linux 41+**. It requires DNF5, which is Fedora-specific. However, the modular architecture makes it easy to adapt for other distributions.

## Installation Questions

### Do I need to install all package managers?

No. Only **DNF5** is required. Flatpak, Snap, Homebrew, and akmods are optional. The script will skip updates for tools that aren't installed.

### How do I uninstall?

```bash
sudo dnf remove fedora-update
```

### Can I install from source?

Yes:
```bash
git clone https://github.com/Lineax17/fedora-update.git
cd fedora-update
pip install .
```

## Usage Questions

### How do I run it?

Simply:
```bash
fedora-update
```

For verbose output:
```bash
fedora-update --verbose
```

### Does it need sudo?

Yes, but you don't need to run it with `sudo fedora-update`. The script will prompt for your password once and maintain privileges throughout execution.

### Can I automate it?

Yes, but be careful with kernel updates. You might want to disable the kernel confirmation prompt for automation. See [Developer Guide](developer-guide.md) for details.

### What if I don't want kernel updates?

When prompted for kernel update confirmation, press any key except `y` or `Y`, or press `Ctrl+C`.

### Can I update only specific package managers?

Currently, the script updates all available package managers. You can use the `--brew` flag to optionally include Homebrew. Future versions may add more granular control.

## Troubleshooting Questions

### Why does it keep asking for my password?

You should only be prompted once. If prompted multiple times:
1. Check your sudo configuration: `sudo cat /etc/sudoers`
2. Ensure sudo timeout is not too short
3. Check if sudo_keepalive is working: `fedora-update --verbose`

### What if the script crashes?

1. Run with verbose mode to see details: `fedora-update --verbose`
2. Check the error message
3. Report bugs at: https://github.com/Lineax17/fedora-update/issues

### My NVIDIA drivers stopped working after update

This can happen after kernel updates. Solutions:

1. **Reboot first**: The new drivers might need a reboot
2. **Rebuild manually**:
   ```bash
   sudo akmods --force
   sudo dracut -f --regenerate-all
   sudo reboot
   ```
3. **Check logs**: `dmesg | grep nvidia`

### The script says "DNF5 not found"

Install DNF5:
```bash
sudo dnf install dnf5
```

Fedora 41+ should have DNF5 by default.

### Flatpak/Snap updates fail

These are non-critical. The script will continue even if they fail. You can update manually:
```bash
flatpak update
snap refresh
```

### Can I see what's happening during updates?

Yes, use verbose mode:
```bash
fedora-update --verbose
```

### How do I save update logs?

```bash
fedora-update --verbose 2>&1 | tee ~/update-$(date +%Y%m%d).log
```

## Feature Questions

### Does it support Homebrew?

Yes, with the `--brew` flag:
```bash
fedora-update --brew
```

### Does it clean old packages?

Currently, it updates packages but doesn't clean old versions. You can manually clean with:
```bash
sudo dnf clean packages
```

### Can it rollback failed updates?

Not currently. Future versions may include rollback support using Btrfs/LVM snapshots.

### Does it support dry-run mode?

Not yet, but it's planned for a future release.

### Can I schedule automatic updates?

Yes, but be cautious with kernel updates. You can create a systemd timer or cron job. See [Developer Guide](developer-guide.md#automated-updates-advanced) for details.

## Technical Questions

### What's the difference between v1.x (Bash) and v2.x (Python)?

| Feature | v1.x (Bash) | v2.x (Python) |
|---------|-------------|---------------|
| Language | Bash | Python 3.10+ |
| Testing | Limited | Comprehensive unit tests |
| Type Safety | None | Type hints |
| Error Handling | Basic | Advanced |
| Extensibility | Moderate | High (modular) |
| Performance | Fast | Comparable |

### Why was it rewritten in Python?

- Better error handling and testing
- Type safety with type hints
- Easier to extend and maintain
- Better cross-platform potential
- More robust subprocess handling

### What Python version is required?

Python 3.10 or higher. This is because we use:
- Modern type hints (`str | None`)
- Match-case statements (if used in future)
- Other Python 3.10+ features

### Does it have dependencies?

No external dependencies. It uses only Python standard library modules:
- `subprocess`
- `argparse`
- `threading`
- `logging`
- etc.

### How is sudo keepalive implemented?

A background thread refreshes the sudo timestamp every 60 seconds using `sudo -n true`. See [sudo_keepalive.md](modules/sudo_keepalive.md) for details.

### Can I contribute?

Yes! See the [Developer Guide](developer-guide.md#contributing) for details.

## Comparison Questions

### vs. GNOME Software

| Feature | Fedora Update Kit | GNOME Software |
|---------|-------------------|----------------|
| Interface | CLI | GUI |
| Speed | Fast | Slower |
| Package Managers | DNF, Flatpak, Snap, Brew | DNF, Flatpak |
| Kernel Safety | Explicit confirmation | Automatic |
| NVIDIA Support | Automatic rebuild | Manual |
| Automation | Easy | Difficult |

### vs. dnf-automatic

| Feature | Fedora Update Kit | dnf-automatic |
|---------|-------------------|---------------|
| Kernel Updates | With confirmation | Automatic |
| Flatpak | Yes | No |
| Snap | Yes | No |
| Homebrew | Yes | No |
| NVIDIA | Automatic rebuild | No |
| Interactive | Yes | No |

### vs. Manual Updates

| Feature | Fedora Update Kit | Manual |
|---------|-------------------|--------|
| Commands | 1 command | Multiple commands |
| Kernel Safety | Built-in | Manual checking |
| NVIDIA Rebuild | Automatic | Manual |
| Error Handling | Automatic | Manual |
| Time | Quick | Slower |

## Security Questions

### Is it safe to keep sudo active?

The sudo keepalive refreshes privileges every 60 seconds, which is the same timeout as the default sudo configuration. It doesn't bypass security, just prevents re-prompting.

### Can it be exploited?

The script:
- Uses subprocess with list arguments (no shell injection)
- Doesn't accept network input
- Doesn't execute arbitrary code
- Has signal handlers for clean shutdown

### Should I review the code?

Yes! The code is open source. Review it before use:
https://github.com/Lineax17/fedora-update

## Version Questions

### How do I check the version?

```bash
fedora-update --version
```

### How often are releases made?

Currently on an as-needed basis. Follow the GitHub repository for updates.

### What's the update policy?

- **Patch releases** (2.0.x): Bug fixes, no breaking changes
- **Minor releases** (2.x.0): New features, backward compatible
- **Major releases** (x.0.0): Breaking changes, major refactoring

## Getting More Help

### Where can I find more documentation?

- **User Guide**: [user-guide.md](user-guide.md)
- **Architecture**: [architecture.md](architecture.md)
- **Developer Guide**: [developer-guide.md](developer-guide.md)
- **API Reference**: [api-reference.md](api-reference.md)

### How do I report bugs?

Create an issue on GitHub:
https://github.com/Lineax17/fedora-update/issues

### How do I request features?

Open a discussion on GitHub:
https://github.com/Lineax17/fedora-update/discussions

### Can I get help from the community?

Yes! Use GitHub Discussions for questions and help:
https://github.com/Lineax17/fedora-update/discussions

