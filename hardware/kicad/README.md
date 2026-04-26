# KiCad Project

This directory contains the KiCad 8 project for SQMeter Hardware.

## Files

| File | Description |
|------|-------------|
| `SQMeter-Hardware.kicad_pro` | KiCad project file |
| `SQMeter-Hardware.kicad_sch` | Schematic source |
| `SQMeter-Hardware.kicad_pcb` | PCB layout source |

These files are not yet committed — the KiCad design is in progress.

## Opening the project

Open `SQMeter-Hardware.kicad_pro` in KiCad 8. Do not open `.kicad_sch` or `.kicad_pcb` directly — always open via the project file to ensure footprint and symbol library associations are resolved correctly.

## Generating exports

From the repo root:

```bash
./scripts/export-kicad.sh
```

This requires `kicad-cli` on your PATH (included with KiCad 8).
