# Labels and stickers

Print-ready SQMeter labels for an enclosure and a round sticker, made from the brand kit in the firmware repository (`brand/`, rendered with `tools/brand/render.mjs`).

| File | Size | Use |
|---|---|---|
| `sqmeter-label-enclosure-70x24mm.pdf` | 70 × 24 mm | Full-colour enclosure label, with S/N and FW fields to fill in and an arrow marking the zenith side |
| `sqmeter-label-enclosure-mono.pdf` | 70 × 24 mm | One-colour version, for vinyl cutters, label printers or engraving |
| `sqmeter-sticker-round-60mm.pdf` | 60 mm round | Sticker |
| `*-600dpi.png` | Same sizes at 600 dpi | For printers that want images |
| `*.svg` | — | Sources (text in Inter and JetBrains Mono; use the PDFs if you don't have those fonts) |
| `sqmeter-mark-silkscreen.svg` | 6 mm and up | One-colour mark for the PCB silkscreen |
| `sqmeter-mark-emboss.svg` | 20 mm and up | One-colour mark for embossing, debossing or engraving a case |

## Printing

- Print the PDFs at **100% scale** ("actual size"), not "fit to page". Each PDF is one page at the label's size; Chromium rounds the page to the nearest pixel, so it is up to 0.4 mm larger, which falls within the bleed.
- For outdoor enclosures use weatherproof vinyl or laminate the label: the full-colour label has a dark background that fades in direct sun.
- The arrow on the enclosure label marks the zenith: fit the label so it points up, the way the sensors face.

To regenerate these files, run `node tools/brand/render.mjs --only sticker` in the firmware repository and copy `brand/render/print/` here.
