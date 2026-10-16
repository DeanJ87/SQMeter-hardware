#!/bin/bash
# Export JLCPCB fab files for one variant: gerbers+drill zip, BOM, CPL -> ../manufacturing/<name>/
set -euo pipefail
cd "$(dirname "$0")"
export SQM_VARIANT=${1:-${SQM_VARIANT:-module}}
NAME=$(python3 -c 'import design; print(design.NAME)')
REV=$(python3 -c 'import design; print(design.HW_REV)')
K=${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}
KP=${KICAD_PYTHON:-/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3}
PCB=../kicad/$NAME.kicad_pcb
OUT=../manufacturing/$NAME-rev$REV
q() { grep -vE 'Fontconfig|assert|Debug:|Unable to revert' || true; }
rm -rf "$OUT" && mkdir -p "$OUT/gerbers"
$K pcb export gerbers --use-drill-file-origin --subtract-soldermask --no-x2 \
  --layers F.Cu,B.Cu,F.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts -o "$OUT/gerbers/" "$PCB" 2>&1 | q | tail -1
$K pcb export drill --drill-origin plot --excellon-separate-th \
  -o "$OUT/gerbers/" "$PCB" 2>&1 | q | tail -1
(cd "$OUT/gerbers" && zip -q -r "../$NAME-rev$REV-gerbers.zip" .) && rm -rf "$OUT/gerbers"
$KP jlc_bom_cpl.py "$PCB" "$OUT" 2>&1 | q
ls "$OUT"
