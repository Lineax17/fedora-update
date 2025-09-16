#!/bin/bash

new_kernel_version=true

SPINNER_CHARS=( '-' '\' '|' '/' )

# Draws a spinner while a given command is running
run_with_spinner() {
    local message="$1"
    shift

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
            sudo -n true 2>/dev/null || exit 0
            sleep 60
            # Stop refreshing if parent script exits
            kill -0 "$PPID" 2>/dev/null || exit 0
        done
    ) &
    SUDO_KEEPALIVE_PID=$!

    # Ensure background refresher is cleaned up on exit
    trap 'kill $SUDO_KEEPALIVE_PID 2>/dev/null || true' EXIT
}

main() {
    setup_sudo_keepalive
    run_with_spinner "Require DNF5" require_dnf_5
    check_kernel_updates
    confirm_kernel_upgrade
    run_with_spinner "Apply DNF Updates" apply_dnf_upgrade
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
    dnf5 -q check-upgrade 'kernel*' >/dev/null 2>&1
    exit_code=$?
    if [ "$exit_code" -eq 0 ]; then
        new_kernel_version=false
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
    sudo dnf5 --refresh upgrade -y >/dev/null 2>&1
}


update_flatpak() {
    if command -v flatpak >/dev/null 2>&1; then
        flatpak update -y >/dev/null 2>&1
    fi
}

update_snap() {
    if command -v snap >/dev/null 2>&1; then
        sudo snap refresh >/dev/null 2>&1
    fi
}

# Rebuild Nvidia drivers (Nvidia users only)
check_nvidia_akmods() {
    if rpm -q akmods >/dev/null 2>&1 && rpm -qa | grep -q '^akmod-'; then
        sudo akmods >/dev/null 2>&1
    fi
}

ensure_initramfs() {
    if [ "$new_kernel_version" = true ]; then
        sudo dracut -f --regenerate-all
    fi
}

run_success_message() {
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