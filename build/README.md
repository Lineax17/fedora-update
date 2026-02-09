# Build Directory

This directory contains scripts and configuration files for building tuxgrade packages.

## Files

- `build-packages.sh` - Main build script that calls individual package builders
- `build-rpm.sh` - Standalone RPM package build script
- `build-deb.sh` - Standalone DEB package build script
- `tuxgrade.spec` - RPM package specification for Fedora/RHEL
- `output/` - Build output directory in the project root (created by build scripts, not in git)

## Building Packages

The build scripts use Podman containers to build packages, ensuring builds work on any Linux distribution.
Each script can be used individually for testing or called together via `build-packages.sh`.

### Prerequisites

- Podman installed on your system
  - Fedora/RHEL: `sudo dnf install podman`
  - Ubuntu/Debian: `sudo apt install podman`

### Usage

**Build both RPM and DEB packages:**

```bash
./build-packages.sh
```

**Build only RPM package:**

```bash
./build-packages.sh --rpm
# or directly:
./build-rpm.sh
```

**Build only DEB package:**

```bash
./build-packages.sh --deb
# or directly:
./build-deb.sh
```

**Help:**

```bash
./build-packages.sh --help
./build-rpm.sh --help
./build-deb.sh --help
```

### Output

Built packages are placed in:

- RPM packages: `output/rpm/`
- DEB packages: `output/deb/`

### Testing Packages

**Test RPM (Fedora/RHEL):**

```bash
sudo dnf install ./output/rpm/tuxgrade-*.noarch.rpm
```

**Test DEB (Ubuntu/Debian):**

```bash
sudo dpkg -i ./output/deb/tuxgrade_*.deb
sudo apt-get install -f  # Install dependencies if needed
```

## How It Works

The build system consists of three scripts:

### build-packages.sh

Main orchestrator script that calls `build-rpm.sh` and `build-deb.sh` based on command-line options.

### build-rpm.sh

Standalone RPM builder that:

1. **Extracts version** from `pyproject.toml` (single source of truth)
2. **Builds RPM** in a Fedora container using `rpmbuild`
3. **Outputs packages** to `output/rpm/` directory

### build-deb.sh

Standalone DEB builder that:

1. **Extracts version** from `pyproject.toml` (single source of truth)
2. **Builds DEB** in an Ubuntu 24.04 container using `dpkg-buildpackage`
3. **Outputs packages** to `output/deb/` directory

All builds use read-only volume mounts of the project source to ensure reproducibility.
Each script can be used independently for testing and development.
