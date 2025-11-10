#!/bin/bash

# Global variables
new_kernel_version=true
VERBOSE=false
SPINNER_CHARS=( '-' '\' '|' '/' )

# Parse command line arguments
case "$1" in
    -l|--log|--verbose)
        VERBOSE=true
        ;;
    "")
        VERBOSE=false
        ;;
    *)
        echo "Usage: fedora-update [-l]"
        echo "  -l    Show live output during update"
        exit 1
        ;;
esac

# Print a section header (verbose mode only)
print_header() {
    if [ "$VERBOSE" = false ]; then
        return
    fi

    local title="$1"
    echo
    if command -v figlet >/dev/null 2>&1; then
        figlet "$title"
    else
        local title_upper=$(echo "$title" | tr '[:lower:]' '[:upper:]')
        local line_length=${#title_upper}
        local total_length=$((line_length + 12))
        
        printf '#%.0s' $(seq 1 $total_length)
        echo
        echo "#     $title_upper     #"
        printf '#%.0s' $(seq 1 $total_length)
        echo
    fi
    echo
}

# Print message (verbose mode only)
print_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo "$@"
    fi
}

# Draws a spinner while a given command is running (silent mode only)
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

# Redirect output based on mode
redirect_output() {
    if [ "$VERBOSE" = true ]; then
        "$@"
    else
        "$@" >/dev/null 2>&1
    fi
}

# Ensure sudo is authenticated once and keep it alive for the duration of the script
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

    # Keep sudo timestamp updated in the background until this script exits
    (
        while true; do
            # Ensure we're still the child of the original script
            [ -d "/proc/$PPID" ] || exit 0
            sudo -n true 2>/dev/null || exit 0
            sleep 60
            # Stop refreshing if parent script exits
            kill -0 "$PPID" 2>/dev/null || exit 0
        done
    ) &
    SUDO_KEEPALIVE_PID=$!

    # Ensure background refresher is cleaned up on exit and all signals
    trap 'kill $SUDO_KEEPALIVE_PID 2>/dev/null || true' EXIT INT TERM
}

main() {
    setup_sudo_keepalive
    
    if [ "$VERBOSE" = true ]; then
        print_header "Performing full system upgrade"
    fi
    
    run_with_spinner "Require DNF5" require_dnf_5
    check_kernel_updates
    confirm_kernel_upgrade
    run_with_spinner "Apply DNF Updates" apply_dnf_upgrade
    run_with_spinner "Clean DNF Cache" clean_dnf_cache
    run_with_spinner "Update Flatpak" update_flatpak
    run_with_spinner "Update Snap" update_snap
    run_with_spinner "Check NVIDIA Akmods" check_nvidia_akmods
    run_with_spinner "Ensure Initramfs" ensure_initramfs
    run_success_message
}

require_dnf_5() {
    if ! command -v dnf5 >/dev/null 2>&1; then
        echo "Error: dnf5 is required but not found in PATH."
        exit 1
    fi
}

check_kernel_updates() {
    print_header "Check Kernel Updates"
    
    dnf5 check-upgrade -q 'kernel*' >/dev/null 2>&1
    exit_code=$?
    
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

apply_dnf_upgrade() {
    print_header "Apply DNF Upgrade"
    redirect_output sudo dnf5 --refresh upgrade -y
}

# Clean DNF cache to prevent accumulation (Fedora 42 specific)
clean_dnf_cache() {
    print_header "Clean DNF Cache"
    print_verbose "Cleaning DNF package cache..."
    redirect_output sudo dnf5 clean packages
    print_verbose "Cleaning old DNF metadata..."
    redirect_output sudo dnf5 clean metadata --setopt=metadata_expire=1d
}

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

update_snap() {
    print_header "Update Snap"
    
    if command -v snap >/dev/null 2>&1; then
        print_verbose "snap is installed – run 'snap refresh'..."
        redirect_output sudo snap refresh
    else
        print_verbose "snap is not installed."
    fi
}

# Rebuild Nvidia drivers (Nvidia users only)
check_nvidia_akmods() {
    print_header "Check NVIDIA Akmods"
    
    if rpm -q akmods >/dev/null 2>&1 && rpm -qa | grep -q '^akmod-'; then
        redirect_output sudo akmods
    else
        print_verbose "Skipping akmods: no 'akmods' package installed."
    fi
}

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

run_success_message() {
    print_header "System Upgrade Finished"
    
    if [ "$VERBOSE" = false ]; then
        if command -v figlet >/dev/null 2>&1; then
            figlet "System Upgrade Finished"
        else
            echo
            echo "########################################"
            echo "#                                      #"
            echo "#        SYSTEM UPGRADE FINISHED       #"
            echo "#                                      #"
            echo "########################################"
            echo
        fi
    fi
}

get_new_kernel_version() {
    local version
    version=$(dnf5 check-update 'kernel-core' 2>/dev/null \
        | awk '/^kernel-core/ {print $2; exit}')
    
    if [ -n "$version" ]; then
        echo "$version"
        return 0
    else
        return 1
    fi
}

# Call main entrypoint
main