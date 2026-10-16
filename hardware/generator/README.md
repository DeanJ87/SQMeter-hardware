# Board generator

The main board is described in `design.py` (parts, footprints, nets) and `genpcb.py` (placement).
`build.sh` regenerates the KiCad schematic and PCB in `../kicad/` from those, autoroutes with
Freerouting, adds GND pours and stitching vias, then runs ERC/DRC.

```bash
FREEROUTING_JAR=~/tools/freerouting-2.4.1.jar JAVA=/opt/homebrew/opt/openjdk/bin/java ./build.sh
```

Requires KiCad 10 (uses its bundled Python for `pcbnew`) and Java 21+.

Once the layout is hand-tuned in KiCad, edit the KiCad files directly; re-running `build.sh`
overwrites them.
