#!/bin/bash

new_kernel_version=true

main() {
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

apply_dnf_upgrade() {
    if [ "$new_kernel_version" = true ]; then
        echo "Kernel update detected. The following kernel packages have updates available:"
        if ! dnf5 --refresh list upgrades 'kernel*'; then
            echo "Error: Could not retrieve kernel upgrade list. Aborting." >&2
            exit 1
        fi
        echo
        read -r -p "Proceed and install the kernel update? [y/N]: " confirm
        case "$confirm" in
            [yY]|[yY][eE][sS]) ;;
            *) echo "Aborted: Kernel update detected and not confirmed."; exit 1 ;;
        esac
    fi

    sudo dnf5 --refresh upgrade -y
}

update_flatpak() {
    if command -v flatpak >/dev/null 2>&1; then
        echo "flatpak is installed – run 'flatpak update -y'..."
        flatpak update -y
    else
        echo "flatpak is not installed."
    fi
}

update_snap() {
    if command -v snap >/dev/null 2>&1; then
        echo "snap is installed – run 'snap refresh'..."
        sudo snap refresh
    else
        echo "snap is not installed."
    fi
}

# Rebuild Nvidia drivers (Nvidia users only)
check_nvidia_akmods() {
    if rpm -q akmods >/dev/null 2>&1 && rpm -qa | grep -q '^akmod-'; then
        sudo akmods
    else
        echo "Skipping akmods: no 'akmods' package installed."
    fi
}

ensure_initramfs() {
    if [ "$new_kernel_version" = true ]; then
        echo "Rebuilding initramfs..."
        sudo dracut -f --regenerate-all
    else
        echo "No kernel update detected. Skipping initramfs rebuild..."
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

# Call main entrypoint
main