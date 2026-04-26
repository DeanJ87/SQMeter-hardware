# Contributing

Contributions to the SQMeter hardware design are welcome.

## What this repo contains

KiCad schematic and PCB source, generated exports, manufacturing files, BOM, and assembly support assets. Firmware and web UI belong in the [main SQMeter repo](https://github.com/DeanJ87/SQMeter).

## Making changes

1. Fork the repo and create a branch for your change.
2. Open your KiCad project from `hardware/kicad/`.
3. Make schematic or PCB changes in KiCad.
4. Run `./scripts/export-kicad.sh` to regenerate exports locally before submitting.
5. Open a pull request with a clear description of what changed and why.

## Generated files

Files under `hardware/exports/`, `hardware/manufacturing/`, `hardware/bom/`, and `hardware/ibom/` are generated artifacts. Do not edit them by hand — regenerate them from the KiCad source using the scripts in `scripts/`.

## Schematic and PCB review

When reviewing hardware PRs, check:
- Component values and footprints are correct
- Net names are consistent between schematic and PCB
- Design rule checks (DRC) pass in KiCad
- Generated exports in the PR reflect the actual changes

## Reporting issues

Open an issue in this repo for hardware-specific problems (schematic errors, footprint issues, DRC violations, BOM discrepancies). For firmware or software bugs, use the [main SQMeter repo](https://github.com/DeanJ87/SQMeter/issues).
