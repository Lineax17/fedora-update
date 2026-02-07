# Tuxgrade

A robust and automated system upgrade script for multiple Linux distributions. It streamlines the update process for APT, DNF, Flatpak, Snap, and Homebrew, while ensuring system stability — especially for NVIDIA users.

**Supported Distributions:**
- Fedora/RHEL based
  - Fedora
  - RHEL
  - Alma
  - Rocky
- Debian/Ubuntu based
  - Debian
  - Ubuntu
  - Pop OS
  - Linux Mint
  - Zorin OS
- Any distribution with Flatpak, Snap, or Homebrew

## Features

- **Multi-Distribution Support:** Automatically detects your Linux distribution and uses the appropriate package manager (DNF for Fedora/RHEL, APT for Ubuntu/Debian)
- **Comprehensive Updates:** Updates system packages, Flatpak, Snap, and optionally Homebrew
- **Kernel Safety:** Detects kernel updates on rolling release distros (like Fedora), requests user confirmation, and automatically rebuilds `initramfs`
- **NVIDIA Driver Support:** Checks and rebuilds NVIDIA drivers to ensure they persist across kernel updates (Fedora/RHEL)
- **Modes:**
  - **Silent (Default):** Clean interface with progress spinners
  - **Verbose (`-l` / `--verbose`):** Detailed output for debugging or monitoring
- **Maintenance:** Automatically cleans old package caches and metadata

## Usage

```bash
tuxgrade [options]
```

**Note:** For backward compatibility, the commands `fedora-update` and `fedora-upgrade` still work as aliases.

### Options

- `-l`, `--verbose`: Enable detailed output.
- `-b`, `--brew`: Include Homebrew packages in the update.

## Installation

### Fedora/Alma/Rocky

#### Add the repo and install the package

Get the repo

```
sudo curl -L https://raw.githubusercontent.com/Lineax17/tuxgrade/refs/heads/master/extras/tuxgrade.repo -o /etc/yum.repos.d/tuxgrade.repo
```

Clear the dnf cache

```
sudo dnf clean all
```

Verify the repo with repolist command

```
sudo dnf repolist
```

Install the package

```
sudo dnf install tuxgrade
```

## Documentation

📚 **[Complete Documentation](docs/README.md)**

- **[User Guide](docs/user-guide.md)** - Installation, usage, and troubleshooting
- **[Architecture](docs/architecture.md)** - System design and architecture
- **[Developer Guide](docs/developer-guide.md)** - Contributing and development
- **[API Reference](docs/api-reference.md)** - Complete API documentation
- **[FAQ](docs/faq.md)** - Frequently asked questions

## Contributing

Contributions are welcome! Please read the [Developer Guide](docs/developer-guide.md) for details on:

- Setting up development environment
- Running tests
- Code style guidelines
- Submitting pull requests

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## AI Assistance

AI tools were used to assist in the development of this project, primarily for documentation and drafting.
The few lines of generated code have been reviewed and tested by me. This project is not AI-generated slop.
