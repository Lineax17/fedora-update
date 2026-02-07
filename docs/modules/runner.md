# Runner Module Documentation

Detailed documentation for the `runner` module (`src/helper/runner.py`).

## Overview

The runner module provides a unified interface for executing shell commands with configurable error handling and output modes. It's the foundation for all command execution in Tuxgrade.

## Module Components

### `class CommandError(RuntimeError)`

Custom exception raised when a command execution fails.

#### Inheritance

```python
CommandError
  └─ RuntimeError
       └─ Exception
```

#### Usage

```python
from helper import runner

try:
    runner.run(["false"])  # Command that fails
except runner.CommandError as e:
    print(f"Command failed: {e}")
```

---

### `run(cmd, show_live_output=False, check=True) -> CompletedProcess`

Main command execution function with flexible configuration.

## Function Signature

```python
def run(
    cmd: list[str], 
    show_live_output: bool = False, 
    check: bool = True
) -> subprocess.CompletedProcess
```

## Parameters

### `cmd: list[str]`

The command to execute as a list of strings.

**Format:** `["command", "arg1", "arg2", ...]`

**Examples:**
```python
# Good - list format (safe)
runner.run(["ls", "-la", "/home"])
runner.run(["dnf5", "check-upgrade", "-q", "kernel*"])

# Bad - string format (unsafe, don't use)
# runner.run("ls -la /home")  # This won't work!
```

**Why list format?**
- Prevents shell injection vulnerabilities
- Handles arguments with spaces correctly
- No need to escape special characters

### `show_live_output: bool = False`

Controls output display mode.

| Value | Behavior | Use Case |
|-------|----------|----------|
| `False` (default) | Captures output, doesn't display | Silent mode, programmatic use |
| `True` | Displays output in real-time | Verbose mode, user feedback |

**Examples:**
```python
# Silent mode - capture output
result = runner.run(["ls", "-la"])
print(result.stdout)  # Access captured output

# Verbose mode - show live output
runner.run(["dnf", "update", "-y"], show_live_output=True)
# Output appears in terminal as it happens
```

### `check: bool = True`

Controls error handling behavior.

| Value | Behavior | Use Case |
|-------|----------|----------|
| `True` (default) | Raises `CommandError` on failure | Normal commands that must succeed |
| `False` | Returns result regardless of exit code | Checking command availability, special exit codes |

**Examples:**
```python
# Standard usage - fail on error
try:
    runner.run(["dnf5", "update", "-y"])
except runner.CommandError:
    print("Update failed!")

# Check without failing
result = runner.run(["flatpak", "--version"], check=False)
if result.returncode == 0:
    print("Flatpak is installed")
else:
    print("Flatpak not found")
```

## Return Value

Returns a `subprocess.CompletedProcess` object with:

- `returncode` (int): Exit code (0 = success)
- `stdout` (str): Standard output (if captured)
- `stderr` (str): Standard error (if captured)
- `args` (list[str]): The command that was run

**Example:**
```python
result = runner.run(["echo", "Hello"])
print(f"Exit code: {result.returncode}")  # 0
print(f"Output: {result.stdout}")         # "Hello\n"
print(f"Error: {result.stderr}")          # ""
```

## Exceptions

### `CommandError`

Raised when a command fails (exit code != 0) and `check=True`.

**Attributes:**
- Inherits from `RuntimeError`
- Contains the original command in args

**Handling:**
```python
try:
    runner.run(["false"])
except runner.CommandError as e:
    print(f"Command failed: {e}")
    # Access the original exception if needed
    # print(e.__cause__)
```

## Use Cases

### Use Case 1: Live Output (DNF Updates)

Display package manager output in real-time during updates.

```python
from helper import runner

# User sees progress as it happens
runner.run(
    ["sudo", "dnf5", "upgrade", "-y"],
    show_live_output=True
)
```

**Behavior:**
- Output streams to terminal in real-time
- User can see download progress, installation steps
- `stdout` and `stderr` are NOT captured
- Good for long-running, interactive commands

---

### Use Case 2: Command Existence Check

Check if a tool is installed without failing.

```python
from helper import runner

def check_flatpak_installed() -> bool:
    result = runner.run(
        ["flatpak", "--version"],
        check=False  # Don't raise exception
    )
    return result.returncode == 0

if check_flatpak_installed():
    print("Flatpak is available")
```

**Behavior:**
- Returns `CompletedProcess` even if command fails
- Allows checking exit code
- Good for optional dependencies

---

### Use Case 3: Special Exit Code Handling

Handle commands with meaningful non-zero exit codes.

