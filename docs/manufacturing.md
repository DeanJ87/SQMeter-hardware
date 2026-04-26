# Manufacturing

## Overview

Manufacturing outputs are generated artifacts. The KiCad PCB source in `hardware/kicad/` is the canonical file. Gerbers, drill files, and pick-and-place are produced by `scripts/export-kicad.sh` and packaged by `scripts/package-release.sh`.

## Output files

| Path | Contents |
|------|---------|
| `hardware/manufacturing/gerbers/` | Gerber files per copper layer, silkscreen, mask, edge cuts |
| `hardware/manufacturing/drill/` | Excellon drill files |
| `hardware/manufacturing/pick-and-place/` | Pick-and-place CSV for SMT assembly |

## Board specifications

TODO: fill in once finalised.

| Parameter | Value |
|-----------|-------|
| Board outline | TBD |
| Layer count | TBD |
| PCB thickness | TBD mm |
| Copper weight | TBD oz |
| Min trace/space | TBD / TBD mm |
| Min via drill | TBD mm |
| Surface finish | TBD (HASL / ENIG) |
| Soldermask colour | TBD |
| Silkscreen | TBD |
| Controlled impedance | TBD |

## Panelisation

TODO: panelisation strategy if needed (V-score, mouse bites, or single board).

## Board house notes

TODO: add notes for the target board house once chosen (JLCPCB, PCBWay, OSHPark, etc.).

Typical JLCPCB notes:
- Upload `hardware/manufacturing/gerbers/` as a ZIP
- Upload `hardware/manufacturing/drill/` drill files alongside
- For SMT assembly: provide pick-and-place CSV and BOM CSV

## Generating manufacturing outputs

```bash
./scripts/export-kicad.sh
```

Outputs are written to `hardware/manufacturing/`. Check DRC and ERC in KiCad before generating for production.
