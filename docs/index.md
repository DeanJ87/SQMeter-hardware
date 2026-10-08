# SQMeter Hardware

This repository is the canonical source of truth for SQMeter electronics design and manufacturing files.

The main SQMeter documentation site at <https://sqmeter.dev/> covers firmware, the web interface, and sensor integration. Hardware-specific assets (schematic, PCB renders, BOM, gerbers, iBOM) are generated from this repo and linked from the main docs.

## What lives here

| Asset | Source | Generated output |
|-------|--------|-----------------|
| Schematic | `hardware/kicad/*.kicad_sch` | `hardware/exports/schematic.svg`, `schematic.pdf` |
| PCB layout | `hardware/kicad/*.kicad_pcb` | `hardware/exports/pcb-top.png`, `pcb-bottom.png` |
| Gerbers + drill | `hardware/kicad/*.kicad_pcb` | `hardware/manufacturing/gerbers/`, `drill/` |
| BOM | KiCad schematic | `hardware/bom/bom.csv`, `bom.md` |
| InteractiveHtmlBom | KiCad PCB | `hardware/ibom/ibom.html` |

## Hardware releases

Each hardware release (tagged `vX.Y.Z`) packages the above outputs into a downloadable ZIP. See [Releases](../../releases).

## What does not live here

- Firmware source → [SQMeter repo](https://github.com/DeanJ87/SQMeter)
- Web UI → [SQMeter repo](https://github.com/DeanJ87/SQMeter)
- 3D printed enclosure files → Printables (TODO: add link)
