# Fedora Update Control Kit

A robust and automated system upgrade script for Fedora Linux (Fedora 41+). It streamlines the update process for DNF5, Flatpak, Snap, and Homebrew, while ensuring system stability-especially for NVIDIA users.

## Features

- **Comprehensive Updates:** Updates system packages (DNF5), Flatpak, Snap, and optionally Homebrew.
- **Kernel Safety:** Detects kernel updates, requests user confirmation, and automatically rebuilds `initramfs`.
- **NVIDIA Driver Support:** Checks and rebuilds `akmods` to ensure NVIDIA drivers persist across kernel updates.
- **Modes:**
  - **Silent (Default):** Clean interface with progress spinners.
  - **Verbose (`-l` / `--verbose`):** Detailed output for debugging or monitoring.
- **Maintenance:** Automatically cleans old package caches and metadata.

## Usage

```bash
fedora-update [options]
```

### Options

- `-l`, `--verbose`: Enable detailed output.
- `-b`, `--brew`: Include Homebrew packages in the update.

## Installation

### Add the repo and install the package

Get the repo

```
sudo curl -L https://raw.githubusercontent.com/Lineax17/fedora-update/refs/heads/master/extras/fedora-update.repo -o /etc/yum.repos.d/fedora-update.repo
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
sudo dnf install fedora-update
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
