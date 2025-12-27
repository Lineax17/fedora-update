# Architecture

This document describes the architecture and design decisions of the Fedora Update Control Kit.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Module Structure](#module-structure)
- [Data Flow](#data-flow)
- [Design Decisions](#design-decisions)

## Overview

Fedora Update Control Kit is designed as a modular Python application that orchestrates system updates across multiple package managers while ensuring system stability, especially for kernel updates and NVIDIA drivers.

### Key Principles

1. **Modularity** - Separate concerns into independent modules
2. **Safety** - User confirmation for critical updates (kernel)
3. **Robustness** - Graceful handling of missing package managers
4. **Transparency** - Clear feedback in both silent and verbose modes

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                             │
│                   (Entry Point & Orchestration)             │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│ Core Modules │ │  Helper  │ │  __version__ │
│              │ │  Modules │ │              │
└──────────────┘ └──────────┘ └──────────────┘
```

### Layer Structure

#### 1. Entry Point Layer (`main.py`)

- Argument parsing
- Workflow orchestration
- Error handling
- Exit code management

#### 2. Core Layer (`src/core/`)

Business logic for different package managers and system operations:

- `kernel.py` - Kernel update detection and user confirmation
- `dnf.py` - DNF package management
- `flatpak.py` - Flatpak application updates
- `snap.py` - Snap package updates
- `brew.py` - Homebrew package updates
- `init.py` - Initramfs regeneration
- `nvidia.py` - NVIDIA driver rebuilds

#### 3. Helper Layer (`src/helper/`)

Utility modules providing cross-cutting functionality:

- `runner.py` - Command execution with flexible error handling
- `cli.py` - User interface (spinners, headers, output)
- `sudo_keepalive.py` - Sudo privilege persistence
- `log.py` - Logging utilities (future use)

## Module Structure

### Core Modules

Each core module follows a consistent pattern:

```python
"""Module docstring"""

from helper import runner

def _check_<tool>_installed() -> bool:
    """Private: Check if tool is available"""
    ...

def update_<tool>(show_live_output: bool = False):
    """Public: Perform update operation"""
    ...
```

**Key characteristics:**
- Private functions prefixed with `_`
- Graceful degradation (skip if tool not installed)
- Consistent return types and error handling
- Google-style docstrings

### Helper Modules

#### runner.py

Central command execution module with three use cases:

1. **Live output** - For interactive updates (DNF)
2. **Command existence check** - For tool availability
3. **Exit code handling** - For special cases (kernel check)

```python
def run(cmd: list[str], 
        show_live_output: bool = False, 
        check: bool = True) -> CompletedProcess
```

#### cli.py

User interface abstraction:

```python
def print_output(function, verbose: bool, description: str)
    # Silent mode: spinner
    # Verbose mode: live output

def run_with_spinner(function, description: str)
    # Animated spinner with ✅/❌ status

def print_header(string: str, verbose: bool)
    # Only in verbose mode
```

#### sudo_keepalive.py

Maintains sudo privileges using a background thread:

```python
# Global singleton pattern
def start(refresh_interval: int = 60)
def stop()
def is_running() -> bool
```

## Data Flow

### Update Process Flow

```
┌─────────────────┐
│   User Input    │
│  (CLI args)     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  main.py                                    │
│  ┌────────────────────────────────────────┐│
│  │ 1. Start sudo_keepalive                ││
│  │ 2. Check kernel updates                ││
│  │    └─> Prompt if available             ││
│  │ 3. Update DNF packages                 ││
│  │ 4. Rebuild initramfs (if kernel update)││
│  │ 5. Rebuild NVIDIA modules              ││
│  │ 6. Update Snap packages                ││
│  │ 7. Update Flatpak packages             ││
│  │ 8. Update Homebrew (if --brew)         ││
│  │ 9. Stop sudo_keepalive                 ││
│  └────────────────────────────────────────┘│
└─────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│   Exit Code     │
│  (0/1/130)      │
└─────────────────┘
```

### Command Execution Flow

```
┌──────────────┐
│ Core Module  │
│ (e.g. dnf.py)│
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│  runner.run()    │
│  ┌────────────┐  │
│  │subprocess  │  │
│  │   .run()   │  │
│  └────────────┘  │
└──────┬───────────┘
       │
       ├─> Success: return CompletedProcess
       │
       └─> Failure: raise CommandError (if check=True)
```

## Design Decisions

### 1. Why Python Instead of Bash?

**Original:** Bash script (`legacy/fedora-update.sh`)

**Migration to Python:**
- ✅ Better error handling
- ✅ Type hints for reliability
- ✅ Easier testing with mocks
- ✅ More maintainable for complex logic
- ✅ Native subprocess handling

### 2. Modular Package Manager Support

Each package manager is in its own module, allowing:
- Independent testing
- Easy addition of new package managers
- Graceful degradation if a tool isn't installed

### 3. Kernel Update Confirmation

**Decision:** Always prompt for kernel updates

**Rationale:**
- Kernel updates can break systems (especially with NVIDIA)
- Users should be aware of kernel changes
- Allows users to postpone updates if needed

**Implementation:**
```python
if new_kernel:
    version = kernel.get_new_kernel_version()
    kernel.confirm_kernel_update(version)  # Exits if declined
```

### 4. Sudo Keepalive

**Decision:** Background thread refreshes sudo timestamp

**Alternatives considered:**
- Run everything with `sudo fedora-update` ❌ (less secure)
- Prompt for password multiple times ❌ (annoying)

**Implementation:** Thread-based keepalive with signal handlers

### 5. Silent vs Verbose Modes

**Decision:** Two distinct modes

**Silent mode:**
- Clean, minimal output
- Animated spinners
- ✅/❌ status indicators
- Target audience: Daily users

**Verbose mode:**
- Live command output
- Detailed headers
- Debugging information
- Target audience: Developers, troubleshooting

### 6. Error Handling Strategy

**Levels of error handling:**

1. **Critical errors** → Exit immediately
   - DNF5 not installed
   - Sudo validation fails
   - Kernel update declined

2. **Recoverable errors** → Log and continue
   - Flatpak not installed
   - Snap not installed
   - Homebrew not installed

3. **User cancellation** → Clean exit with code 130
   - Ctrl+C handling
   - Signal handlers

### 7. Return vs Raise for Optional Tools

**Pattern for optional package managers:**

```python
def update_flatpak():
    if not _check_flatpak_installed():
        print("Flatpak is not installed")  # Inform but don't fail
        return  # Silent return
    # ... proceed with update
```

**Pattern for required tools:**

```python
def update_dnf():
    if not _check_dnf_installed():
        raise RuntimeError("DNF is required")  # Fail loudly
```

### 8. Test Strategy

**Unit tests:** Mock `runner.run()` to test logic without executing commands

```python
# Example from tests/test_kernel_logic.py
with patch('core.kernel.runner.run', return_value=mock_result):
    result = kernel.new_kernel_version()
    assert result == True
```

### 9. Version Management

**Single source of truth:** `src/__version__.py`

```python
__version__ = "2.0.0"
```

Referenced by:
- `main.py` (--version argument)
- `pyproject.toml` (package metadata)
- Documentation

## Extension Points

### Adding a New Package Manager

1. Create `src/core/<manager>.py`
2. Implement pattern:
   ```python
   def _check_<manager>_installed() -> bool
   def update_<manager>(show_live_output: bool = False)
   ```
3. Add to `main.py` orchestration
4. Add tests in `tests/test_<manager>.py`
5. Update documentation

### Adding a New Helper Module

1. Create `src/helper/<module>.py`
2. Add module docstring
3. Implement Google-style docstrings
4. Import in relevant modules
5. Add documentation

## Performance Considerations

### Sequential Execution

**Current:** Updates run sequentially

**Rationale:**
- Prevents package manager conflicts
- Easier error tracking
- Predictable behavior

**Future consideration:** Parallel updates for independent package managers

### Sudo Keepalive

**Overhead:** Minimal (one background thread, refreshes every 60s)

**Benefit:** Eliminates sudo password prompts during long updates

## Security Considerations

1. **Sudo usage:** Limited to specific commands, not shell injection
2. **Command construction:** Uses list format, not string concatenation
3. **Input validation:** Kernel confirmation accepts only y/Y
4. **Signal handling:** Clean shutdown on Ctrl+C or SIGTERM

## Future Improvements

- [ ] Parallel package manager updates
- [ ] Rollback mechanism for failed updates
- [ ] System snapshot integration (Btrfs/LVM)
- [ ] Configuration file support
- [ ] Dry-run mode
- [ ] Update scheduling
- [ ] Email notifications

