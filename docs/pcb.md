# PCB Layout

## Source

The KiCad PCB layout lives in `hardware/kicad/SQMeter-Hardware.kicad_pcb`. All manufacturing outputs and preview images are derived from this file.

## Generated exports

| File | Purpose |
|------|---------|
| `hardware/exports/pcb-top.png` | Top copper layer render |
| `hardware/exports/pcb-bottom.png` | Bottom copper layer render |
| `hardware/exports/pcb-3d.png` | 3D board render |
| `hardware/manufacturing/gerbers/` | Gerber files for board fabrication |
| `hardware/manufacturing/drill/` | Drill files (Excellon) |
| `hardware/manufacturing/pick-and-place/` | Pick-and-place CSV for SMT assembly |
| `hardware/ibom/ibom.html` | Interactive BOM for manual assembly |

Regenerate from source:

```bash
./scripts/export-kicad.sh    # PCB renders + gerbers + drill
./scripts/generate-ibom.sh   # InteractiveHtmlBom
```

## Gerbers

Gerbers and drill files are published as a ZIP in each hardware release. Submit the ZIP directly to your board house. No further modification should be needed.

## InteractiveHtmlBom

`hardware/ibom/ibom.html` is a self-contained HTML file that shows component placement overlaid on the PCB. Open it in any browser — no server required. Useful for hand assembly and inspection.

## Board specifications

TODO: fill in once design is finalised.

| Parameter | Value |
|-----------|-------|
| Layers | TBD |
| Dimensions | TBD |
| PCB thickness | TBD |
| Min track width | TBD |
| Min via diameter | TBD |
| Copper weight | TBD |
| Surface finish | TBD |
| Soldermask colour | TBD |
