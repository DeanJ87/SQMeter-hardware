# SQMeter Hardware

Hardware source files for the [SQMeter](https://github.com/DeanJ87/SQMeter) open-source sky quality meter.

The main firmware, web UI, and documentation live in the **[SQMeter repo](https://github.com/DeanJ87/SQMeter)**. This repo is the canonical source of truth for the electronics design and manufacturing files.

---

## What's here

| Path | Contents |
|------|----------|
| `hardware/kicad/` | KiCad schematic and PCB source |
| `hardware/exports/` | Generated schematic SVG/PDF and PCB renders |
| `hardware/manufacturing/` | Gerbers, drill files, pick-and-place |
| `hardware/bom/` | Bill of materials (CSV and human-readable) |
| `hardware/ibom/` | InteractiveHtmlBom for assembly |
| `hardware/images/` | Board renders and preview images |
| `scripts/` | Export, BOM, iBOM, and release packaging scripts |

---

## Quick links

| | |
|--|--|
| Main docs site | <https://deanj87.github.io/SQMeter/> |
| Main repo | <https://github.com/DeanJ87/SQMeter> |
| Hardware releases | [Releases](../../releases) |
| Schematic PDF | TODO: link once first release is published |
| Schematic SVG | TODO: link once first release is published |
| BOM CSV | TODO: link once first release is published |
| InteractiveHtmlBom | TODO: link once first release is published |
| Gerbers ZIP | TODO: link once first release is published |

---

## Versioning

Hardware versions follow `vMAJOR.MINOR.PATCH` tied to physical board revisions.

- `v0.x.x` — prototype / bring-up
- `v1.0.0` — first stable public release

Hardware versions are independent of firmware versions. A firmware update does not require a new board revision.

---

## Generating exports locally

Requires KiCad 8 with `kicad-cli` on your PATH.

```bash
./scripts/export-kicad.sh      # schematic SVG/PDF + PCB renders + gerbers
./scripts/generate-bom.sh      # hardware/bom/bom.csv
./scripts/generate-ibom.sh     # hardware/ibom/ibom.html
./scripts/package-release.sh   # dist/SQMeter-Hardware-release.zip
```

---

## 3D printed enclosure

Enclosure files are hosted on Printables (TODO: add link when available). This repo focuses on PCB electronics and manufacturing assets. Mounting dimensions and interface notes may be added under `docs/assembly.md`.

---

## License

[MIT](LICENSE)
