#!/usr/bin/env bash
set -euo pipefail

# Package generated hardware outputs into a release ZIP.
# Run after export-kicad.sh, generate-bom.sh, and generate-ibom.sh.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPORTS_DIR="$REPO_ROOT/hardware/exports"
MFG_DIR="$REPO_ROOT/hardware/manufacturing"
BOM_DIR="$REPO_ROOT/hardware/bom"
IBOM_DIR="$REPO_ROOT/hardware/ibom"

VERSION="${RELEASE_VERSION:-dev}"
RELEASE_NAME="SQMeter-Hardware-${VERSION}"
DIST_DIR="$REPO_ROOT/dist/$RELEASE_NAME"
GERBERS_ZIP="$DIST_DIR/gerbers.zip"

# ── Clean and create dist dir ────────────────────────────────────────────────

echo "Preparing release: $RELEASE_NAME"
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

# ── Critical files (fail if missing) ─────────────────────────────────────────

copy_required() {
  local src="$1" dst="$2"
  if [[ ! -f "$src" ]]; then
    echo "ERROR: Required file not found: $src"
    echo "       Run the export scripts before packaging."
    exit 1
  fi
  cp "$src" "$dst"
  echo "  + $(basename "$src")"
}

copy_optional() {
  local src="$1" dst="$2"
  if [[ -f "$src" ]]; then
    cp "$src" "$dst"
    echo "  + $(basename "$src")"
  else
    echo "  ~ MISSING (optional): $(basename "$src")"
  fi
}

echo ""
echo "Copying schematic..."
copy_required "$EXPORTS_DIR/schematic.pdf" "$DIST_DIR/schematic.pdf"
copy_required "$EXPORTS_DIR/schematic.svg" "$DIST_DIR/schematic.svg"

echo ""
echo "Copying BOM..."
copy_required "$BOM_DIR/bom.csv" "$DIST_DIR/bom.csv"
copy_optional "$BOM_DIR/bom.md" "$DIST_DIR/bom.md"
copy_optional "$BOM_DIR/bom.html" "$DIST_DIR/bom.html"

echo ""
echo "Packaging gerbers..."
if [[ -d "$MFG_DIR/gerbers" ]] && [[ -n "$(ls -A "$MFG_DIR/gerbers" 2>/dev/null)" ]]; then
  zip -j "$GERBERS_ZIP" "$MFG_DIR/gerbers/"* "$MFG_DIR/drill/"* 2>/dev/null || \
  zip -j "$GERBERS_ZIP" "$MFG_DIR/gerbers/"*
  echo "  + gerbers.zip"
else
  echo "ERROR: Gerbers directory is empty or missing: $MFG_DIR/gerbers"
  exit 1
fi

echo ""
echo "Copying optional assets..."
copy_optional "$IBOM_DIR/ibom.html" "$DIST_DIR/ibom.html"
copy_optional "$EXPORTS_DIR/pcb-top.png" "$DIST_DIR/pcb-top.png"
copy_optional "$EXPORTS_DIR/pcb-bottom.png" "$DIST_DIR/pcb-bottom.png"
copy_optional "$EXPORTS_DIR/pcb-3d.png" "$DIST_DIR/pcb-3d.png"

# ── ZIP the release ───────────────────────────────────────────────────────────

RELEASE_ZIP="$REPO_ROOT/dist/${RELEASE_NAME}.zip"
echo ""
echo "Creating release ZIP..."
(cd "$REPO_ROOT/dist" && zip -r "${RELEASE_NAME}.zip" "$RELEASE_NAME/")
echo ""
echo "Release package: $RELEASE_ZIP"
echo "Contents:"
unzip -l "$RELEASE_ZIP" | tail -n +4 | head -n -2