```python
from helper import runner

def new_kernel_version() -> bool:
    result = runner.run(
        ["dnf5", "check-upgrade", "-q", "kernel*"],
        check=False
    )
    
    if result.returncode == 0:
        return False  # No updates
    elif result.returncode == 100:
        return True   # Updates available
    else:
        raise runner.CommandError("Unexpected exit code")
```

**Behavior:**
- Exit code 100 is valid (DNF5 "updates available")
- Can distinguish between different exit codes
- Good for commands with exit code conventions

## Implementation Details

### Internal Flow

```python
def run(cmd, show_live_output, check):
    logging.debug("Executing: %s", " ".join(cmd))
    
    try:
        if show_live_output:
            # Real-time output mode
            result = subprocess.run(cmd, check=check, text=True)
        else:
            # Capture mode
            result = subprocess.run(
                cmd,
                check=check,
                text=True,
                capture_output=True
            )
        return result
    except subprocess.CalledProcessError as e:
        logging.error("Command failed: %s", " ".join(cmd))
        if e.stderr:
            logging.debug(e.stderr.strip())
        raise CommandError(cmd) from e
```

### Key Decisions

**1. Always return `CompletedProcess`**
- Consistent interface
- Access to returncode, stdout, stderr
- Easier testing

**2. Text mode enabled**
- `text=True` returns strings, not bytes
- Easier to work with in Python
- Assumes UTF-8 encoding

**3. Logging integration**
- Debug log shows all executed commands
- Error log shows failed commands
- Stderr logged on failure

## Error Handling Patterns

### Pattern 1: Try-Except

```python
from helper import runner

try:
    runner.run(["some-command"])
    print("Success!")
except runner.CommandError:
    print("Failed!")
```

### Pattern 2: Check Parameter

```python
from helper import runner

result = runner.run(["some-command"], check=False)
if result.returncode == 0:
    print("Success!")
else:
    print(f"Failed with code {result.returncode}")
```

### Pattern 3: Specific Exit Codes

```python
from helper import runner

result = runner.run(["command"], check=False)

match result.returncode:
    case 0:
        print("Success")
    case 100:
        print("Special success code")
    case _:
        raise runner.CommandError("Unexpected failure")
```

## Testing

### Mocking runner.run()

```python
from unittest.mock import patch
from subprocess import CompletedProcess

def test_my_function():
    mock_result = CompletedProcess(
        args=["echo", "test"],
        returncode=0,
        stdout="test output\n",
        stderr=""
    )
    
    with patch('helper.runner.run', return_value=mock_result):
        # Test your function that uses runner.run()
        result = my_function()
        assert result == expected
```

### Testing Different Exit Codes

```python
def test_command_failure():
    mock_result = CompletedProcess(
        args=["false"],
        returncode=1,
        stdout="",
        stderr="error"
    )
    
    with patch('helper.runner.run', return_value=mock_result):
        result = runner.run(["false"], check=False)
        assert result.returncode == 1
```

## Performance Considerations

### Command Overhead

Each `runner.run()` call:
- Spawns a new process
- Minimal overhead (~1-2ms for simple commands)
- Output capture adds negligible overhead

### Long-Running Commands

For long-running commands:
- Use `show_live_output=True` for user feedback
- Output is not buffered, streams in real-time
- Process can be interrupted with Ctrl+C

### Parallel Execution

Runner doesn't support parallel execution. For multiple commands:

```python
# Sequential (current)
runner.run(["command1"])
runner.run(["command2"])

# Parallel (not supported, future consideration)
# Would need separate implementation
```

## Security Considerations

### Shell Injection Protection

✅ **Safe** - List format prevents injection:
```python
filename = "file; rm -rf /"
runner.run(["cat", filename])  # Safe - filename treated as literal
```

❌ **Unsafe** - String format allows injection:
```python
# Don't do this!
# os.system(f"cat {filename}")  # Dangerous!
```

### Sudo Usage

Commands with sudo are explicit:
```python
runner.run(["sudo", "dnf", "update"])  # Clear sudo usage
```

No implicit privilege escalation.

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from helper import runner
runner.run(["ls", "-la"])
# Logs: "Executing: ls -la"
```

### Capture stderr

```python
result = runner.run(["command"], check=False)
if result.returncode != 0:
    print(f"Error output: {result.stderr}")
```

## Related Modules

- **core/***: All core modules use runner for command execution
- **sudo_keepalive.py**: Uses subprocess directly (not runner)
- **cli.py**: Wraps runner calls with UI elements

## References

- Python subprocess: https://docs.python.org/3/library/subprocess.html
- Shell injection: https://owasp.org/www-community/attacks/Command_Injection

