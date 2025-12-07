#!/usr/bin/env bash

#######################################################################################################
## Script Name:   fedora-update
## Description:   Fedora Update Control Kit is an automated system upgrade script for Fedora Linux 
##                with support for DNF5, Flatpak, Snap, Homebrew and NVIDIA akmods. Provides both
##                silent mode (with ASCI animation) and verbose mode (detailed output).
## Usage:         fedora-update (fedora-upgrade|fuck) [-l|--log|--verbose] [-b|--brew|--brew-upgrade]
## Author:        Lineax17
## Version:       1.3.5
## Requirements:  - Bash 4.0+
##                - dnf5
##                - sudo privileges
##                - Optional: flatpak, snap, brew, akmods
#######################################################################################################

set -euo pipefail

## Global variables
VERSION_NUMBER=1.3.5
new_kernel_version=true
VERBOSE=false
UPDATE_BREW=false
SPINNER_CHARS=( '-' '\' '|' '/' )

## Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -l|--log|--verbose)
            VERBOSE=true
            shift
            ;;
        -b|--brew|--brew-upgrade)
            UPDATE_BREW=true
            shift
            ;;
        -v|--version)
            cat << EOF
Fedora Update Control Kit ${VERSION_NUMBER}
EOF
            exit 0
            ;;
        -h|--help)
            cat << EOF
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

EOF
            exit 0
            ;;
        *)
            echo "Error: Unknown option '$1'" >&2
            echo "Usage: fedora-update [-l|--log|--verbose] [-b|--brew|--brew-upgrade]" >&2
            echo "Try 'fedora-update --help' for more information." >&2
            exit 1
            ;;
    esac
done

################################################################################
## Helper Functions
################################################################################

## Print a section header
## Displays formatted ASCII art header for section identification
## In verbose mode: Shows header for all sections
## In silent mode: Only shows first and final header
##
## Arguments:
##   $1 - Section title to display
## Returns:
##   0 on success
## Example:
##   print_header "System Update"
print_header() {
    local title="$1"
    local title_upper=$(echo "$title" | tr '[:lower:]' '[:upper:]')
    local line_length=${#title_upper}
    local total_length=$((line_length + 12))
    
    # In silent mode, only show the first and final header
    if [ "$VERBOSE" = false ] && [ "$title" != "Performing full system upgrade" ] && [ "$title" != "System Upgrade Finished" ]; then
        return
    fi
    
    echo
    printf '#%.0s' $(seq 1 $total_length)
    echo
    echo "#     $title_upper     #"
    printf '#%.0s' $(seq 1 $total_length)
    echo
    echo
}

## Print message in verbose mode only
## Outputs messages only when verbose flag is enabled
##
## Arguments:
##   $@ - Message to print
## Returns:
##   0 on success
## Example:
##   print_verbose "Processing files..."
print_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo "$@"
    fi
}

## Run command with spinner animation (silent mode only)
## In verbose mode, executes command directly with output
## In silent mode, shows spinner and success/failure status
##
## Arguments:
##   $1 - Description message for the spinner
##   $@ - Command and arguments to execute
## Returns:
##   Exit code of the executed command
## Example:
##   run_with_spinner "Installing packages" sudo dnf install -y package
run_with_spinner() {
    local message="$1"
    shift

    if [ "$VERBOSE" = true ]; then
        # In verbose mode, just run the command directly
        "$@"
        return $?
    fi

    # Start command in background
    "$@" &
    local cmd_pid=$!

    # Spinner loop
    while kill -0 "$cmd_pid" 2>/dev/null; do
        for c in "${SPINNER_CHARS[@]}"; do
            # Clear line and print spinner frame
            printf "\r\033[2K%s %s..." "$c" "$message"
            sleep 0.1
            # Stop early if command finished during this frame
            kill -0 "$cmd_pid" 2>/dev/null || break
        done
    done

    wait "$cmd_pid"
    local exit_code=$?

    # Clear spinner and show result
    if [[ $exit_code -eq 0 ]]; then
        printf "\r\033[2K✅ %s\n" "$message"
    else
        printf "\r\033[2K❌ %s (failed)\n" "$message"
    fi

    return $exit_code
}

## Redirect command output based on verbosity mode
## In verbose mode, shows all output
## In silent mode, suppresses stdout and stderr
##
## Arguments:
##   $@ - Command and arguments to execute
## Returns:
##   Exit code of the executed command
## Example:
##   redirect_output sudo dnf upgrade -y
redirect_output() {
    if [ "$VERBOSE" = true ]; then
        "$@"
    else
        "$@" >/dev/null 2>&1
    fi
}

