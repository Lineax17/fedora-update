#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$1" in
    -l|--log|--verbose)
        exec "$SCRIPT_DIR/fedora-update-verbose.sh"
        ;;
    "")
        exec "$SCRIPT_DIR/fedora-update-silent.sh"
        ;;
    *)
        echo "Usage: fedora-update [-l]"
        echo "  -l    Show live output during update"
        exit 1
        ;;
esac