#!/bin/bash

set -e  # Exit on error

# Check if rpmbuild is installed
if ! command -v rpmbuild >/dev/null 2>&1; then
    echo "Error: rpmbuild is not installed."
    echo "Install it with: sudo dnf install rpm-build"
    exit 1
fi

# Extract version from spec file
VERSION=$(grep -E "^Version:" fedora-update.spec | awk '{print $2}')

if [ -z "$VERSION" ]; then
    echo "Error: Could not extract version from fedora-update.spec"
    exit 1
fi

echo "Building version: $VERSION"

BUILD_DIR="$HOME/fedora-update"

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
tar czf ~/rpmbuild/SOURCES/fedora-update-${VERSION}.tar.gz -C ~ fedora-update

# Clean up temporary build directory
rm -rf "$BUILD_DIR"

# Build the RPM package
echo "Building RPM package..."
rpmbuild -ba ~/rpmbuild/SPECS/fedora-update.spec

echo "✅ Build complete! RPMs are in ~/rpmbuild/RPMS/"
