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

## Hardware revision

`HW_REV` in `design.py` is the board's hardware revision (Rev A, B, ...). It is independent of any
firmware version: bump it whenever the copper changes. It goes on the silkscreen, in the KiCad title
blocks and gerber metadata, and in the fab file names (`../manufacturing/<project>-rev<X>/`).

## Silkscreen branding

The SQMeter lockup on the silkscreen comes from `brand_silk.json`: the brand kit's
`sqmeter-mark-silkscreen.svg` plus "SQMeter" in Inter SemiBold, converted to plain polygons by
`brand_silk.py` so nobody needs the font installed. Regenerate it only if the brand changes (see the
script's docstring). Functional labels (pin names, connector titles) use KiCad's stroke font, which stays
legible at 1 mm on a fab's silkscreen.

## JLCPCB files

```bash
./export_jlc.sh zero        # or module / devkit
```

writes `../manufacturing/<project>-rev<X>/`: the gerber + drill zip (upload as-is), `-bom.csv` and
`-cpl.csv` (for PCB assembly).
