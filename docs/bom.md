# Bill of Materials

## Source of truth

The BOM is generated from the KiCad schematic. Do not maintain a separate BOM in a spreadsheet or Google Docs — this leads to drift between the schematic and the BOM.

To regenerate:

```bash
./scripts/generate-bom.sh
```

## Output files

| File | Purpose |
|------|---------|
| `hardware/bom/bom.csv` | Machine-readable, included in every hardware release |
| `hardware/bom/bom.md` | Human-readable Markdown table (generated from CSV) |
| `hardware/bom/bom.html` | Human-readable HTML table (generated from CSV, optional) |

## Release asset

`bom.csv` is included in every hardware release ZIP. Distributors and assembly houses can consume the CSV directly.

## Sourcing notes

TODO: add preferred suppliers and part numbers once the component selection is finalised.

## KiCad BOM export

TODO: decide on BOM export method:
- KiCad 8 built-in BOM export via `kicad-cli sch export bom`
- [KiBOM](https://github.com/SchrodingersGat/KiBoM) plugin
- [InteractiveHtmlBom](https://github.com/openscopeproject/InteractiveHtmlBom) BOM export

Prefer `kicad-cli` where possible to avoid external dependencies in CI.
