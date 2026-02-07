# Sudo Keepalive Module Documentation

Detailed documentation for the `sudo_keepalive` module (`src/helper/sudo_keepalive.py`).

## Overview

The sudo_keepalive module maintains sudo privileges throughout script execution by periodically refreshing the sudo timestamp in the background. This eliminates repeated password prompts during long-running operations in Tuxgrade.

## Module Functions

### `start(refresh_interval: int = 60) -> None`

Starts the global sudo keepalive thread.

#### Implementation Details

1. **Root Check**: Skips if already running as root (EUID=0)
2. **Sudo Validation**: Requests sudo password once (`sudo -v`)
3. **Background Thread**: Launches daemon thread executing `sudo -n true` every 60 seconds
4. **Automatic Cleanup**: Registers handlers for atexit, SIGINT, and SIGTERM

#### Parameters

- `refresh_interval` (int): Seconds between refreshes (default: 60)

#### Exceptions

- `SystemExit`: Raised when sudo validation fails

#### Usage Example

```python
from helper import sudo_keepalive

sudo_keepalive.start()
# Execute sudo commands without password prompts
```

#### Behavior When Already Running

If called while already active, logs a warning but doesn't fail:

```python
sudo_keepalive.start()
sudo_keepalive.start()  # Warning: "Sudo keepalive is already running"
```

---

### `stop() -> None`

Stops the global sudo keepalive thread.

#### Implementation Details

Sets the stop event and waits for the background thread to terminate gracefully.

#### Usage Example

```python
from helper import sudo_keepalive

sudo_keepalive.stop()
```

#### Idempotent Behavior

Safe to call even if not running:

```python
sudo_keepalive.stop()  # No error if already stopped
```

---

### `is_running() -> bool`

Checks if the keepalive thread is currently active.

#### Return Value

- `True`: Keepalive thread is running
- `False`: Keepalive thread is not running

#### Usage Example

```python
from helper import sudo_keepalive

if sudo_keepalive.is_running():
    print("Keepalive active")
else:
    print("Keepalive not running")
```

---

### `class SudoKeepalive`

Internal class for direct instantiation when more control is needed.

#### Methods

- `start() -> None`: Starts the keepalive thread
- `stop() -> None`: Stops the keepalive thread
- `is_running() -> bool`: Returns thread status

#### Usage Example

```python
from helper.sudo_keepalive import SudoKeepalive

keepalive = SudoKeepalive(refresh_interval=30)
keepalive.start()
# ... operations ...
keepalive.stop()
```

**Note:** The module-level functions use a global singleton instance. Direct instantiation is rarely needed.

## Usage Examples

### Basic Usage

```python
from helper import sudo_keepalive, runner

def main():
    sudo_keepalive.start()

    try:
        runner.run(["sudo", "dnf", "update", "-y"])
        runner.run(["sudo", "dnf", "clean", "all"])
    finally:
        sudo_keepalive.stop()
```

### With Error Handling

```python
from helper import sudo_keepalive, runner

def main():
    print("Starting system update...")

    sudo_keepalive.start()

    try:
        # DNF updates
        runner.run(["sudo", "dnf", "update", "-y"])

        # Flatpak updates
        runner.run(["sudo", "flatpak", "update", "-y"])

        # NVIDIA akmods
        runner.run(["sudo", "akmods", "--force"])

        print("✅ Update completed successfully")
        return 0

    except runner.CommandError as e:
        print(f"❌ Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n⚠️  Aborted by user")
        return 130
    finally:
        sudo_keepalive.stop()
```

### Custom Refresh Interval

```python
from helper import sudo_keepalive

# Refresh every 30 seconds instead of 60
sudo_keepalive.start(refresh_interval=30)
```

### Integration with main.py

```python
from helper import sudo_keepalive, runner

def main():
    sudo_keepalive.start()

    try:
        update_dnf()
        update_flatpak()
        update_nvidia()
    except KeyboardInterrupt:
        print("\nUpdate cancelled")
        raise SystemExit(130)
    finally:
        sudo_keepalive.stop()
```

## Technical Details

### Threading Architecture

- **Daemon Thread**: Automatically terminates when main process exits
- **Event-Based**: Uses `threading.Event()` for clean shutdown
- **Non-Blocking**: Waits with timeout instead of sleep

**Implementation:**

```python
def _refresh_loop(self):
    while not self._stop_event.is_set():
        self._refresh_sudo()
        self._stop_event.wait(self.refresh_interval)  # Interruptible wait
```

### Cleanup Mechanisms

1. **atexit**: Registered during `start()`, runs on normal exit
2. **Signal Handlers**: Catches SIGINT (Ctrl+C) and SIGTERM
3. **try-finally**: Additional protection in main script

**Registration:**

```python
atexit.register(self.stop)
signal.signal(signal.SIGINT, self._handle_signal)
signal.signal(signal.SIGTERM, self._handle_signal)
```

### Security

- **Minimal Privileges**: Thread only executes `sudo -n true`, no other commands
- **User Control**: Initial password prompt gives user full control
- **Automatic Timeout**: Thread stops automatically if refresh fails

### Root Handling

When the script is already running as root (EUID=0), the keepalive does nothing:

```python
if os.geteuid() == 0:
    logging.debug("Already running as root, sudo keepalive not needed")
    return
```

**Why?** Root doesn't need sudo, so the keepalive would be redundant.

## Logging

The module uses Python's logging framework for diagnostics.

### Debug Messages

- `"Already running as root, sudo keepalive not needed"`
- `"Sudo keepalive started (refresh every 60s)"`
- `"Sudo timestamp refreshed"`
- `"Stopping sudo keepalive"`

### Warnings

- `"Sudo keepalive is already running"`
- `"Failed to refresh sudo timestamp"`

### Errors

- `"Error refreshing sudo: {exception}"`
- `"Sudo validation failed: {exception}"`

### Enabling Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
# Now keepalive debug messages will be displayed
```

## Best Practices

### ✅ DO

```python
# Always use finally for cleanup
sudo_keepalive.start()
try:
    # ... code ...
finally:
    sudo_keepalive.stop()

# Start only once per process (singleton pattern)
sudo_keepalive.start()
```

### ❌ DON'T

```python
# No cleanup - thread keeps running!
sudo_keepalive.start()
# ... code ...

# Multiple starts (works but unnecessary)
sudo_keepalive.start()
sudo_keepalive.start()  # Warning: Already running
```

## Testing

### Run Test Suite

```bash
python3 tests/sudo_keepalive/test_basic.py
python3 tests/sudo_keepalive/test_cross_module.py
```

### Test Coverage

The tests verify:

- Start/stop functionality
- Multiple sudo commands without password re-prompt
- `is_running()` status
- Cleanup on exit
- Signal handling (SIGINT, SIGTERM)

### Example Test

```python
def test_sudo_commands_without_password():
    sudo_keepalive.start()

    # These should all succeed without password prompts
    runner.run(["sudo", "true"])
    runner.run(["sudo", "ls", "/root"])

    sudo_keepalive.stop()
```

## Compatibility

- **Python**: 3.10+
- **OS**: Linux/Unix (sudo must be available)
- **Dependencies**: Python standard library only (subprocess, threading, signal, atexit)

## See Also

- [runner.md](runner.md) - Command execution
- [cli.md](cli.md) - User interface
- [Architecture](../architecture.md) - System design
