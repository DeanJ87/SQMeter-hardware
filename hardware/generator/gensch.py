"""Generate SQMeter-Hardware.kicad_sch from design.py (net-label style schematic)."""
import sys, uuid
from sexp import Sym, dump
from libs import flat, pins
import design

PROJECT = 'SQMeter-Hardware'
ROOT = str(uuid.uuid5(uuid.NAMESPACE_URL, 'sqmeter-root'))
_n = [0]


def U():
    _n[0] += 1
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f'sqmeter-{_n[0]}'))


def g(v):  # snap to 1.27 grid
    return round(v / 1.27) * 1.27


def font(hide=False, justify=None):
    e = [Sym('effects'), [Sym('font'), [Sym('size'), 1.27, 1.27]]]
    if justify:
        e.append([Sym('justify')] + [Sym(j) for j in justify.split()])
    if hide:
        e.append([Sym('hide'), Sym('yes')])
    return e


def prop(name, val, x, y, hide=False, justify=None, ang=0):
    return [Sym('property'), name, val, [Sym('at'), x, y, ang], font(hide, justify)]


OUT = {0: (-1, 0), 180: (1, 0), 90: (0, 1), 270: (0, -1)}  # pin rot -> outward dir (sch coords, y down)

items = []
lib_ids = set()
pwr_n = [0]


def instance(lib_id, ref, value, x, y, ang, props_extra, pinnums, ref_at=None, val_at=None, hide_ref=False):
    lib_ids.add(lib_id)
    s = [Sym('symbol'), [Sym('lib_id'), lib_id], [Sym('at'), x, y, ang], [Sym('unit'), 1],
         [Sym('exclude_from_sim'), Sym('no')], [Sym('in_bom'), Sym('yes' if not ref.startswith('#') else 'no')],
         [Sym('on_board'), Sym('yes' if not ref.startswith('#') else 'no')], [Sym('dnp'), Sym('no')], [Sym('uuid'), U()]]
    rx, ry = ref_at or (x, y)
    vx, vy = val_at or (x, y)
    s.append(prop('Reference', ref, rx, ry, hide=hide_ref, justify='left'))
    s.append(prop('Value', value, vx, vy, justify='left'))
    for k, v in props_extra:
        s.append(prop(k, v, x, y, hide=True))
    for p in pinnums:
        s.append([Sym('pin'), p, [Sym('uuid'), U()]])
    s.append([Sym('instances'), [Sym('project'), PROJECT,
                                 [Sym('path'), '/' + ROOT, [Sym('reference'), ref], [Sym('unit'), 1]]]])
    items.append(s)


def power_symbol(net, x, y, outward):
    pwr_n[0] += 1
    dx, dy = outward
    if net == 'GND':
        ang = {(0, 1): 0, (1, 0): 90, (0, -1): 180, (-1, 0): 270}[(dx, dy)]
    else:
        ang = {(0, -1): 0, (-1, 0): 90, (0, 1): 180, (1, 0): 270}[(dx, dy)]
    vx, vy = x + dx * 5, y + dy * 5
    instance(design.POWER_NETS[net], f'#PWR{pwr_n[0]:03d}', net, x, y, ang, [('Footprint', ''), ('Datasheet', '')], ['1'],
             ref_at=(x, y), val_at=(vx, vy), hide_ref=True)


def label(net, x, y, outward):
    ang = {(-1, 0): 180, (1, 0): 0, (0, 1): 270, (0, -1): 90}[outward]
    just = 'left bottom' if ang in (0, 90) else 'right bottom'
    items.append([Sym('label'), net, [Sym('at'), x, y, ang], font(justify=just), [Sym('uuid'), U()]])


def glabel(net, x, y, outward):
    ang = {(-1, 0): 180, (1, 0): 0}[outward]
    just = 'left' if ang == 0 else 'right'
    items.append([Sym('global_label'), net, [Sym('shape'), Sym('passive')], [Sym('at'), x, y, ang],
                  font(justify=just), [Sym('uuid'), U()],
                  [Sym('property'), 'Intersheetrefs', '${INTERSHEET_REFS}', [Sym('at'), x, y, 0], font(hide=True)]])


def noconnect(x, y):
    items.append([Sym('no_connect'), [Sym('at'), x, y], [Sym('uuid'), U()]])


def text(t, x, y, size=2.54):
    items.append([Sym('text'), t, [Sym('exclude_from_sim'), Sym('no')], [Sym('at'), x, y, 0],
                  [Sym('effects'), [Sym('font'), [Sym('size'), size, size], [Sym('bold'), Sym('yes')]], [Sym('justify'), Sym('left'), Sym('bottom')]],
                  [Sym('uuid'), U()]])


