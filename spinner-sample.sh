#!/usr/bin/env bash

# Spinner symbols
SPINNER_CHARS='-\|/'

# Draws a spinner while a given command is running
run_with_spinner() {
    local message="$1"
    shift

    printf "⏳ %s..." "$message"

    # Start command in background
    "$@" &
    local cmd_pid=$!

    # Spinner loop
    while kill -0 "$cmd_pid" 2>/dev/null; do
        for c in $(echo "$SPINNER_CHARS" | sed -e 's/\(.\)/\1 /g'); do
            printf "\r%s %s..." "$c" "$message"
            sleep 0.1
        done
    done

    wait "$cmd_pid"
    local exit_code=$?

    # Clear spinner and show result
    if [[ $exit_code -eq 0 ]]; then
        printf "\r✅ %s\n" "$message"
    else
        printf "\r❌ %s (failed)\n" "$message"
    fi

    return $exit_code
}

# Example dummy tasks
require_dnf_5() { sleep 1; }
check_kernel_updates() { sleep 1; }
apply_dnf_upgrade() { sleep 3; }
update_flatpak() { sleep 2; }
update_snap() { sleep 1; }
check_nvidia_akmods() { sleep 1; }
ensure_initramfs() { sleep 1; }
run_success_message() { echo "System upgrade finished!"; }

main() {
    run_with_spinner "Require DNF5" require_dnf_5
    run_with_spinner "Check Kernel Updates" check_kernel_updates
    run_with_spinner "Apply DNF Updates" apply_dnf_upgrade
    run_with_spinner "Update Flatpak" update_flatpak
    run_with_spinner "Update Snap" update_snap
    run_with_spinner "Check NVIDIA Akmods" check_nvidia_akmods
    run_with_spinner "Ensure Initramfs" ensure_initramfs
    run_success_message
}

main
