#!/bin/bash
# Rebuild the board from design.py:
#   schematic -> ERC -> netlist check -> PCB placement -> net classes -> Freerouting -> pours/stitching -> DRC
# Needs KiCad 10 and Java; set FREEROUTING_JAR to a freerouting-<ver>.jar.
set -euo pipefail
cd "$(dirname "$0")"
OUT=${OUT:-../kicad}
K=${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}
KP=${KICAD_PYTHON:-/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3}
JAVA=${JAVA:-java}
: "${FREEROUTING_JAR:?set FREEROUTING_JAR to the Freerouting jar}"
export SQM_VARIANT=${1:-${SQM_VARIANT:-module}}
NAME=$(python3 -c 'import design; print(design.NAME)')
echo "== variant $SQM_VARIANT -> $NAME"
TMP=$(mktemp -d)
q() { grep -vE 'Fontconfig|assert|Debug:|IMK|Unable to revert' || true; }

python3 gensch.py "$OUT/$NAME.kicad_sch"
$K sch erc -o "$TMP/erc.rpt" "$OUT/$NAME.kicad_sch" 2>&1 | q | grep -i violation
$K sch export netlist --format kicadsexpr -o "$TMP/net.net" "$OUT/$NAME.kicad_sch" 2>&1 | q >/dev/null
python3 checknet.py "$TMP/net.net"
for attempt in $(seq 1 "${ATTEMPTS:-5}"); do
  echo "== route attempt $attempt"
  $KP genpcb.py "$OUT/$NAME.kicad_pcb" "$TMP/net.net" 2>&1 | q
  python3 netclasses.py "$OUT/$NAME.kicad_pro"
  $KP route.py "$OUT/$NAME.kicad_pcb" export "$TMP/board.dsn" 2>&1 | q
  $JAVA -Djava.awt.headless=true -jar "$FREEROUTING_JAR" -de "$TMP/board.dsn" -do "$TMP/board.ses" -mp "${PASSES:-60}" --gui.enabled=false 2>&1 \
    | grep -E 'could not be routed|Net |    - ' || true
  $KP route.py "$OUT/$NAME.kicad_pcb" import "$TMP/board.ses" 2>&1 | q
  $K pcb drc --severity-all -o "$TMP/drc.rpt" "$OUT/$NAME.kicad_pcb" 2>&1 | q | grep Found
  { grep -E '^\[' "$TMP/drc.rpt" || true; } | sed 's/:.*//' | sort | uniq -c
  if ! grep -qE '^\[(unconnected_items|clearance|shorting_items|tracks_crossing|track_dangling|via_dangling)' "$TMP/drc.rpt"; then
    echo "routed cleanly"; break
  fi
done
echo "reports in $TMP"