################################################################################
## Core Functions
################################################################################

## Setup and maintain sudo privileges
## Prompts for sudo password once and keeps it alive in background
##
## Arguments:
##   None
## Returns:
##   0 on success, 1 if sudo is unavailable
## Example:
##   setup_sudo_keepalive
setup_sudo_keepalive() {
    # If already root, nothing to do
    if [ "$EUID" -eq 0 ]; then
        return 0
    fi

    # Prompt once for sudo and validate we can escalate
    if ! sudo -v; then
        echo "Error: sudo privileges are required to continue." >&2
        exit 1
    fi

    # Store main script PID before entering subshell
    local main_pid=$$
    
    # Keep sudo timestamp updated in the background until this script exits
    (
        while true; do
            sleep 60
            # Check if main script is still running
            kill -0 "$main_pid" 2>/dev/null || exit 0
            # Refresh sudo timestamp
            sudo -n true 2>/dev/null || exit 0
        done
    ) &
    SUDO_KEEPALIVE_PID=$!

    # Ensure background refresher is cleaned up on exit and all signals
    trap 'kill $SUDO_KEEPALIVE_PID 2>/dev/null || true' EXIT INT TERM
}

## Main execution flow
## Orchestrates the complete system upgrade process
##
## Arguments:
##   None
## Returns:
##   0 on success, non-zero on failure
## Example:
##   main
main() {
    setup_sudo_keepalive
    
    print_header "Performing full system upgrade"
    
    run_with_spinner "Require DNF5" require_dnf_5
    check_kernel_updates
    confirm_kernel_upgrade
    run_with_spinner "Apply DNF Updates" apply_dnf_upgrade
    run_with_spinner "Clean DNF Cache" clean_dnf_cache
    run_with_spinner "Update Flatpak" update_flatpak
    run_with_spinner "Update Snap" update_snap
    
    if [ "$UPDATE_BREW" = true ]; then
        run_with_spinner "Update Homebrew" update_brew
    fi
    
    run_with_spinner "Check NVIDIA Akmods" check_nvidia_akmods
    run_with_spinner "Ensure Initramfs" ensure_initramfs
    print_header "System Upgrade Finished"
}

## Verify DNF5 is installed and available
## Checks if dnf5 command exists in PATH
##
## Arguments:
##   None
## Returns:
##   0 if dnf5 is available, exits with 1 if not found
## Example:
##   require_dnf_5
require_dnf_5() {
    if ! command -v dnf5 >/dev/null 2>&1; then
        echo "Error: dnf5 is required but not found in PATH."
        exit 1
    fi
}

## Check for available kernel updates
## Queries DNF5 for kernel package updates and sets global flag
##
## Arguments:
##   None
## Returns:
##   0 on success, 1 on dnf5 error
## Sets:
##   new_kernel_version - true if kernel update available, false otherwise
## Example:
##   check_kernel_updates
check_kernel_updates() {
    print_header "Check Kernel Updates"
    
    exit_code=0
    dnf5 check-upgrade -q 'kernel*' >/dev/null 2>&1 || exit_code=$?
    
    if [ "$exit_code" -eq 0 ]; then
        new_kernel_version=false
        print_verbose "No new kernel version detected."
    elif [ "$exit_code" -eq 100 ]; then
        new_kernel_version=true
    else
        echo "Error: 'dnf5 check-upgrade kernel*' failed (exit_code=$exit_code)." >&2
        exit 1
    fi
}

## Prompt user to confirm kernel upgrade
## Only prompts if kernel update is available
##
## Arguments:
##   None
## Returns:
##   0 if confirmed or no kernel update, 1 if user declines
## Example:
##   confirm_kernel_upgrade
confirm_kernel_upgrade() {
    if [ "$new_kernel_version" = true ]; then
        kernel_update_version=$(get_new_kernel_version)
        echo -n "Kernel update available: $kernel_update_version. Proceed? [y/N]: "
        read -r -n 1 confirm
        echo
        case "$confirm" in
            [yY]) return 0 ;;
            *) echo "Aborted: Kernel update detected and not confirmed."; exit 1 ;;
        esac
    fi
}

## Execute system package upgrade
## Runs DNF5 upgrade with repository refresh
##
## Arguments:
##   None
## Returns:
##   0 on success, non-zero on upgrade failure
## Example:
##   apply_dnf_upgrade
apply_dnf_upgrade() {
    print_header "Apply DNF Upgrade"
    redirect_output sudo dnf5 --refresh upgrade -y
}

