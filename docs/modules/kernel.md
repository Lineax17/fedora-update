# Kernel Module Documentation

Detailed documentation for the `kernel` module (`src/core/kernel.py`).

## Overview

The kernel module handles kernel update detection, version extraction, and user confirmation for kernel upgrades. It ensures users are aware of kernel updates before proceeding, which is critical for system stability, especially with NVIDIA drivers.

**Note:** Implementation details vary by distribution. Fedora/RHEL use DNF, while Ubuntu/Debian use APT.

## Module Functions

### `new_kernel_version() -> bool`

Checks if a new kernel version is available via DNF5.

#### Implementation Details

Uses distribution-specific package manager to check for kernel updates:

**Fedora/RHEL:**
- Uses `dnf5 check-upgrade -q kernel*` or `dnf check-upgrade -q kernel*`
- **Exit code 0**: No kernel updates available
- **Exit code 100**: Kernel updates available  
- **Other exit codes**: Error condition

**Ubuntu/Debian:**
- No kernel check required and for this reason not implemented.

#### Algorithm

```python
result = runner.run(["dnf5", "check-upgrade", "-q", "kernel*"], check=False)

if result.returncode == 0:
    return False  # No updates
elif result.returncode == 100:
    return True   # Updates available
else:
    raise CommandError("Kernel update check failed")
```

#### Return Value

- `True`: Kernel update is available
- `False`: No kernel update available

#### Exceptions

- `CommandError`: Raised when dnf5 fails with an unexpected exit code (not 0 or 100)

#### Usage Example

```python
from core import kernel

if kernel.new_kernel_version():
    print("Kernel update available!")
    # Proceed with update logic
else:
    print("System is up to date")
```

#### DNF5 Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No updates available |
| 100 | Updates available |
| Other | Error (network, permissions, etc.) |

---

### `get_new_kernel_version() -> str`

Extracts the kernel version string from DNF5 output.

#### Implementation Details

Queries DNF5 for the `kernel-helper` package and parses the version from the output.

**DNF5 Output Format:**
```
kernel-helper                     6.12.5-300.fc41                     updates
```

The function extracts `6.12.5` from `6.12.5-300.fc41`.

#### Algorithm

```python
result = runner.run(['dnf5', 'check-update', 'kernel-helper'], check=False)

for line in result.stdout.splitlines():
    line = line.strip()
    if line.startswith('kernel-helper'):
        parts = line.split()  # Split by whitespace
        if len(parts) >= 2:
            full_version = parts[1]  # e.g., "6.12.5-300.fc41"
            kernel_version = full_version.split('-')[0]  # Extract "6.12.5"
            return kernel_version

raise CommandError("Kernel version check failed")
```

#### Return Value

Returns the kernel version string (e.g., `"6.12.5"`).

#### Exceptions

- `CommandError`: Raised when kernel-helper version cannot be found in DNF5 output

#### Usage Example

```python
from core import kernel

if kernel.new_kernel_version():
    version = kernel.get_new_kernel_version()
    print(f"New kernel version: {version}")
```

#### Why kernel-helper?

The `kernel-helper` package is used instead of `kernel-core` because it provides a consistent version string that matches the actual kernel version.

---

### `confirm_kernel_update(new_version: str) -> bool`

Prompts the user to confirm a kernel upgrade.

#### Implementation Details

Displays an interactive prompt asking the user to confirm the kernel update before proceeding.

#### User Interaction

```
Kernel update available: 6.12.5. Proceed? [y/N]:
```

- User types `y` or `Y`: Update proceeds (returns `True`)
- User types anything else or presses Enter: Update aborted (raises `SystemExit(1)`)
- User presses Ctrl+C: Update aborted (raises `SystemExit(1)`)

#### Algorithm

```python
try:
    response = input(f"Kernel update available: {new_version}. Proceed? [y/N]: ").strip()
    
    if response in ['y', 'Y']:
        return True
    else:
        print("Aborted: Kernel update detected and not confirmed.")
        raise SystemExit(1)
except (KeyboardInterrupt, EOFError):
    print("\nAborted: Kernel update detected and not confirmed.")
    raise SystemExit(1)
```

