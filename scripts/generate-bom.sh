#!/usr/bin/env bash
set -euo pipefail

# Generate BOM from KiCad schematic source.
# Requires kicad-cli (bundled with KiCad 8).

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KICAD_DIR="$REPO_ROOT/hardware/kicad"
BOM_DIR="$REPO_ROOT/hardware/bom"

SCH_FILE="$KICAD_DIR/SQMeter-Hardware.kicad_sch"

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

mkdir -p "$BOM_DIR"

# ── BOM export ───────────────────────────────────────────────────────────────

echo "Exporting BOM CSV..."
# TODO: kicad-cli sch export bom is available in KiCad 8.
# Review the output columns — default may need customisation for your BOM format.
# Options to consider:
#   --fields "Reference,Value,Footprint,Quantity,MPN,Supplier,SupplierPN"
#   --group-by "Value,Footprint"
kicad-cli sch export bom \
  --output "$BOM_DIR/bom.csv" \
  "$SCH_FILE"

echo "BOM written to: $BOM_DIR/bom.csv"

# TODO: optionally convert bom.csv to bom.md using a small Python/awk script.
# Example (requires python3 + csv module):
#
# python3 - <<'EOF'
# import csv, sys
# with open("hardware/bom/bom.csv") as f:
#     reader = csv.DictReader(f)
#     rows = list(reader)
# headers = rows[0].keys() if rows else []
# print("| " + " | ".join(headers) + " |")
# print("| " + " | ".join(["---"] * len(headers)) + " |")
# for row in rows:
#     print("| " + " | ".join(row.values()) + " |")
# EOF > hardware/bom/bom.md

echo "Done."
