#!/bin/bash

set -e  # Exit on error

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Parse command line arguments
BUILD_RPM=false
BUILD_DEB=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --rpm)
            BUILD_RPM=true
            shift
            ;;
        --deb)
            BUILD_DEB=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--rpm] [--deb]"
            echo ""
            echo "Build tuxgrade packages by calling individual build scripts."
            echo ""
            echo "Options:"
            echo "  --rpm    Build RPM package (calls build-rpm.sh)"
            echo "  --deb    Build DEB package (calls build-deb.sh)"
            echo "  -h       Show this help message"
            echo ""
            echo "If no options are specified, both packages will be built."
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# If neither option specified, build both
if [ "$BUILD_RPM" = false ] && [ "$BUILD_DEB" = false ]; then
    BUILD_RPM=true
    BUILD_DEB=true
fi

echo "================================================"
echo "Building tuxgrade packages"
echo "================================================"
echo ""

# Build RPM package
if [ "$BUILD_RPM" = true ]; then
    "$SCRIPT_DIR/build-rpm.sh"
fi

# Build DEB package
if [ "$BUILD_DEB" = true ]; then
    "$SCRIPT_DIR/build-deb.sh"
fi

echo "================================================"
echo "✅ All builds completed successfully!"
echo "================================================"
echo ""
echo "Output directory: $PROJECT_ROOT/output"
echo ""
if [ "$BUILD_RPM" = true ]; then
    echo "RPM packages:"
    ls -1 "$PROJECT_ROOT/output/rpm/"*.rpm 2>/dev/null || echo "  No RPM packages found"
    echo ""
fi
if [ "$BUILD_DEB" = true ]; then
    echo "DEB packages:"
    ls -1 "$PROJECT_ROOT/output/deb/"*.deb 2>/dev/null || echo "  No DEB packages found"
    echo ""
fi
