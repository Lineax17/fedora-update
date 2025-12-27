"""Sudo privilege persistence module.

Maintains sudo privileges throughout script execution by periodically
refreshing the sudo timestamp. This prevents sudo password prompts during
long-running operations.

Example:
    import sudo_keepalive

    sudo_keepalive.start()
    try:
        # Run commands that need sudo
        subprocess.run(["sudo", "dnf", "update"])
    finally:
        sudo_keepalive.stop()
"""

import os
import sys
import subprocess
import threading
import atexit
import signal
import logging


class SudoKeepalive:
    """Manages sudo privilege persistence via background refresh thread."""

    def __init__(self, refresh_interval: int = 60):
        """Initialize sudo keepalive manager.

        Args:
            refresh_interval: Seconds between sudo refreshes (default: 60).
        """
        self.refresh_interval = refresh_interval
        self._thread = None
        self._stop_event = threading.Event()
        self._running = False

    def start(self) -> None:
        """Start sudo keepalive background thread.

        Checks if already running as root (EUID=0), prompts for sudo password
        if needed, starts background refresh thread, and registers cleanup handlers.

        Raises:
            SystemExit: If sudo validation fails.
        """
        # If already root, nothing to do
        if os.geteuid() == 0:
            logging.debug("Already running as root, sudo keepalive not needed")
            return

        # If already running, don't start again
        if self._running:
            logging.warning("Sudo keepalive is already running")
            return

        # Validate sudo access (prompts for password if needed)
        if not self._validate_sudo():
            print("Error: sudo privileges are required to continue.", file=sys.stderr)
            sys.exit(1)

        # Start background refresh thread
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self._thread.start()
        self._running = True

        logging.debug(f"Sudo keepalive started (refresh every {self.refresh_interval}s)")

        # Register cleanup handlers
        atexit.register(self.stop)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def stop(self) -> None:
        """Stop the sudo keepalive background thread.

        Signals the refresh thread to stop and waits for it to terminate.
        Safe to call multiple times.
        """
        if not self._running:
            return

        logging.debug("Stopping sudo keepalive")
        self._stop_event.set()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

        self._running = False

    def is_running(self) -> bool:
        """Check if keepalive is currently running.

        Returns:
            True if the keepalive thread is active, False otherwise.
        """
        return self._running

    def _refresh_loop(self) -> None:
        """Background thread that periodically refreshes sudo timestamp.

        Runs in a loop until stop event is set, refreshing sudo privileges
        at the configured interval.
        """
        while not self._stop_event.is_set():
            # Wait for the refresh interval or until stop event
            if self._stop_event.wait(timeout=self.refresh_interval):
                break

            # Refresh sudo timestamp (non-interactive)
            try:
                result = subprocess.run(
                    ["sudo", "-n", "true"],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    logging.debug("Sudo timestamp refreshed")
                else:
                    logging.warning("Failed to refresh sudo timestamp")
                    break
            except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
                logging.error(f"Error refreshing sudo: {e}")
                break

    def _validate_sudo(self) -> bool:
        """Validate sudo access with initial prompt.

        Prompts the user for their password if needed and validates sudo access.

        Returns:
            True if sudo access is granted, False otherwise.
        """
        try:
            # Don't capture output so user can interact with sudo prompt
            result = subprocess.run(
                ["sudo", "-v"],
                timeout=60  # Give user time to enter password
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            logging.error(f"Sudo validation failed: {e}")
            return False

    def _signal_handler(self, signum, frame):
        """Handle signals for cleanup.

        Stops the keepalive thread when receiving termination signals
        (SIGINT, SIGTERM) and re-raises the signal for normal handling.

        Args:
            signum: Signal number.
            frame: Current stack frame.
        """
        logging.debug(f"Received signal {signum}, stopping keepalive")
        self.stop()
        # Re-raise the signal to allow normal handling
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)


# Global singleton instance
_keepalive_instance: SudoKeepalive | None = None


def start(refresh_interval: int = 60) -> None:
    """Start global sudo keepalive.

    Creates and starts a global singleton keepalive instance if it doesn't
    exist, or starts the existing instance.

    Args:
        refresh_interval: Seconds between sudo refreshes (default: 60).
    """
    global _keepalive_instance
    if _keepalive_instance is None:
        _keepalive_instance = SudoKeepalive(refresh_interval)
    _keepalive_instance.start()


def stop() -> None:
    """Stop global sudo keepalive.

    Stops the global singleton keepalive instance if it exists.
    Safe to call even if keepalive was never started.
    """
    global _keepalive_instance
    if _keepalive_instance is not None:
        _keepalive_instance.stop()


def is_running() -> bool:
    """Check if global sudo keepalive is running.

    Returns:
        True if the global keepalive is active, False otherwise.
    """
    global _keepalive_instance
    if _keepalive_instance is None:
        return False
    return _keepalive_instance.is_running()

