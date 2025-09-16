#!/bin/bash

new_kernel_version=true

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

main() {
    run_with_spinner "Require DNF5" require_dnf_5
    run_with_spinner "Check Kernel Updates" check_kernel_updates
    confirm_kernel_upgrade_if_needed
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
    if [ "$exit_code" -eq 100 ]; then
        new_kernel_version=true
    elif [ "$exit_code" -eq 0 ]; then
        new_kernel_version=false
    else
        echo "Error: 'dnf5 check-upgrade kernel*' failed (exit_code=$exit_code)." >&2
        exit 1
    fi
}

confirm_kernel_upgrade_if_needed() {
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
        #echo "flatpak is installed – run 'flatpak update -y'..."
        flatpak update -y >/dev/null 2>&1
    fi
}

update_snap() {
    if command -v snap >/dev/null 2>&1; then
        #echo "snap is installed – run 'snap refresh'..."
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
        #echo "Rebuilding initramfs..."
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