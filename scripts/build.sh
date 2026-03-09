#!/usr/bin/env bash
#
# Build MagicSpell.app using py2app.
#
# Usage:
#   ./scripts/build.sh          # build the .app bundle
#   ./scripts/build.sh clean    # remove build artifacts
#
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$ROOT/.venv"
DIST="$ROOT/dist"

# ------------------------------------------------------------------
# Clean mode
# ------------------------------------------------------------------
if [[ "${1:-}" == "clean" ]]; then
    echo "Cleaning build artifacts..."
    rm -rf "$ROOT/build" "$DIST" "$ROOT/.eggs"
    echo "Done."
    exit 0
fi

# ------------------------------------------------------------------
# Create virtual environment if needed
# ------------------------------------------------------------------
if [[ ! -d "$VENV" ]]; then
    echo "Creating virtual environment at $VENV ..."
    python3 -m venv "$VENV"
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"

# ------------------------------------------------------------------
# Install dependencies
# ------------------------------------------------------------------
echo "Installing dependencies..."
pip install --quiet --upgrade pip setuptools wheel
pip install --quiet -e ".[dev]"
pip install --quiet py2app

# ------------------------------------------------------------------
# Build the .app bundle
# ------------------------------------------------------------------
echo "Building MagicSpell.app..."
cd "$ROOT"
python setup_mac.py py2app

echo ""
echo "============================================="
echo "  Build complete!"
echo "  App bundle: $DIST/MagicSpell.app"
echo "============================================="
echo ""
echo "To install:"
echo "  cp -r $DIST/MagicSpell.app /Applications/"
echo ""
echo "To run:"
echo "  open /Applications/MagicSpell.app"
echo ""
echo "Note: On first launch, macOS will prompt for"
echo "Accessibility permissions. Grant access in:"
echo "  System Settings > Privacy & Security > Accessibility"
echo ""
