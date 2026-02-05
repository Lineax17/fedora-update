"""Command-line interface utilities module.

This module provides functions for displaying formatted output, progress indicators,
and interactive elements in the terminal.
"""

import sys
import time
import threading


def print_output(function, verbose: bool = False, description: str = "Processing"):
    """Execute a function with either verbose output or spinner animation.

    In verbose mode, executes the function and displays its output directly.
    In silent mode, shows an animated spinner during execution.

    Args:
        function: Callable that accepts a verbose parameter and performs an operation.
        verbose: If True, show full output; if False, show spinner (default).
        description: Description text to display with the spinner.
    """
    if verbose:
        result = function(verbose)
        if isinstance(result, str):
            print(result)
    else:
        run_with_spinner(lambda: function(verbose), description)


def run_with_spinner(function, description: str):
    """Execute a function while displaying an animated spinner.

    Shows a rotating spinner animation during function execution and displays
    a success (✅) or failure (❌) indicator upon completion.

    Args:
        function: Callable to execute (should not accept parameters).
        description: Description message to display with the spinner.

    Raises:
        Exception: Re-raises any exception from the function after showing failure status.
    """
    spinner_chars = ['-', '\\', '|', '/']
    spinner_index = 0
    is_running = True
    error_occurred = False

    def spin():
        """Display the spinner animation while the function is running."""
        nonlocal spinner_index
        while is_running:
            # Clear line and print spinner frame
            sys.stdout.write(f'\r\033[2K{spinner_chars[spinner_index]} {description}...')
            sys.stdout.flush()
            spinner_index = (spinner_index + 1) % len(spinner_chars)
            time.sleep(0.1)

    # Start spinner in separate thread
    spinner_thread = threading.Thread(target=spin, daemon=True)
    spinner_thread.start()

    try:
        # Execute the function
        function()
    except Exception as e:
        error_occurred = True
        raise
    finally:
        # Stop spinner
        is_running = False
        spinner_thread.join()

        # Show result
        if error_occurred:
            sys.stdout.write(f'\r\033[2K❌ {description} (failed)\n')
        else:
            sys.stdout.write(f'\r\033[2K✅ {description}\n')
        sys.stdout.flush()

def print_header(string: str, verbose: bool = False):
    """Print a formatted header with decorative borders.

    Displays the given string as a centered header surrounded by hash symbols.
    Only prints in verbose mode; silently returns in silent mode.

    Example output:
        #################
        #     Title     #
        #################

    Args:
        string: The text to display in the header.
        verbose: If True, print the header; if False, do nothing (default).
    """
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

    print("\n")