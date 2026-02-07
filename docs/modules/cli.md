# CLI Module Documentation

Detailed documentation for the `cli_print_utility` module (`src/helper/cli_print_utility.py`).

## Overview

The CLI module provides user interface components for Tuxgrade, including spinners, headers, and output formatting. It bridges the gap between silent mode (clean, minimal) and verbose mode (detailed, informative).

## Module Functions

### `print_output(function, verbose=False, description="Processing")`

High-level function that executes operations with appropriate UI feedback.

#### Signature

```python
def print_output(
    function: Callable,
    verbose: bool = False,
    description: str = "Processing"
) -> None
```

#### Parameters

**`function: Callable`**
- A function that accepts a `verbose` parameter
- Should perform the actual operation
- Can return a string for verbose output

**`verbose: bool = False`**
- `False`: Silent mode with spinner animation
- `True`: Verbose mode with live output

**`description: str = "Processing"`**
- Description shown during execution
- Used with spinner in silent mode

#### Behavior

**Silent Mode (verbose=False):**
```
⠋ Updating DNF packages...
```

Then becomes:
```
✅ Updating DNF packages
```

**Verbose Mode (verbose=True):**
```
Full command output displayed in real-time
```

#### Implementation

```python
def print_output(function, verbose=False, description="Processing"):
    if verbose:
        result = function(verbose)
        if isinstance(result, str):
            print(result)
    else:
        run_with_spinner(lambda: function(verbose), description)
```

#### Usage Examples

**Example 1: Simple function**

```python
from helper import cli_print_utility
from package_managers import dnf

cli_print_utility.print_output(
    dnf.update_dnf,
    verbose=False,
    description="Updating DNF packages"
)
```

**Example 2: Lambda for complex calls**

```python
from helper import cli_print_utility
from core import init

cli_print_utility.print_output(
    lambda verbose: init.rebuild_initramfs(new_kernel=True),
    verbose=True,
    description="Rebuilding initramfs"
)
```

**Example 3: Function with string return**
```python
def my_function(verbose: bool) -> str:
    # Do work...
    return "Operation completed successfully"

cli.print_output(my_function, verbose=True, description="Working")
# In verbose mode, prints: "Operation completed successfully"
```

---

### `run_with_spinner(function, description)`

Executes a function while displaying an animated spinner.

#### Signature

```python
def run_with_spinner(
    function: Callable[[], None],
    description: str
) -> None
```

#### Parameters

**`function: Callable[[], None]`**
- A function that takes NO parameters
- Performs the operation
- Can raise exceptions

**`description: str`**
- Description of the operation
- Displayed next to the spinner

#### Spinner Animation

**During execution:**
```
- Processing...
\ Processing...
| Processing...
/ Processing...
```

**On success:**
```
✅ Processing
```

**On failure:**
```
❌ Processing (failed)
```

#### Implementation Details

```python
def run_with_spinner(function, description):
    spinner_chars = ['-', '\\', '|', '/']
    spinner_index = 0
    is_running = True
    error_occurred = False

    def spin():
        nonlocal spinner_index
        while is_running:
            sys.stdout.write(f'\r\033[2K{spinner_chars[spinner_index]} {description}...')
            sys.stdout.flush()
            spinner_index = (spinner_index + 1) % len(spinner_chars)
            time.sleep(0.1)

    spinner_thread = threading.Thread(target=spin, daemon=True)
    spinner_thread.start()

    try:
        function()
    except Exception as e:
        error_occurred = True
        raise
    finally:
        is_running = False
        spinner_thread.join()

        if error_occurred:
            sys.stdout.write(f'\r\033[2K❌ {description} (failed)\n')
        else:
            sys.stdout.write(f'\r\033[2K✅ {description}\n')
        sys.stdout.flush()
```

#### Key Features

**1. Thread-based animation**
- Runs in background thread
- Doesn't block main operation
- Daemon thread (auto-cleanup)

**2. ANSI escape codes**
- `\r`: Return to line start
- `\033[2K`: Clear entire line
- Prevents text artifacts

**3. Error handling**
- Catches exceptions
- Shows ❌ on failure
- Re-raises exception after cleanup

#### Usage Examples

**Example 1: Simple operation**

```python
from helper import cli_print_utility
import time


def long_task():
    time.sleep(5)


cli_print_utility.run_with_spinner(long_task, "Processing data")
```

**Example 2: With lambda**

```python
from helper import cli_print_utility
from core import dnf

cli.run_with_spinner(
    lambda: dnf.update_dnf(show_live_output=False),
    "Updating packages"
)
```

**Example 3: Error handling**

```python
from helper import cli_print_utility


def failing_task():
    raise RuntimeError("Something went wrong")


try:
    cli.run_with_spinner(failing_task, "Attempting task")
except RuntimeError as e:
    print(f"Task failed: {e}")
# Output:
# ❌ Attempting task (failed)
# Task failed: Something went wrong
```

---

### `print_header(string, verbose=False)`

Prints a formatted header with decorative borders.

#### Signature

```python
def print_header(
    string: str,
    verbose: bool = False
) -> None
```

#### Parameters

**`string: str`**
- The text to display in the header

**`verbose: bool = False`**
- `False`: Nothing is printed (silent mode)
- `True`: Header is printed (verbose mode)

#### Output Format

```
#########################
#     Update DNF      #
#########################
```

#### Implementation

```python
def print_header(string, verbose=False):
    if not verbose:
        return

    string_length = len(string)
    spacing = 12

    print()
    for i in range(string_length + spacing):
        print("#", end="")
    print()

    print("#     " + string + "     #", end="")
    print()

    for i in range(string_length + spacing):
        print("#", end="")
    print()
```

