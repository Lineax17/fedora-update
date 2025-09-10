#!/bin/bash

set -euo pipefail

# -----------------------------
# Logging helpers
# -----------------------------
log_info()  { printf "[INFO] %s\n"  "$*"; }
log_warn()  { printf "[WARN] %s\n"  "$*"; }
log_error() { printf "[ERROR] %s\n" "$*" 1>&2; }

# -----------------------------
# Globals (booleans as strings: "true"/"false")
# -----------------------------
HAS_UPDATES="false"
HAS_KERNEL_UPDATE="false"

# -----------------------------
# Pre-flight
# -----------------------------
require_dnf5_or_exit() {
	if ! command -v dnf5 >/dev/null 2>&1; then
		log_error "dnf5 is required but not found in PATH."
		exit 1
	fi
}

# Determine if any DNF updates are available. Sets HAS_UPDATES to true/false.
check_updates() {
	if dnf5 -q --refresh check-upgrade >/dev/null 2>&1; then
		# Exit code 0 means no updates
		HAS_UPDATES="false"
		return 0
	else
		rc=$?
		if [ "$rc" -eq 100 ]; then
			# 100 means updates available
			HAS_UPDATES="true"
			return 0
		else
			# Any other code: treat as unknown; be conservative and assume updates
			log_warn "'dnf5 check-upgrade' failed (RC=$rc). Assuming updates might be available."
			HAS_UPDATES="true"
			return 0
		fi
	fi
}

# Check for kernel updates; prompt for confirmation if present
check_and_confirm_kernel_update_if_any() {
	[ "$HAS_UPDATES" = "true" ] || return 0

	dnf5 -q check-upgrade 'kernel*' >/dev/null 2>&1
	rc=$?
	if [ "$rc" -eq 100 ]; then
		HAS_KERNEL_UPDATE="true"
		log_info "Kernel update detected. The following kernel packages have updates available:"
		dnf5 --refresh list upgrades 'kernel*' || true
		echo
		read -r -p "Proceed and install the kernel update? [y/N]: " confirm
		case "$confirm" in
			[yY]|[yY][eE][sS]) ;;
			*)
				log_warn "Aborted by user: kernel update detected and not confirmed."
				exit 1
				;;
		esac
	elif [ "$rc" -ne 0 ] && [ "$rc" -ne 100 ]; then
		log_warn "'dnf5 check-upgrade kernel*' failed (RC=$rc). Skipping kernel-specific confirmation."
	fi
}

# Perform system upgrade only if updates are available
perform_system_upgrade_if_needed() {
	if [ "$HAS_UPDATES" = "true" ]; then
		log_info "Running system upgrade via dnf5..."
		sudo dnf5 --refresh upgrade -y
	else
		log_info "No package updates available via dnf5. Skipping system upgrade step."
	fi
}

# Update Flatpaks unconditionally
update_flatpaks() {
	log_info "Updating Flatpak apps and runtimes..."
	flatpak update -y || log_warn "Flatpak update encountered issues."
}

# Rebuild NVIDIA akmods if akmods and at least one akmod-* package are installed
rebuild_nvidia_akmods_if_installed() {
	if rpm -q akmods >/dev/null 2>&1 && rpm -qa | grep -q '^akmod-'; then
		log_info "Rebuilding akmods (NVIDIA users only)..."
		sudo akmods
	else
		log_info "Skipping akmods: 'akmods' missing or no akmod-* packages installed."
	fi
}

# Run dracut only if we had package updates
rebuild_initramfs_if_needed() {
	if [ "$HAS_UPDATES" = "true" ]; then
		log_info "Rebuilding initramfs via dracut..."
		sudo dracut -f --regenerate-all
	else
		log_info "No package updates installed; skipping dracut."
	fi
}

main() {
	require_dnf5_or_exit

	# 1) Check for updates (boolean)
	check_updates

	# 2) If updates include kernel, confirm with user
	check_and_confirm_kernel_update_if_any

	# 3) Perform system upgrade (only if updates exist)
	perform_system_upgrade_if_needed

	# 4) Update Flatpaks
	update_flatpaks

	# 5) NVIDIA akmods
	rebuild_nvidia_akmods_if_installed

	# 6) Run dracut only if updates were installed
	rebuild_initramfs_if_needed

	log_info "System upgrade completed. Go tell everyone you use Linux!"
}

main "$@"
