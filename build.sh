#!/bin/bash

set -e  # Exit on error

# Check required RPM build tools
MISSING_PACKAGES=()

if ! command -v rpmbuild >/dev/null 2>&1; then
    echo "Error: rpmbuild is not installed."
    MISSING_PACKAGES+=("rpm-build")
fi

if ! command -v rpmdev-setuptree >/dev/null 2>&1; then
    echo "Error: rpmdev-setuptree is not installed."
    MISSING_PACKAGES+=("rpmdevtools")
fi

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo "Install missing packages with: sudo dnf install ${MISSING_PACKAGES[*]}"
    exit 1
fi

# Check if rpmbuild directory structure exists
if [ ! -d "$HOME/rpmbuild/SPECS" ] || [ ! -d "$HOME/rpmbuild/SOURCES" ] || [ ! -d "$HOME/rpmbuild/RPMS" ]; then
    echo "RPM build directory structure not found."
    echo "Setting up RPM build directories..."
    rpmdev-setuptree
fi

# Extract version from spec file
VERSION=$(grep -E "^Version:" fedora-update.spec | awk '{print $2}')

if [ -z "$VERSION" ]; then
    echo "Error: Could not extract version from fedora-update.spec"
    exit 1
fi

echo "Building version: $VERSION"

BUILD_DIR="$HOME/fedora-update-${VERSION}"

# Copy the spec file
cp fedora-update.spec ~/rpmbuild/SPECS/

# Prepare directory for tar.gz (remove if exists to ensure clean build)
if [ -d "$BUILD_DIR" ]; then
    echo "Removing existing build directory: $BUILD_DIR"
    rm -rf "$BUILD_DIR"
fi

# Create fresh build directory with all required files
mkdir -p "$BUILD_DIR"
cp fedora-update.sh "$BUILD_DIR/"
cp LICENSE "$BUILD_DIR/"
cp README.md "$BUILD_DIR/"

# Create tar.gz archive
echo "Creating tar.gz archive..."
tar czf ~/rpmbuild/SOURCES/fedora-update-${VERSION}.tar.gz -C ~ fedora-update-${VERSION}

# Clean up temporary build directory
rm -rf "$BUILD_DIR"

# Build the RPM package
echo "Building RPM package..."
rpmbuild -ba ~/rpmbuild/SPECS/fedora-update.spec

echo "✅ Build complete! RPMs are in ~/rpmbuild/RPMS/"