#### Behavior

**Silent Mode:**
```python
cli.print_header("Test", verbose=False)
# No output
```

**Verbose Mode:**
```python
cli.print_header("Test", verbose=True)
# Output:
# ################
# #     Test     #
# ################
```

#### Usage Examples

**Example 1: Section headers**

```python
from helper import cli_print_utility

verbose = True

cli_print_utility.print_header("Check Kernel Updates", verbose)
# Check logic here

cli_print_utility.print_header("Update DNF Packages", verbose)
# Update logic here
```

**Example 2: Dynamic headers**

```python
from helper import cli_print_utility


def update_section(name: str, verbose: bool):
    cli.print_header(f"Update {name}", verbose)
    # Update logic


update_section("Flatpak", verbose=True)
```

---

## Usage Patterns

### Complete Update Flow

```python
from helper import cli_print_utility
from core import dnf
from package_managers import flatpak, snap

verbose = False

# Kernel check (always visible)
cli.print_header("Check Kernel Update", verbose)
# ... kernel logic ...

# DNF update
cli.print_header("Update DNF Packages", verbose)
cli.print_output(dnf.update_dnf, verbose, "Updating DNF packages")

# Flatpak update
cli.print_header("Update Flatpak Packages", verbose)
cli.print_output(flatpak.update_flatpak, verbose, "Updating Flatpak packages")

# Snap update
cli.print_header("Update Snap Packages", verbose)
cli.print_output(snap.update_snap, verbose, "Updating Snap packages")
```

### Silent vs Verbose Comparison

**Silent Mode Output:**
```
--- Tuxgrade ---

No new kernel version detected.
✅ Updating system packages
✅ Updating initramfs
✅ Updating Snap packages
✅ Updating Flatpak packages

--- System Upgrade finished ---
```

**Verbose Mode Output:**
```
--- Tuxgrade ---

############################
#  Check Kernel Update  #
############################
No new kernel version detected.

############################
#  Update System Packages   #
############################
Updating system packages...
[Full DNF output shown]

############################
#  Rebuild initramfs     #
############################
Rebuilding initramfs...
[Full dracut output shown]

--- System Upgrade finished ---
```

## Design Decisions

### Why Two Modes?

**Silent Mode:**
- For daily use
- Clean, minimal output
- Quick visual feedback
- Desktop/laptop users

**Verbose Mode:**
- For debugging
- Detailed information
- Log capture
- Server administrators

### Why Thread-Based Spinner?

**Alternatives considered:**
1. **Polling loop** - Would block main thread
2. **Async/await** - Too complex for this use case
3. **Background process** - Heavier overhead

**Thread approach:**
- Simple implementation
- Doesn't block operation
- Easy cleanup with daemon threads
- Minimal overhead

### Why ANSI Escape Codes?

**Alternatives considered:**
1. **Newlines** - Would create scroll spam
2. **Clear screen** - Would hide previous output
3. **Curses library** - Too heavy, compatibility issues

**ANSI escape codes:**
- Widely supported
- Minimal footprint
- Works in most terminals


### ANSI Codes Used

| Code | Purpose |
|------|---------|
| `\r` | Carriage return (move cursor to line start) |
| `\033[2K` | Clear entire line |
| `\n` | Newline |

### Fallback Behavior

If terminal doesn't support ANSI:
- Spinner may show artifacts
- Functionality still works
- Use verbose mode as workaround

## Threading Considerations

### Thread Safety

**Spinner thread:**
- Accesses only local variables
- Uses `nonlocal` for counter
- No shared state issues
- Daemon thread (auto-cleanup)

### Thread Lifecycle

```
Main Thread              Spinner Thread
     |                         |
     |--- start thread ------->|
     |                         |--- animate ---
     |--- do work ---          |--- animate ---
     |                         |--- animate ---
     |--- signal stop -------->|
     |--- join thread -------->|--- cleanup ---
     |<------------------------|
     |--- show result ---
```

### Cleanup Handling

```python
finally:
    is_running = False    # Signal thread to stop
    spinner_thread.join() # Wait for thread to finish
    # Show final result
```

## Performance Considerations

### Spinner Overhead

- **CPU**: <0.1% (sleeps 100ms between frames)
- **Memory**: ~10KB (thread stack)
- **Latency**: None (runs in background)

### Output Buffering

```python
sys.stdout.flush()  # Ensure immediate display
```

Without flush, output may be buffered and delayed.

## Error Handling

### Exception Propagation

```python
try:
    function()
except Exception as e:
    error_occurred = True
    raise  # Re-raise after showing ❌
```

Ensures:
1. User sees failure indicator
2. Exception isn't swallowed
3. Caller can handle error

### Cleanup Guarantee

```python
finally:
    # Always runs, even on exception
    is_running = False
    spinner_thread.join()
    # Show result
```

## Future Improvements

- [ ] Progress bars (percentage)
- [ ] Color support
- [ ] Terminal width detection
- [ ] Alternative spinner styles
- [ ] Log file integration
- [ ] Rich text formatting (using `rich` library)

## Related Modules

- **runner.py**: Executes commands wrapped by CLI functions
- **main.py**: Orchestrates CLI calls for update flow
- **core/***: All core modules use CLI for user feedback

## References

- ANSI Escape Codes: https://en.wikipedia.org/wiki/ANSI_escape_code
- Python Threading: https://docs.python.org/3/library/threading.html
- Terminal Control: https://www.ascii-code.com/