def bbox(part):
    ps = pins(part['lib'])
    if not ps:
        return -3, -3, 3, 3
    xs = [p['x'] for p in ps]; ys = [-p['y'] for p in ps]
    l, r, t, b = min(xs), max(xs), min(ys), max(ys)
    for p in ps:
        dx, dy = OUT[int(p['rot'])]
        if dx < 0: l = min(l, p['x'] - 16)
        if dx > 0: r = max(r, p['x'] + 16)
        if dy < 0: t = min(t, -p['y'] - 10)
        if dy > 0: b = max(b, -p['y'] + 10)
    right_pins = any(OUT[int(p['rot'])][0] > 0 for p in ps)
    if not right_pins:
        r = max(r, max(xs) + 24)
    else:
        t = t - 8
    return l, t, max(r, l + 14), max(b, t + 14)


def place(part, x, y):
    ps = pins(part['lib'])
    done = set()
    for p in ps:
        net = part['pins'].get(p['num'], 'UNSET')
        if net == 'UNSET':
            sys.exit(f"{part['ref']} pin {p['num']} unassigned")
        px, py = round(x + p['x'], 2), round(y - p['y'], 2)
        if (px, py) in done:
            continue
        done.add((px, py))
        out = OUT[int(p['rot'])]
        if net is None:
            noconnect(px, py)
        elif net in design.POWER_NETS and out[0] == 0:
            power_symbol(net, px, py, out)
        elif net in design.POWER_NETS:
            glabel(net, px, py, out)
        else:
            label(net, px, py, out)
    l, t, r, b = bbox(part)
    maxx = max([p['x'] for p in ps] + [0])
    miny = min([-p['y'] for p in ps] + [0])
    right_pins = any(OUT[int(p['rot'])][0] > 0 for p in ps)
    rx = x + max(maxx, 0) + 2.54
    if right_pins:
        top = min(-p['y'] for p in ps)
        top = min(top, min((-p['y'] for p in ps if OUT[int(p['rot'])][1] < 0), default=top) - 8)
        rx, miny = x - 5, (top - 6) * 2 - 0
    extra = [('Footprint', part['fp']), ('Datasheet', ''), ('Description', part['desc'])]
    if part['lcsc']:
        extra.append(('LCSC', part['lcsc']))
    instance(part['lib'], part['ref'], part['value'], x, y, 0, extra, sorted({p['num'] for p in ps}),
             ref_at=(rx, y + miny / 2 - 1.27 if ps else y - 3), val_at=(rx, y + miny / 2 + 1.27 if ps else y + 3))


def layout():
    byref = {p['ref']: p for p in design.parts}
    col_x, y0 = 15.24, 25.4
    x, y = col_x, y0
    max_w = 200
    col_w = 0
    for title, refs in design.blocks:
        # measure the block
        rows, row, w, rw = [], [], 0, 0
        for r in refs:
            l, t, rr, b = bbox(byref[r])
            pw = rr - l
            if row and rw + pw > max_w:
                rows.append(row); row, rw = [], 0
            row.append(r); rw += pw + 5
            w = max(w, rw)
        rows.append(row)
        heights = [max(bbox(byref[r])[3] - bbox(byref[r])[1] for r in rw_) for rw_ in rows]
        bh = sum(heights) + 5 * len(rows) + 10
        if y + bh > 400 and y > y0:
            x += col_w + 20; y = y0; col_w = 0
        text(title, g(x), g(y))
        cy = y + 8
        for rw_, h in zip(rows, heights):
            cx = x
            for r in rw_:
                l, t, rr, b = bbox(byref[r])
                place(byref[r], g(cx - l), g(cy - t))
                cx += rr - l + 5
            cy += h + 5
        col_w = max(col_w, w)
        y = cy + 10
    # power flags
    fx = x + col_w + 20 if y > 300 else x
    text('Power flags', g(fx), g(y))
    for i, net in enumerate(design.FLAGS):
        px, py = g(fx + 5 + i * 25), g(y + 15)
        instance('power:PWR_FLAG', f'#FLG{i + 1:02d}', 'PWR_FLAG', px, py, 0, [('Footprint', ''), ('Datasheet', '')], ['1'],
                 ref_at=(px, py), val_at=(px, py - 4), hide_ref=True)
        power_symbol(net, px, py, (0, 1) if net == 'GND' else (0, -1))
        if net != 'GND':
            # flag points up, power symbol also up -> move power symbol to a stub below via label-free trick: stack same point
            pass


def main(out):
    layout()
    sch = [Sym('kicad_sch'), [Sym('version'), 20250114], [Sym('generator'), 'eeschema'], [Sym('generator_version'), '9.0'],
           [Sym('uuid'), ROOT], [Sym('paper'), 'A2'],
           [Sym('title_block'), [Sym('title'), 'SQMeter main board'], [Sym('date'), '2026-10-16'], [Sym('rev'), 'v1.0-draft'],
            [Sym('company'), 'SQMeter'], [Sym('comment'), 1, 'ESP32-S3, 12 V input, JST-XH I2C ports']],
           [Sym('lib_symbols')] + [flat(l) for l in sorted(lib_ids)]]
    sch += items
    sch.append([Sym('sheet_instances'), [Sym('path'), '/', [Sym('page'), '1']]])
    sch.append([Sym('embedded_fonts'), Sym('no')])
    open(out, 'w').write(dump(sch) + '\n')


if __name__ == '__main__':
    main(sys.argv[1])