## Clean DNF package cache and metadata
## Removes cached packages and old metadata to save disk space
##
## Arguments:
##   None
## Returns:
##   0 on success
## Example:
##   clean_dnf_cache
clean_dnf_cache() {
    print_header "Clean DNF Cache"
    print_verbose "Cleaning DNF package cache..."
    redirect_output sudo dnf5 clean packages
    print_verbose "Cleaning old DNF metadata..."
    redirect_output sudo dnf5 clean metadata --setopt=metadata_expire=1d
}

## Update Flatpak applications
## Updates all installed Flatpak apps and cleans old cache files
##
## Arguments:
##   None
## Returns:
##   0 on success
## Example:
##   update_flatpak
update_flatpak() {
    print_header "Update Flatpak"
    
    if command -v flatpak >/dev/null 2>&1; then
        print_verbose "flatpak is installed – run 'flatpak update -y'..."
        redirect_output flatpak update -y
        # Clean old Flatpak cache files
        print_verbose "Cleaning old Flatpak cache files (>7 days)..."
        find /var/tmp -name "flatpak-cache-*" -type d -mtime +7 -exec rm -rf {} + 2>/dev/null || true
    else
        print_verbose "flatpak is not installed."
    fi
}

## Update Snap applications
## Refreshes all installed Snap packages
##
## Arguments:
##   None
## Returns:
##   0 on success
## Example:
##   update_snap
update_snap() {
    print_header "Update Snap"
    
    if command -v snap >/dev/null 2>&1; then
        print_verbose "snap is installed – run 'snap refresh'..."
        redirect_output sudo snap refresh
    else
        print_verbose "snap is not installed."
    fi
}

## Update Homebrew packages
## Updates Homebrew and all installed packages if Homebrew is installed
##
## Arguments:
##   None
## Returns:
##   0 on success
## Example:
##   update_brew
update_brew() {
    print_header "Update Homebrew"
    
    if command -v brew >/dev/null 2>&1; then
        print_verbose "Homebrew is installed – updating..."
        redirect_output brew update
        print_verbose "Upgrading Homebrew packages..."
        redirect_output brew upgrade
        print_verbose "Cleaning up old Homebrew versions..."
        redirect_output brew cleanup
    else
        print_verbose "Homebrew is not installed."
    fi
}

## Rebuild NVIDIA kernel modules
## Rebuilds akmods if NVIDIA drivers are installed
##
## Arguments:
##   None
## Returns:
##   0 on success
## Example:
##   check_nvidia_akmods
check_nvidia_akmods() {
    print_header "Check NVIDIA Akmods"
    
    #if rpm -q akmods >/dev/null 2>&1 && rpm -qa | grep -q '^akmod-'; then
    if command -v akmods >/dev/null 2>&1; then
        redirect_output sudo akmods
    else
        print_verbose "Skipping akmods: no 'akmods' package installed."
    fi
}

## Regenerate initramfs for new kernel
## Rebuilds initramfs if kernel was updated and cleans temp files
##
## Arguments:
##   None
## Returns:
##   0 on success
## Example:
##   ensure_initramfs
ensure_initramfs() {
    print_header "Ensure Initramfs"
    
    if [ "$new_kernel_version" = true ]; then
        print_verbose "Rebuilding initramfs..."
        sudo dracut -f --regenerate-all
        # Clean temporary dracut files older than 1 day (silent mode only)
        if [ "$VERBOSE" = false ]; then
            sudo find /tmp /var/tmp -name "dracut.*" -mtime +1 -delete 2>/dev/null || true
        fi
    else
        print_verbose "No kernel update detected. Skipping initramfs rebuild..."
    fi
}

## Get version string of new kernel update
## Queries DNF5 for available kernel-core version
##
## Arguments:
##   None
## Returns:
##   0 if version found, 1 otherwise
## Outputs:
##   Kernel version string to stdout
## Example:
##   version=$(get_new_kernel_version)
get_new_kernel_version() {
    local version
    version=$(dnf5 check-update 'kernel-core' 2>/dev/null \
        | awk '/^kernel-core/ {print $2; exit}' || true)
    
    if [ -n "$version" ]; then
        echo "$version"
        return 0
    else
        return 1
    fi
}

################################################################################
## Main Entrypoint
################################################################################

# Call main entrypoint
main