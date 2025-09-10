#!/bin/bash

# Require dnf5
if ! command -v dnf5 >/dev/null 2>&1; then
	echo "Error: dnf5 is required but not found in PATH."
	exit 1
fi

# Check if kernel updates are available and ask for an extra confirmation
dnf5 -q check-upgrade 'kernel*' >/dev/null 2>&1
rc=$?
if [ "$rc" -eq 100 ]; then
	echo "Kernel update detected. The following kernel packages have updates available:"
	dnf5 --refresh list upgrades 'kernel*' || true
	echo
	read -r -p "Proceed and install the kernel update? [y/N]: " confirm
	case "$confirm" in
		[yY]|[yY][eE][sS])
			;;
		*)
			echo "Aborted: Kernel update detected and not confirmed."
			exit 1
			;;
	esac
elif [ "$rc" -ne 0 ] && [ "$rc" -ne 100 ]; then
	echo "Warning: 'dnf5 check-upgrade' failed (RC=$rc). Continuing without kernel check."
fi

sudo dnf5 --refresh upgrade -y 

flatpak update -y

# Rebuild Nvidia drivers (Nvidia users only)
if rpm -q akmods >/dev/null 2>&1 && rpm -qa | grep -q '^akmod-'; then
	sudo akmods
else
	echo "Skipping akmods: no 'akmods' package installed."
fi

# Rebuild inital ram filesystem (all users)

sudo dracut -f --regenerate-all

echo "System upgrade completed. Go tell everyone you use Linux!"
