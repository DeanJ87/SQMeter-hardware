# Manufacturing

Generated fabrication outputs. Do not edit these files by hand.

Regenerate from source:

```bash
./scripts/export-kicad.sh
```

## Subdirectories

| Directory | Contents |
|-----------|---------|
| `gerbers/` | Gerber files (one per layer) |
| `drill/` | Excellon drill files |
| `pick-and-place/` | Pick-and-place CSV for SMT assembly |

These files are not yet present — they will be generated once the KiCad PCB layout is committed.

See `docs/manufacturing.md` for board specifications and board house notes.
