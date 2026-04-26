# Exports

Generated schematic and PCB preview assets. Do not edit these files by hand.

Regenerate from source:

```bash
./scripts/export-kicad.sh
```

## Expected files

| File | Description |
|------|-------------|
| `schematic.svg` | Schematic — embeddable in docs |
| `schematic.pdf` | Schematic — downloadable from releases |
| `pcb-top.png` | PCB top copper render |
| `pcb-bottom.png` | PCB bottom copper render |
| `pcb-3d.png` | 3D board render |

These files are not yet present — they will be generated once the KiCad project files are committed.
