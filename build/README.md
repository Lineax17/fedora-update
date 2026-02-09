# Build Directory

This directory contains scripts and configuration files for building tuxgrade packages.

## Files

- `podman/` - Podman-based build scripts
- `docker/` - Docker-based build scripts (used by CI)
- `tuxgrade.spec` - RPM package specification for Fedora/RHEL
- `output/` - Build output directory in the project root (created by build scripts, not in git)

## Building Packages

The build scripts use containerized builds to ensure reproducibility across Linux distributions.
Each script can be used individually or called together via `build-packages.sh` in the respective runtime directory.

### Prerequisites

- Podman installed on your system (Podman scripts)
  - Fedora/RHEL: `sudo dnf install podman`
  - Ubuntu/Debian: `sudo apt install podman`
- Docker installed on your system (Docker scripts)
  - https://docs.docker.com/get-docker/

### Usage

**Build both RPM and DEB packages (Podman):**

```bash
./podman/build-packages.sh
```

**Build only RPM package (Podman):**

```bash
./podman/build-packages.sh --rpm
# or directly:
./podman/build-rpm.sh
```

**Build only DEB package (Podman):**

````bash
./podman/build-packages.sh --deb
# or directly:
./podman/build-deb.sh

**Build both RPM and DEB packages (Docker):**

```bash
./docker/build-packages.sh
````

**Build only RPM package (Docker):**

```bash
./docker/build-packages.sh --rpm
# or directly:
./docker/build-rpm.sh
```

**Build only DEB package (Docker):**

```bash
./docker/build-packages.sh --deb
# or directly:
./docker/build-deb.sh
```

````

**Help:**

```bash
./podman/build-packages.sh --help
./podman/build-rpm.sh --help
./podman/build-deb.sh --help
./docker/build-packages.sh --help
./docker/build-rpm.sh --help
./docker/build-deb.sh --help
````

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

The build system consists of three scripts per runtime (Podman or Docker):

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
