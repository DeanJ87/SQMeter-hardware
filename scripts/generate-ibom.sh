#!/usr/bin/env bash
set -euo pipefail

# Generate InteractiveHtmlBom from KiCad PCB source.
# Requires InteractiveHtmlBom: https://github.com/openscopeproject/InteractiveHtmlBom

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KICAD_DIR="$REPO_ROOT/hardware/kicad"
IBOM_DIR="$REPO_ROOT/hardware/ibom"

PCB_FILE="$KICAD_DIR/SQMeter-Hardware.kicad_pcb"

# ── Preflight ────────────────────────────────────────────────────────────────

if [[ ! -f "$PCB_FILE" ]]; then
  echo "ERROR: PCB layout not found: $PCB_FILE"
  echo "       Commit the KiCad project files before running this script."
  exit 1
fi

# TODO: InteractiveHtmlBom can be run as a KiCad plugin or as a standalone CLI tool.
# For CI use, the standalone CLI (generate_interactive_bom.py) is preferred.
# Install options:
#   pip install interactivehtmlbom          # if available via pip
#   or clone https://github.com/openscopeproject/InteractiveHtmlBom and use the script directly

IBOM_CMD=""
if command -v generate_interactive_bom.py &>/dev/null; then
  IBOM_CMD="generate_interactive_bom.py"
elif command -v python3 &>/dev/null && python3 -c "import InteractiveHtmlBom" &>/dev/null 2>&1; then
  IBOM_CMD="python3 -m InteractiveHtmlBom.generate_interactive_bom"
else
  echo "ERROR: InteractiveHtmlBom not found."
  echo "       Install from https://github.com/openscopeproject/InteractiveHtmlBom"
  echo "       or via pip: pip install interactivehtmlbom"
  exit 1
fi

mkdir -p "$IBOM_DIR"

# ── Generate iBOM ─────────────────────────────────────────────────────────────

echo "Generating InteractiveHtmlBom..."
# TODO: review flags — output path, dark mode, layer visibility, etc.
$IBOM_CMD \
  --dest-dir "$IBOM_DIR" \
  --output-file-name ibom.html \
  --no-browser \
  "$PCB_FILE"

echo "iBOM written to: $IBOM_DIR/ibom.html"
