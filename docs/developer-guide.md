# Developer Guide

Guide for developers who want to contribute to or extend Fedora Update Control Kit.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Code Style](#code-style)
- [Contributing](#contributing)
- [Release Process](#release-process)

## Development Setup

### Prerequisites

- **Fedora Linux 41+**
- **Python 3.10+**
- **Git**
- **DNF5**

### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/Lineax17/fedora-update.git
cd fedora-update

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
fedora-update/
├── src/                          # Source code
│   ├── __version__.py           # Version information
│   ├── main.py                  # Entry point
│   ├── core/                    # Core business logic
│   │   ├── kernel.py           # Kernel update management
│   │   ├── dnf.py              # DNF package updates
│   │   ├── flatpak.py          # Flatpak updates
│   │   ├── snap.py             # Snap updates
│   │   ├── brew.py             # Homebrew updates
│   │   ├── init.py             # Initramfs rebuild
│   │   └── nvidia.py           # NVIDIA driver rebuild
│   └── helper/                  # Utility modules
│       ├── runner.py           # Command execution
│       ├── cli.py              # UI components
│       ├── sudo_keepalive.py   # Sudo management
│       └── log.py              # Logging (future)
├── tests/                       # Test suite
│   ├── test_kernel_logic.py   # Kernel module tests
│   ├── test_sudo_keepalive.py # Keepalive tests
│   ├── test_syntax.sh         # Bash syntax tests
│   └── run_tests.sh           # Test runner
├── docs/                        # Documentation
│   ├── README.md              # Documentation index
│   ├── user-guide.md          # User documentation
│   ├── architecture.md        # Architecture overview
│   ├── developer-guide.md     # This file
│   └── modules/               # Module-specific docs
├── legacy/                      # Original Bash script
│   └── fedora-update.sh
├── build/                       # RPM build files
│   ├── build.sh
│   └── fedora-update.spec
├── pyproject.toml              # Python project config
├── README.md                   # Project README
└── LICENSE                     # MIT License
```

## Running Tests

### Python Tests

```bash
# Run all Python tests
python3 tests/test_kernel_logic.py
python3 tests/test_sudo_keepalive.py

# Or use pytest if installed
pytest tests/
```

### Test Coverage

```bash
# Run with coverage
pytest --cov=src --cov-report=html tests/
```

### Bash Tests (Legacy)

```bash
# Run all tests
bash tests/run_tests.sh

# Run specific test
bash tests/test_kernel_logic.sh
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

## Adding New Features

### Adding a New Package Manager

Example: Adding support for APT

1. **Create the module:**
   ```python
   # src/core/apt.py
   """APT package manager update module."""
   
   from helper import runner
   
   def _check_apt_installed() -> bool:
       """Check if APT is installed."""
       result = runner.run(["apt", "--version"], check=False)
       return result.returncode == 0
   
   def update_apt(show_live_output: bool = False):
       """Update all APT packages."""
       if not _check_apt_installed():
           print("APT is not installed on this system.")
           return
       runner.run(["sudo", "apt", "update"], show_live_output=show_live_output)
       runner.run(["sudo", "apt", "upgrade", "-y"], show_live_output=show_live_output)
   ```

2. **Add to main.py:**
   ```python
   from core import apt
   
   # In main():
   cli.print_header("Update APT Packages", verbose)
   cli.print_output(apt.update_apt, verbose, "Updating APT packages")
   ```

3. **Write tests:**
   ```python
   # tests/test_apt.py
   def test_apt_update():
       with patch('core.apt.runner.run') as mock_run:
           mock_run.return_value = CompletedProcess([], 0, "", "")
           apt.update_apt()
           assert mock_run.called
   ```

4. **Update documentation:**
   - Add to `docs/user-guide.md`
   - Add to `docs/architecture.md`
   - Create `docs/modules/apt.md`

### Adding a Helper Function

1. Choose appropriate module or create new one
2. Add docstring with type hints
3. Write unit tests
4. Update API reference

## Debugging

### Verbose Mode

Always test with verbose mode:

```bash
fedora-update --verbose
```

### Logging

Add debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.debug("Debug message")
```

### Testing Individual Modules

```python
# Test a specific function
from core import kernel
result = kernel.new_kernel_version()
print(f"Kernel update available: {result}")
```

## Testing Strategy

### Unit Tests

Mock external commands:

```python
from unittest.mock import patch
from subprocess import CompletedProcess

def test_kernel_update_available():
    mock_result = CompletedProcess(
        args=["dnf5", "check-upgrade", "-q", "kernel*"],
        returncode=100,
        stdout="kernel-core.x86_64 6.11.0-200.fc40 updates\n",
        stderr=""
    )
    
    with patch('core.kernel.runner.run', return_value=mock_result):
        result = kernel.new_kernel_version()
        assert result == True
```

### Integration Tests

Test with actual commands (requires sudo):

```python
# Integration test (run manually)
def test_dnf_update_integration():
    # Only run on actual Fedora system
    if not is_fedora():
        pytest.skip("Not on Fedora")
    
    dnf.update_dnf(show_live_output=True)
```

### Test Coverage Goals

- **Core modules:** 80%+ coverage
- **Helper modules:** 90%+ coverage
- **Critical paths:** 100% coverage (kernel, sudo)

## Release Process

### Version Bumping

1. **Update version:**
   ```python
   # src/__version__.py
   __version__ = "2.1.0"
   ```

2. **Update pyproject.toml:**
   ```toml
   [project]
   version = "2.1.0"
   ```

3. **Update RPM spec:**
   ```spec
   # build/fedora-update.spec
   Version: 2.1.0
   ```

### Creating a Release

1. **Commit version changes:**
   ```bash
   git commit -am "Bump version to 2.1.0"
   ```

2. **Tag the release:**
   ```bash
   git tag -a v2.1.0 -m "Release version 2.1.0"
   ```

3. **Push changes:**
   ```bash
   git push origin main
   git push origin v2.1.0
   ```

4. **Build RPM:**
   ```bash
   bash build/build.sh
   ```

5. **Create GitHub Release:**
   - Go to GitHub releases
   - Create new release from tag
   - Upload RPM file
   - Add changelog

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
# In main.py
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

## Getting Help

- **Questions:** [GitHub Discussions](https://github.com/Lineax17/fedora-update/discussions)
- **Bugs:** [GitHub Issues](https://github.com/Lineax17/fedora-update/issues)
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

