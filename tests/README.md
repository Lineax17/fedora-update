# Test Suite

This directory contains all automated tests for the Fedora Update Control Kit.

## Structure

```
tests/
├── kernel/              # Kernel update tests
│   ├── test_version_detection.py      # Kernel update availability detection
│   ├── test_version_extraction.py     # Kernel version string extraction
│   ├── test_user_confirmation.py      # User confirmation prompts
│   └── test_full_upgrade.py          # Full upgrade workflow simulation
│
├── sudo_keepalive/      # Sudo keepalive tests
│   ├── test_basic.py                  # Basic keepalive functionality
│   └── test_cross_module.py          # Cross-module persistence
│
├── syntax/              # Code quality tests
│   └── test_python_syntax.py         # Python syntax validation
│
└── run_tests.py         # Main test runner
```

## Running Tests

### Run all tests:

```bash
python tests/run_tests.py
```

### Run specific test category:

```bash
# Kernel tests
python tests/kernel/test_version_detection.py
python tests/kernel/test_version_extraction.py
python tests/kernel/test_user_confirmation.py
python tests/kernel/test_full_upgrade.py

# Sudo keepalive tests
python tests/sudo_keepalive/test_basic.py
python tests/sudo_keepalive/test_cross_module.py

# Syntax tests
python tests/syntax/test_python_syntax.py
```

## Test Categories

### Kernel Tests

Tests for kernel update detection, version parsing, and user interaction:

- **Version Detection**: Checks if new kernel updates are available via DNF
- **Version Extraction**: Parses kernel version strings from DNF output
- **User Confirmation**: Tests user prompts and input validation
- **Full Upgrade**: End-to-end workflow simulation with DNF integration

### Sudo Keepalive Tests

Tests for the sudo credential caching system:

- **Basic**: Start, stop, and persistence of keepalive process
- **Cross-Module**: Verifies keepalive works across function boundaries

### Syntax Tests

Code quality and validation:

- **Python Syntax**: Validates all Python files compile without errors

## Test Output

Each test provides:

- ✅ Clear pass/fail indicators
- Detailed test descriptions
- Summary statistics
- Category-based organization

## Requirements

Tests use Python's built-in modules:

- `unittest.mock` for mocking
- `subprocess` for process execution
- `pathlib` for file operations

No external test frameworks required.
