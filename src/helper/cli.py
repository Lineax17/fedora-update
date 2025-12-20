def version(version_number: str) -> None:
    """Prints the version number of the application."""
    print(f"Fedora Update Control Kit: {version_number}")

def help() -> None:
    """Prints help information for the application."""
    help_text = """
    Usage: fedora-update (fedora-upgrade|fuck) [-l|--log|--verbose] [-b|--brew|--brew-upgrade]

    Automated system upgrade script for Fedora Linux.

    Options:
        -l, --log, --verbose       Show detailed output during upgrade process
        -b, --brew, --brew-upgrade Update Homebrew packages (if installed)
        -h, --help                 Display this help message
        -v, --version              Show current version of tool

    Examples:
        fedora-update              # Run in silent mode with spinner
        fedora-update -l           # Run in verbose mode with detailed output
        fedora-update -b           # Update Homebrew packages

    Aliases:
        fedora-upgrade, fuck       # Symlinks to this script; behave identically

    Note:
        Multiple options can be combined. The -b flag only runs if Homebrew is installed.
    """
    print(help_text)

