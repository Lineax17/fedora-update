#!/bin/bash

new_kernel_version=true

# Print a section header with figlet if available, otherwise ASCII art
print_header() {
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

main() {
    setup_sudo_keepalive
    require_dnf_5
    check_kernel_updates
    apply_dnf_upgrade
    update_flatpak
    update_snap
    check_nvidia_akmods
    ensure_initramfs
    run_success_message
}

require_dnf_5() {
    print_header "Require DNF5"
    if ! command -v dnf5 >/dev/null 2>&1; then
	    echo "Error: dnf5 is required but not found in PATH."
	    exit 1
    fi
}

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

check_kernel_updates() {
    print_header "Check Kernel Updates"
    dnf5 -q check-upgrade 'kernel*' >/dev/null 2>&1
    exit_code=$?
    if [ "$exit_code" -eq 100 ]; then
        new_kernel_version=true
    elif [ "$exit_code" -eq 0 ]; then
        new_kernel_version=false
    else
        echo "Error: 'dnf5 check-upgrade kernel*' failed (exit_code=$exit_code)." >&2
        exit 1
    fi
}

apply_dnf_upgrade() {
    print_header "Apply DNF Upgrade"
    if [ "$new_kernel_version" = true ]; then
        kernel_update_version=$(get_new_kernel_version)
        echo -n "Kernel update available: $kernel_update_version. Proceed? [y/N]: "
        read -r -n 1 confirm
        echo
        case "$confirm" in
            [yY]) ;;
            *) echo "Aborted: Kernel update detected and not confirmed."; exit 1 ;;
        esac
    fi

    sudo dnf5 --refresh upgrade -y
}


update_flatpak() {
    print_header "Update Flatpak"
    if command -v flatpak >/dev/null 2>&1; then
        echo "flatpak is installed – run 'flatpak update -y'..."
        flatpak update -y 
    else
        echo "flatpak is not installed."
    fi
}

update_snap() {
    print_header "Update Snap"
    if command -v snap >/dev/null 2>&1; then
        echo "snap is installed – run 'snap refresh'..."
        sudo snap refresh
    else
        echo "snap is not installed."
    fi
}

# Rebuild Nvidia drivers (Nvidia users only)
check_nvidia_akmods() {
    print_header "Check NVIDIA Akmods"
    if rpm -q akmods >/dev/null 2>&1 && rpm -qa | grep -q '^akmod-'; then
        sudo akmods
    else
        echo "Skipping akmods: no 'akmods' package installed."
    fi
}

ensure_initramfs() {
    print_header "Ensure Initramfs"
    if [ "$new_kernel_version" = true ]; then
        echo "Rebuilding initramfs..."
        sudo dracut -f --regenerate-all
    else
        echo "No kernel update detected. Skipping initramfs rebuild..."
    fi
}

run_success_message() {
    print_header "System Upgrade Finished"
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