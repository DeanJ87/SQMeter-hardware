# Schematic

## Source

The KiCad schematic source lives in `hardware/kicad/SQMeter-Hardware.kicad_sch`. This is the authoritative design file — all other schematic assets are derived from it.

## Generated exports

| File | Purpose |
|------|---------|
| `hardware/exports/schematic.svg` | Embeddable in docs pages |
| `hardware/exports/schematic.pdf` | Downloadable from hardware releases |
| `hardware/images/schematic-preview.png` | Preview image for README/docs cards |

Generated exports **must not be edited by hand**. Regenerate them from the KiCad source:

```bash
./scripts/export-kicad.sh
```

## Main docs integration

The main SQMeter docs site can embed `schematic.svg` directly or link to the release asset PDF. Preferred approach:

- Embed SVG inline for the hardware schematic page
- Provide a direct download link to `schematic.pdf` from the latest hardware release
- Link to this repo for the KiCad source

## Viewing the schematic

Open `hardware/kicad/SQMeter-Hardware.kicad_sch` in KiCad 8. Do not rely on the exported SVG for design review — always work from source.
