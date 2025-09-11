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
        sudo snap refresh >/dev/null
    else
        echo "snap is not installed."
    fi
}

# Rebuild Nvidia drivers (Nvidia users only)
check_nvidia_akmods() {
    if rpm -q akmods >/dev/null 2>&1 && rpm -qa | grep -q '^akmod-'; then
        sudo akmods >/dev/null
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