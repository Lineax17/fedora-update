#!/bin/bash

set -e  # Exit on error

# Determine script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
OUTPUT_DIR="${OUTPUT_DIR:-$PROJECT_ROOT/output}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            echo "Usage: $0"
            echo ""
            echo "Build tuxgrade DEB package using Ubuntu container."
            echo ""
            echo "Options:"
            echo "  -h, --help    Show this help message"
            echo ""
            echo "Environment variables:"
            echo "  OUTPUT_DIR    Override output directory (default: $PROJECT_ROOT/output)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check for Docker
if ! command -v docker >/dev/null 2>&1; then
    echo "Error: docker is not installed."
    echo "Install it with: https://docs.docker.com/get-docker/"
    exit 1
fi

# Extract version from pyproject.toml (single source of truth)
VERSION=$(grep -E '^version = ' "$PROJECT_ROOT/pyproject.toml" | sed 's/version = "\(.*\)"/\1/')

if [ -z "$VERSION" ]; then
    echo "Error: Could not extract version from pyproject.toml"
    exit 1
fi

echo "================================================"
echo "Building tuxgrade DEB version: $VERSION"
echo "================================================"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR/deb"

echo "🔨 Building DEB package..."
echo "----------------------------------------"

# Pull Ubuntu image
docker pull docker.io/library/ubuntu:24.04

# Build DEB in Ubuntu container
docker run --rm \
    -v "$PROJECT_ROOT:/workspace:ro" \
    -v "$OUTPUT_DIR/deb:/output:rw" \
    docker.io/library/ubuntu:24.04 \
    bash -c "
        set -e
        
        # Prevent interactive prompts
        export DEBIAN_FRONTEND=noninteractive
        
        # Install build dependencies
        apt-get update
        apt-get install -y \
            debhelper \
            dh-python \
            python3-all \
            python3-setuptools \
            python3-pip \
            python3-build \
            python3-distro \
            pybuild-plugin-pyproject \
            dpkg-dev \
            fakeroot
        
        # Create build directory
        mkdir -p /build
        
        # Copy project to build directory (need write access for build)
        cp -r /workspace/* /build/
        
        # Change to build directory
        cd /build
        
        # Build the package
        dpkg-buildpackage -us -uc -b
        
        # Copy built packages to output (only .deb files)
        cp ../*.deb /output/
        
        echo \"DEB package built successfully!\"
    "

echo ""
echo "✅ DEB build complete!"
echo "   Output: $OUTPUT_DIR/deb/"
ls -lh "$OUTPUT_DIR/deb/"
echo ""
echo "DEB packages:"
ls -1 "$OUTPUT_DIR/deb/"*.deb 2>/dev/null || echo "  No DEB packages found"
echo ""
