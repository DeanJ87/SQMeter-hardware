#!/usr/bin/env bash
set -euo pipefail

# Export schematic SVG/PDF, PCB renders, gerbers, and drill files from KiCad source.
# Requires kicad-cli (bundled with KiCad 8).

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KICAD_DIR="$REPO_ROOT/hardware/kicad"
EXPORTS_DIR="$REPO_ROOT/hardware/exports"
MFG_DIR="$REPO_ROOT/hardware/manufacturing"

SCH_FILE="$KICAD_DIR/SQMeter-Hardware.kicad_sch"
PCB_FILE="$KICAD_DIR/SQMeter-Hardware.kicad_pcb"

# ── Preflight ────────────────────────────────────────────────────────────────

if ! command -v kicad-cli &>/dev/null; then
  echo "ERROR: kicad-cli not found. Install KiCad 8 and ensure kicad-cli is on your PATH."
  exit 1
fi

if [[ ! -f "$SCH_FILE" ]]; then
  echo "ERROR: Schematic not found: $SCH_FILE"
  echo "       Commit the KiCad project files before running this script."
  exit 1
fi

if [[ ! -f "$PCB_FILE" ]]; then
  echo "ERROR: PCB layout not found: $PCB_FILE"
  echo "       Commit the KiCad project files before running this script."
  exit 1
fi

# ── Output directories ───────────────────────────────────────────────────────

mkdir -p "$EXPORTS_DIR"
mkdir -p "$MFG_DIR/gerbers"
mkdir -p "$MFG_DIR/drill"

# ── Schematic export ─────────────────────────────────────────────────────────

echo "Exporting schematic SVG..."
# TODO: verify exact flags for your KiCad version
kicad-cli sch export svg \
  --output "$EXPORTS_DIR/schematic.svg" \
  "$SCH_FILE"

echo "Exporting schematic PDF..."
kicad-cli sch export pdf \
  --output "$EXPORTS_DIR/schematic.pdf" \
  "$SCH_FILE"

# ── PCB renders ──────────────────────────────────────────────────────────────

echo "Exporting PCB renders..."
# TODO: kicad-cli pcb render is available in KiCad 8.0+
# Adjust --side and --output as needed.
kicad-cli pcb render \
  --output "$EXPORTS_DIR/pcb-top.png" \
  --side top \
  "$PCB_FILE" || echo "WARN: PCB render (top) failed — kicad-cli render may not be available in this version."

kicad-cli pcb render \
  --output "$EXPORTS_DIR/pcb-bottom.png" \
  --side bottom \
  "$PCB_FILE" || echo "WARN: PCB render (bottom) failed — kicad-cli render may not be available in this version."

# TODO: 3D render requires KiCad with OpenGL/headless support — may need a different approach.
# kicad-cli pcb render --output "$EXPORTS_DIR/pcb-3d.png" --perspective "$PCB_FILE"

# ── Gerbers ──────────────────────────────────────────────────────────────────

echo "Exporting gerbers..."
# TODO: review layer list for your stackup before production.
kicad-cli pcb export gerbers \
  --output "$MFG_DIR/gerbers/" \
  "$PCB_FILE"

# ── Drill files ──────────────────────────────────────────────────────────────

echo "Exporting drill files..."
kicad-cli pcb export drill \
  --output "$MFG_DIR/drill/" \
  --format excellon \
  "$PCB_FILE"

# ── Pick and place ───────────────────────────────────────────────────────────

echo "Exporting pick-and-place..."
mkdir -p "$MFG_DIR/pick-and-place"
kicad-cli pcb export pos \
  --output "$MFG_DIR/pick-and-place/SQMeter-Hardware-pos.csv" \
  --format csv \
  --units mm \
  "$PCB_FILE"

echo ""
echo "Done. Outputs written to:"
echo "  $EXPORTS_DIR"
echo "  $MFG_DIR"
