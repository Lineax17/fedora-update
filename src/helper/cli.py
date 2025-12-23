import sys
import time
import threading


def print_output(function, verbose_mode: bool, description: str = "Processing"):
    """
    Execute a function either with verbose output or with a spinner animation.

    Args:
        function: Callable to execute
        verbose_mode: If True, show full output; if False, show spinner
        description: Description text to show with the spinner
    """
    if verbose_mode:
        function()
    else:
        run_with_spinner(function, description)


def run_with_spinner(function, description: str):
    """
    Execute a function while displaying an animated spinner.
    Shows success (✅) or failure (❌) status after completion.

    Args:
        function: Callable to execute
        description: Description message for the spinner

    Raises:
        Exception: Re-raises any exception from the function after showing failure status
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
