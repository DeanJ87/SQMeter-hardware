"""jlc_bom_cpl.py <board.kicad_pcb> <out_dir>: JLCPCB BOM + CPL from the board (KiCad bundled python).

Coordinates are relative to the aux (drill/place) origin, which genpcb.py sets to the bottom-left corner.
Rotations are KiCad's; check part orientation in JLC's placement preview before ordering.
"""
import csv, os, sys
from collections import OrderedDict
import pcbnew

SKIP = ('H', 'TP', 'JP')  # mounting holes, test pads, solder jumpers: nothing to place


def main(path, out):
    board = pcbnew.LoadBoard(path)
    origin = board.GetDesignSettings().GetAuxOrigin()
    name = os.path.splitext(os.path.basename(path))[0]
    bom = OrderedDict()
    rows = []
    fps = sorted(board.GetFootprints(), key=lambda f: (f.GetReference().rstrip('0123456789'), int(''.join(c for c in f.GetReference() if c.isdigit()) or 0)))
    for fp in fps:
        ref = fp.GetReference()
        if ref.startswith(SKIP):
            continue
        lcsc = fp.GetFieldText('LCSC') if fp.HasField('LCSC') else ''
        key = (fp.GetValue(), fp.GetFPIDAsString().split(':')[1], lcsc)
        bom.setdefault(key, []).append(ref)
        pos = fp.GetPosition()
        rows.append([ref, f'{pcbnew.ToMM(pos.x - origin.x):.3f}mm', f'{pcbnew.ToMM(origin.y - pos.y):.3f}mm',
                     'Top' if fp.GetLayer() == pcbnew.F_Cu else 'Bottom', f'{fp.GetOrientationDegrees() % 360:.0f}',
                     'THT' if fp.GetAttributes() & pcbnew.FP_THROUGH_HOLE else 'SMD'])
    os.makedirs(out, exist_ok=True)
    with open(f'{out}/{name}-bom.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #'])
        for (val, fpn, lcsc), refs in bom.items():
            w.writerow([val, ','.join(refs), fpn, lcsc])
    with open(f'{out}/{name}-cpl.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation', 'Type'])
        w.writerows(rows)
    print(f'{name}: {len(bom)} BOM lines, {len(rows)} placements')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
