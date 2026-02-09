# Developer Guide

Guide for developers who want to contribute to or extend Tuxgrade.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Code Style](#code-style)
- [Contributing](#contributing)
- [Release Process](#release-process)

## Development Setup

### Prerequisites

- **Python 3.10+**
- **Git**
- **DNF 4/DNF 5** (for Fedora/RHEL testing) or **APT** (for Debian/Ubuntu testing)

### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/Lineax17/tuxgrade.git
cd tuxgrade

# Create a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .
```

### Development Dependencies

```bash
# Install development tools
pip install pytest pytest-cov black mypy
```

## Project Structure

```
tuxgrade/
├── src/                          # Source code
│   ├── __version__.py           # Version information
│   ├── main.py                  # Entry point
│   ├── app/                     # Application layer
│   │   ├── app.py              # Main application logic
│   │   └── cli.py              # CLI argument parsing
│   ├── core/                    # Core business logic
│   │   ├── kernel.py           # Kernel update management
│   │   ├── init.py             # Initramfs rebuild
│   │   └── nvidia.py           # NVIDIA driver rebuild
│   ├── distros/                 # Distribution-specific logic
│   │   ├── distro_manager.py   # Orchestrates distro updates
│   │   ├── fedora_distro.py    # Fedora-specific (dnf, akmods)
│   │   ├── debian_distro.py    # Debian-specific (apt)
│   │   ├── rhel_distro.py      # RHEL/CentOS (dnf + subscription-manager)
│   │   ├── ubuntu_distro.py    # Ubuntu family (apt + PPA)
│   │   └── generic_distro.py   # Fallback for unknown distros
│   ├── package_managers/        # Package manager abstraction
│   │   ├── dnf.py              # DNF package manager
│   │   ├── apt.py              # APT package manager
│   │   ├── flatpak.py          # Flatpak updates
│   │   ├── snap.py             # Snap updates
│   │   └── brew.py             # Homebrew updates
│   └── helper/                  # Utility modules
│       ├── runner.py           # Command execution
│       ├── cli_print_utility.py # UI components
│       ├── sudo_keepalive.py   # Sudo management
│       └── log.py              # Logging (future)
├── tests/                       # Test suite
├── docs/                        # Documentation
├── build/                       # RPM build files
│   ├── build.sh
│   └── tuxgrade.spec
├── pyproject.toml              # Python project config
├── README.md                   # Project README
└── LICENSE                     # MIT License
```

## Running Tests

### Using the Test Runner

The project includes a comprehensive test runner that automatically discovers and runs all tests:

```bash
# Run all tests
python3 tests/run_tests.py
```

The test runner will:

- Automatically discover all test files in `tests/` subdirectories
- Organize tests by category (kernel, sudo_keepalive, syntax, etc.)
- Provide detailed output for each test suite
- Show a comprehensive summary with pass/fail status

### Running Individual Tests

You can also run individual test files directly:

```bash
# Run specific test category
python3 tests/kernel/test_version_detection.py
python3 tests/sudo_keepalive/test_basic.py

# Run syntax tests
python3 tests/syntax/test_python_syntax.py
```

### Test Coverage

```bash
# Run with coverage (if pytest is installed)
pytest --cov=src --cov-report=html tests/
```

## Code Style

### Python Style Guide

We follow **PEP 8** with some modifications:

- **Line length:** 100 characters (not 79)
- **Docstrings:** Google style
- **Type hints:** Required for all public functions
- **Imports:** Grouped (stdlib, third-party, local)

### Type Hints

```python
# Good
def update_dnf(show_live_output: bool = False) -> None:
    """Update DNF packages."""
    ...

# Bad - missing type hints
def update_dnf(show_live_output=False):
    ...
```

### Docstring Format

Use **Google-style docstrings**:

```python
def example_function(param1: str, param2: int) -> bool:
    """Brief description of what the function does.

    More detailed description if needed. Explain the purpose,
    behavior, and any important details.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param2 is negative.
        RuntimeError: When operation fails.
    """
    ...
```

### Module Docstrings

Every module should have a docstring:

```python
"""Brief module description.

Longer description explaining the module's purpose and
what functionality it provides.
"""

import os
...
```

### Code Formatting

```bash
# Format code with black
black src/ tests/

# Check with mypy
mypy src/
```

## Contributing

### Workflow

1. **Fork the repository** on GitHub

2. **Create a feature branch:**

   ```bash
   git checkout -b feature/my-new-feature
   ```

3. **Make your changes** following the code style guide

4. **Add tests** for new functionality

5. **Run tests** to ensure everything works:

   ```bash
   python3 tests/test_kernel_logic.py
   ```

6. **Commit your changes:**

   ```bash
   git commit -m "Add feature: description"
   ```

7. **Push to your fork:**

   ```bash
   git push origin feature/my-new-feature
   ```

8. **Create a Pull Request** on GitHub

### Commit Message Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add support for zypper package manager
fix: correct initramfs rebuild logic
docs: update installation instructions
test: add tests for snap module
refactor: simplify kernel version extraction
```

### Pull Request Guidelines

- **Title:** Clear, concise description
- **Description:** Explain what and why
- **Tests:** Include test results
- **Documentation:** Update relevant docs
- **Breaking changes:** Clearly mark them

## Release Process

### Version Bumping

1. **Update version in pyproject.toml (single source of truth):**

   ```toml
   # pyproject.toml
   [project]
   version = "3.1.0"
   ```

2. **Update RPM spec changelog:**

   ```spec
   # build/tuxgrade.spec
   %changelog
   * Sat Feb 09 2026 Lineax17 <lineax17@gmail.com> - 3.1.0-1
   - Your changelog entry here
   ```

3. **Update Debian changelog:**

   ```bash
   # debian/changelog
   tuxgrade (3.1.0-1) unstable; urgency=medium

     * Your changelog entry here

    -- Lineax17 <lineax17@gmail.com>  Sat, 09 Feb 2026 12:00:00 +0100
   ```

### Building Packages Locally

The project uses container-based builds for both RPM and DEB packages, ensuring consistent builds across any Linux distribution.

**Prerequisites:**

- Podman installed on your system

**Build both packages:**

```bash
cd build
./build.sh
```

**Build only RPM:**

```bash
./build.sh --rpm
```

**Build only DEB:**

```bash
./build.sh --deb
```

**Output location:**

- RPM: `build/output/rpm/`
- DEB: `build/output/deb/`

**Test installations:**

```bash
# Test RPM (Fedora/RHEL)
sudo dnf install ./build/output/rpm/tuxgrade-3.1.0-1.noarch.rpm

# Test DEB (Ubuntu/Debian)
sudo dpkg -i ./build/output/deb/tuxgrade_3.1.0-1_all.deb
sudo apt-get install -f  # Install dependencies if needed
```

### Creating a Release

1. **Commit version changes:**

   ```bash
   git add pyproject.toml build/tuxgrade.spec debian/changelog
   git commit -m "Bump version to 3.1.0"
   git push origin main
   ```

2. **Build packages locally:**

   ```bash
   cd build
   ./build.sh
   ```

   This builds both RPM and DEB packages in `build/output/rpm/` and `build/output/deb/`.

3. **Create and push tag:**

   ```bash
   git tag -a v3.1.0 -m "Release version 3.1.0"
   git push origin v3.1.0
   ```

4. **Create GitHub Release and upload packages:**
   - Go to GitHub → Releases → "Draft a new release"
   - Choose the tag `v3.1.0`
   - Title: `v3.1.0`
   - Add release notes (changelog)
   - **Upload built packages:**
     - Drag and drop files from `build/output/rpm/*.rpm`
     - Drag and drop files from `build/output/deb/*.deb`
   - Click "Publish release"

5. **Automated Repository Update:**

   When you publish the release, the `.github/workflows/publish-repo.yml` workflow automatically:
   - Downloads the RPM and DEB packages from the release
   - Generates repository metadata (repodata for RPM, Packages.gz for DEB)
   - Deploys both repositories to GitHub Pages at:
     - RPM: `https://Lineax17.github.io/tuxgrade/rpm/`
     - DEB: `https://Lineax17.github.io/tuxgrade/deb/`

   No manual intervention needed - the repositories are automatically updated!

### Changelog Format

```markdown
## [2.1.0] - 2025-12-27

### Added

- Support for new package manager
- Dry-run mode

### Changed

- Improved error messages
- Updated dependencies

### Fixed

- Bug in kernel version detection
- Race condition in sudo keepalive

### Breaking Changes

- Renamed --log to --verbose
```

## Common Development Tasks

### Add a Command Line Option

```python
# In cli_print_utility.py
parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Show what would be updated without making changes"
)
```

### Add Error Handling

```python
try:
    result = runner.run(["some", "command"])
except runner.CommandError as e:
    logging.error(f"Command failed: {e}")
    # Decide: continue or exit
```

### Add Progress Indicator

```python
# Silent mode
cli.run_with_spinner(lambda: my_function(), "Doing something")

# Verbose mode
if verbose:
    print("Doing something...")
    my_function()
```

## Troubleshooting

### ModuleNotFoundError: No module named 'src'

If you encounter this error when running the program:

```
ModuleNotFoundError: No module named 'src'
```

**Problem:** Python cannot find the `src` module because the project root is not in the Python path.

**Solution: Run as a module**

```bash
# Navigate to the project root directory
cd /path/to/tuxgrade

# Run as a module
python3 -m src.main --verbose
```

## Getting Help

- **Questions:** [GitHub Discussions](https://github.com/Lineax17/tuxgrade/discussions)
- **Bugs:** [GitHub Issues](https://github.com/Lineax17/tuxgrade/issues)
- **Documentation:** [docs/](../docs/)
- **Architecture:** [architecture.md](architecture.md)

## Code Review Checklist

Before submitting a PR, ensure:

- [ ] Code follows PEP 8 style guide
- [ ] All functions have type hints
- [ ] All functions have Google-style docstrings
- [ ] Tests are written and passing
- [ ] Documentation is updated
- [ ] No unused imports or variables
- [ ] Error handling is appropriate
- [ ] Logging is added where useful
- [ ] Commit messages follow guidelines
- [ ] No breaking changes (or clearly documented)
