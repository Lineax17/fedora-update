#!/bin/bash

set -e  # Exit on error

# Determine script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_DIR="${OUTPUT_DIR:-$SCRIPT_DIR/output}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            echo "Usage: $0"
            echo ""
            echo "Build tuxgrade RPM package using Fedora container."
            echo ""
            echo "Options:"
            echo "  -h, --help    Show this help message"
            echo ""
            echo "Environment variables:"
            echo "  OUTPUT_DIR    Override output directory (default: $SCRIPT_DIR/output)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check for Podman
if ! command -v podman >/dev/null 2>&1; then
    echo "Error: podman is not installed."
    echo "Install it with: sudo dnf install podman  (Fedora/RHEL)"
    echo "             or: sudo apt install podman  (Debian/Ubuntu)"
    exit 1
fi

# Extract version from pyproject.toml (single source of truth)
VERSION=$(grep -E '^version = ' "$PROJECT_ROOT/pyproject.toml" | sed 's/version = "\(.*\)"/\1/')

if [ -z "$VERSION" ]; then
    echo "Error: Could not extract version from pyproject.toml"
    exit 1
fi

echo "================================================"
echo "Building tuxgrade RPM version: $VERSION"
echo "================================================"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR/rpm"

echo "🔨 Building RPM package..."
echo "----------------------------------------"

# Pull Fedora image
podman pull docker.io/library/fedora:latest

# Build RPM in Fedora container
podman run --rm \
    -v "$PROJECT_ROOT:/workspace:ro,z" \
    -v "$OUTPUT_DIR/rpm:/output:rw,z" \
    -w /workspace \
    docker.io/library/fedora:latest \
    bash -c "
        set -e
        
        # Install build dependencies
        dnf -y install rpm-build rpmdevtools python3-devel python3-setuptools pyproject-rpm-macros
        
        # Setup rpmbuild directories
        rpmdev-setuptree
        
        # Copy spec file
        cp /workspace/build/tuxgrade.spec ~/rpmbuild/SPECS/
        
        # Create source tarball
        mkdir -p ~/tuxgrade-${VERSION}
        cp -r /workspace/src ~/tuxgrade-${VERSION}/
        cp /workspace/pyproject.toml ~/tuxgrade-${VERSION}/
        cp /workspace/LICENSE ~/tuxgrade-${VERSION}/
        cp /workspace/README.md ~/tuxgrade-${VERSION}/
        tar czf ~/rpmbuild/SOURCES/tuxgrade-${VERSION}.tar.gz -C ~ tuxgrade-${VERSION}
        
        # Build RPM
        rpmbuild -ba ~/rpmbuild/SPECS/tuxgrade.spec
        
        # Copy built packages to output (binary RPM only, no source RPM)
        cp ~/rpmbuild/RPMS/noarch/*.rpm /output/
        
        echo \"RPM packages built successfully!\"
    "

echo ""
echo "✅ RPM build complete!"
echo "   Output: $OUTPUT_DIR/rpm/"
ls -lh "$OUTPUT_DIR/rpm/"
echo ""
echo "RPM packages:"
ls -1 "$OUTPUT_DIR/rpm/"*.rpm 2>/dev/null || echo "  No RPM packages found"
echo ""