#### Parameters

- `new_version` (str): The version string of the new kernel (e.g., "6.12.5")

#### Return Value

- `True`: User confirmed the update

#### Exceptions

- `SystemExit(1)`: User declined the update or pressed Ctrl+C

#### Usage Example

```python
from core import kernel

if kernel.new_kernel_version():
    version = kernel.get_new_kernel_version()
    kernel.confirm_kernel_update(version)
    # Only reaches here if user confirmed
    print("Proceeding with kernel update...")
```

#### Why Require Confirmation?

Kernel updates can:
- Break NVIDIA drivers (if not rebuilt)
- Introduce compatibility issues
- Require system reboot
- Occasionally cause boot failures

User confirmation ensures awareness and allows deferring updates if needed.

---

## Usage Patterns

### Complete Kernel Update Workflow

```python
from core import kernel, init, nvidia

# Check for kernel updates
if kernel.new_kernel_version():
    # Get the version string
    version = kernel.get_new_kernel_version()
    
    # Ask user to confirm
    kernel.confirm_kernel_update(version)
    
    # Proceed with system update
    # ... (DNF update happens here)
    
    # Rebuild initramfs for new kernel
    init.rebuild_initramfs(new_kernel=True)
    
    # Rebuild NVIDIA modules if present
    nvidia.rebuild_nvidia_modules()
else:
    print("No kernel updates available")
```

### Silent Mode Integration

```python
from core import kernel
from helper import cli_print_utility

cli_print_utility.print_header("Check Kernel Update", verbose)

new_kernel = kernel.new_kernel_version()

if new_kernel:
    version = kernel.get_new_kernel_version()
    kernel.confirm_kernel_update(version)
else:
    if verbose:
        print("No new kernel version detected.")
```

## Error Handling

### Expected Errors

```python
from core import kernel
from helper import runner

try:
    if kernel.new_kernel_version():
        version = kernel.get_new_kernel_version()
        kernel.confirm_kernel_update(version)
except runner.CommandError as e:
    print(f"DNF5 error: {e}")
    sys.exit(1)
except SystemExit as e:
    if e.code == 1:
        print("User cancelled kernel update")
    raise  # Re-raise to exit
```

### Handling User Cancellation

```python
try:
    # ... kernel update logic ...
except SystemExit as e:
    if e.code == 1:
        # User declined kernel update
        # Cleanup if needed
        pass
    raise  # Exit the program
```

## Testing

### Unit Tests

The kernel module has comprehensive unit tests in `tests/test_kernel_logic.py`:

1. **test_kernel_update_available**: Tests exit code 100 handling
2. **test_no_kernel_update**: Tests exit code 0 handling
3. **test_dnf_error_handling**: Tests error exit codes
4. **test_kernel_version_extraction**: Tests version parsing
5. **test_kernel_version_not_found**: Tests error when version not found

### Running Tests

```bash
python3 tests/test_kernel_logic.py
```

## Design Decisions

### Why Check kernel* Instead of kernel-core?

Using `kernel*` catches all kernel-related packages:
- kernel-core
- kernel-modules
- kernel-devel
- etc.

This ensures we detect kernel updates regardless of which package triggers it.

### Why Separate Check and Get Functions?

**Separation of concerns:**
- `new_kernel_version()`: Quick boolean check (used for flow control)
- `get_new_kernel_version()`: Detailed version extraction (used for display)

This allows checking without parsing if version isn't needed.

### Why SystemExit Instead of Returning False?

When a user declines a kernel update, the entire update process should stop, not just the kernel update. `SystemExit` ensures the program terminates gracefully.

## Related Modules

- **init.py**: Rebuilds initramfs after kernel updates
- **nvidia.py**: Rebuilds NVIDIA modules after kernel updates
- **runner.py**: Executes DNF5 commands
- **cli.py**: Displays user prompts and status

## References

- DNF5 Documentation: https://dnf5.readthedocs.io/
- Kernel Updates on Fedora: https://docs.fedoraproject.org/en-US/quick-docs/kernel/
- Dracut (initramfs): https://github.com/dracutdevs/dracut

