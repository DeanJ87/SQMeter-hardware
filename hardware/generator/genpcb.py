"""Build the board: outline, rules, footprints, nets, placement. Run with KiCad's bundled python.

SQM_VARIANT=devkit swaps the soldered ESP32 module for DevKitC-1 sockets (see design.py)."""
import sys
import pcbnew
import design
from sexp import parse, find, find1


def netlist(path):
    """(ref, pin) -> net name and ref -> symbol uuid, from the schematic netlist."""
    n = parse(open(path).read())[0]
    pinnet, uuids = {}, {}
    for c in find(find1(n, 'components'), 'comp'):
        uuids[find1(c, 'ref')[1]] = find1(c, 'tstamps')[1]
    for e in find(find1(n, 'nets'), 'net'):
        for nd in find(e, 'node'):
            pinnet[(find1(nd, 'ref')[1], find1(nd, 'pin')[1])] = find1(e, 'name')[1]
    return pinnet, uuids

FPDIR = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints'
W, H = 125.0, 82.0
mm = pcbnew.FromMM

# ref: (x, y, rot)  -- origin top-left, y down
PLACE = {
    # ESP32-S3: antenna on the top edge
    'U3': (55, 13.25, 0),
    'C8': (43.2, 9.0, 90), 'C7': (43.2, 12.6, 90),
    'R4': (30, 10, 0), 'C9': (30, 13, 0), 'SW1': (21, 12, 0),
    'R5': (30, 23, 0), 'SW2': (21, 23, 0),
    'R6': (70, 19, 90), 'D4': (70, 23, 90),
    'TP1': (47, 30, 0), 'TP2': (51, 30, 0), 'TP3': (59, 30, 0), 'TP4': (63, 30, 0),
    # USB-C, left edge
    'J2': (3.6, 20, 270), 'U2': (12, 20, 90), 'R2': (10, 13.5, 0), 'R3': (10, 26.5, 0),
    # power, bottom left
    'J1': (12, 71.5, 0),
    'F1': (8, 58, 90), 'D1': (14, 58, 90), 'Q1': (20, 58, 0), 'R19': (21, 51, 90), 'R1': (25, 53.5, 90),
    'D3': (12, 40, 90),
    'C1': (31, 60, 0), 'C2': (38.5, 52, 90), 'C3': (38.5, 56.5, 90),
    'U1': (43, 52, 0), 'C4': (43, 47.5, 0), 'L1': (51, 52, 0), 'C5': (58, 49.5, 90), 'C6': (58, 54.5, 90),
    'F2': (50, 64, 0),
    # RG-15, bottom
    'J8': (60, 73, 0), 'R11': (62, 60, 90), 'R12': (65, 60, 90), 'U5': (70, 60, 0),
    # Wind, bottom right
    'J9': (82, 73, 0), 'R13': (82, 64, 90), 'R14': (85, 64, 90), 'C10': (88, 64, 90),
    'JP1': (82, 58, 0), 'R15': (86, 58, 0), 'R16': (90, 58, 0), 'C11': (94, 58, 90), 'U6': (95, 64.5, 0),
    # GPS + AUX, top right
    'J7': (82, 4.5, 0), 'R9': (84, 17, 90), 'R10': (88, 17, 90),
    'J10': (95.5, 4.5, 0),
    # second I2C bus (TSL2591 #2), top right
    'J13': (109, 4.5, 0), 'R20': (99, 18.5, 90), 'R21': (102, 18.5, 90), 'U7': (106, 21, 90),
    # I2C ports, right edge
    'J3': (120.5, 27, 90), 'J4': (120.5, 41, 90), 'J5': (120.5, 55, 90), 'J6': (120.5, 69, 90),
    'R7': (106, 38, 90), 'R8': (109, 38, 90), 'U4': (104, 44, 90),
    # mounting
    'H1': (4, 4, 0), 'H2': (121.5, 11.5, 0), 'H3': (4, 78, 0), 'H4': (121, 78, 0),
}

# DevKitC-1 (Espressif DXF v1.1): 25.4 x 62.865 mm, header rows 22.86 mm apart, pins 2.54 mm,
# first pin 7.96 mm from the USB end, pin 1 at the antenna end.
DK_X0, DK_Y1 = 0.5, 10.0          # USB end at the left board edge; J1 row y
DK_PIN1_X = DK_X0 + 7.96 + 21 * 2.54
# Outline of the plug-in board on our PCB: x0 = USB end, antenna at x1. 'first' = which socket pin sits left.
if design.DEVKIT:
    PLACE.update({'J11': (DK_PIN1_X, DK_Y1, 90), 'J12': (DK_PIN1_X, DK_Y1 + 22.86, 90)})
    DK = dict(x0=DK_X0, x1=DK_X0 + 62.865, y0=DK_Y1 - 1.27, y1=DK_Y1 - 1.27 + 25.4, ant=7.5,
              first={'J11': '22', 'J12': '22'}, title='ESP32-S3-DevKitC-1', tx=32)
elif design.ZERO:
    # Waveshare drawing: 18 x 23.5 mm, rows 15.24 mm apart, first pin 1.17 mm from the USB end.
    # Turned so USB faces the left edge: right column (TX..GP7) on top, left column (5V..GP6) below.
    ZX0, ZY = 1.2, 12.0
    PLACE.update({'J12': (ZX0 + 1.17, ZY, 90), 'J11': (ZX0 + 1.17, ZY + 15.24, 90)})
    DK = dict(x0=ZX0, x1=ZX0 + 23.5, y0=ZY - 1.38, y1=ZY + 15.24 + 1.38, ant=5.0,
              first={'J11': '1', 'J12': '1'}, title='ESP32-S3-Zero', tx=12)


def main(out, netfile):
    pinnet, uuids = netlist(netfile)
    board = pcbnew.BOARD()
    # design rules (JLCPCB 2-layer friendly, with margin)
    ds = board.GetDesignSettings()
    ds.m_TrackMinWidth = mm(0.15)
    ds.m_MinClearance = mm(0.15)
    ds.m_ViasMinSize = mm(0.5)
    ds.m_MinThroughDrill = mm(0.3)
    ds.m_CopperEdgeClearance = mm(0.3)
    ds.m_HoleToHoleMin = mm(0.5)
    ds.SetAuxOrigin(pcbnew.VECTOR2I(0, mm(H)))   # bottom-left corner: positive fab coordinates
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetClearance(mm(0.2)); nc.SetTrackWidth(mm(0.25)); nc.SetViaDiameter(mm(0.6)); nc.SetViaDrill(mm(0.3))

    # outline with rounded corners
    r = 3.0
    def seg(x1, y1, x2, y2):
        s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1))); s.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); board.Add(s)
    def arc(cx, cy, sx, sy):
        a = pcbnew.PCB_SHAPE(board); a.SetShape(pcbnew.SHAPE_T_ARC)
        a.SetCenter(pcbnew.VECTOR2I(mm(cx), mm(cy))); a.SetStart(pcbnew.VECTOR2I(mm(sx), mm(sy)))
        a.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T), True)
        a.SetLayer(pcbnew.Edge_Cuts); a.SetWidth(mm(0.1)); board.Add(a)
    seg(r, 0, W - r, 0); seg(W, r, W, H - r); seg(W - r, H, r, H); seg(0, H - r, 0, r)
    arc(r, r, 0, r); arc(W - r, r, W - r, 0); arc(W - r, H - r, W, H - r); arc(r, H - r, r, H)

    nets = {}
    def net(name):
        if name not in nets:
            n = pcbnew.NETINFO_ITEM(board, name); board.Add(n); nets[name] = n
        return nets[name]

    missing = [p['ref'] for p in design.parts if p['ref'] not in PLACE]
    # parts that only exist in the other variant are simply not placed
    if missing:
        sys.exit(f'unplaced: {missing}')
    for p in design.parts:
        lib, name = p['fp'].split(':')
        fp = pcbnew.FootprintLoad(f'{FPDIR}/{lib}.pretty', name)
        fp.SetReference(p['ref']); fp.SetValue(p['value'])
        fp.SetFPIDAsString(p['fp'])
        fp.SetPath(pcbnew.KIID_PATH('/' + uuids[p['ref']]))
        if p['lcsc']:
            fp.SetField('LCSC', p['lcsc'])
            fp.GetField('LCSC').SetVisible(False)
        x, y, rot = PLACE[p['ref']]
        fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        fp.SetOrientationDegrees(rot)
        if design.PLUGIN and p['ref'] in ('J11', 'J12'):  # make DK['first'] the leftmost (USB-end) pin
            pads = {pd.GetNumber(): pd.GetPosition().x for pd in fp.Pads()}
            if pads[DK['first'][p['ref']]] != min(pads.values()):
                fp.SetOrientationDegrees(rot + 180)
                pads = {pd.GetNumber(): pd.GetPosition().x for pd in fp.Pads()}
                # rotate about pin 1, keep pin 1 where PLACE put it
                fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        for pad in fp.Pads():
            if pad.HasHole() and pad.GetDrillSize().x < mm(0.3):  # JLC standard min drill
                pad.SetDrillSize(pcbnew.VECTOR2I(mm(0.3), mm(0.3))); pad.SetSize(pcbnew.VECTOR2I(mm(0.6), mm(0.6)))
            n = p['pins'].get(pad.GetNumber())
            if n:
                n = pinnet[(p['ref'], pad.GetNumber())]
                if n == 'GND' and p['ref'].startswith('J'):
                    pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)  # edge connectors: spokes get starved
                pad.SetNet(net(n))
        inter(fp.Reference(), 1.0)
        if p['ref'] in HIDE_REF:
            fp.Reference().SetVisible(False)
        board.Add(fp)

    # pre-route: ESD chips have GND in the middle of a signal row -> stub + via outward before autorouting
    for ref in ('U2', 'U4', 'U5', 'U6', 'U7'):
        fp = board.FindFootprintByReference(ref)
        if fp is None:
            continue
        c = fp.GetPosition()
        pad = next(p for p in fp.Pads() if p.GetNumber() == '2')
        pp = pad.GetPosition()
        dx, dy = pp.x - c.x, pp.y - c.y
        ln = (dx * dx + dy * dy) ** 0.5
        end = pcbnew.VECTOR2I(int(pp.x + dx / ln * mm(1.4)), int(pp.y + dy / ln * mm(1.4)))
        gnd = pad.GetNet()
        t = pcbnew.PCB_TRACK(board); t.SetStart(pp); t.SetEnd(end); t.SetWidth(mm(0.4)); t.SetLayer(pcbnew.F_Cu); t.SetNet(gnd)
        v = pcbnew.PCB_VIA(board); v.SetPosition(end); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3)); v.SetNet(gnd)
        t.SetLocked(True); v.SetLocked(True)
        board.Add(t); board.Add(v)

    # silkscreen pin labels: ref -> (names, offset from pad (mm), text angle)
    for ref, (names, off, ang, title) in PINLABELS.items():
        fp = board.FindFootprintByReference(ref)
        for pad in fp.Pads():
            i = int(pad.GetNumber()) - 1
            pos = pad.GetPosition()
            txt(board, names[i], pcbnew.ToMM(pos.x) + off[0], pcbnew.ToMM(pos.y) + off[1], ang, 1.2,
                'right' if off[0] < 0 else ('left' if ang in (90, 270) else 'center'))
        if title:
            bb = fp.GetBoundingBox(False)
            tx, ty, tang = title[1]
            txt(board, title[0], tx, ty, tang, 1.3, 'center')
    ty = 38 if design.PLUGIN else 36.5
    lockup(board, 55, ty, 7.0)
    txt(board, f'Rev {design.HW_REV}  {design.VARIANT_LABEL}', 55, ty + 6.4, 0, 1.3, 'center')
    tb = board.GetTitleBlock()
    tb.SetTitle('SQMeter main board (' + design.VARIANT_LABEL + ')'); tb.SetRevision(design.HW_REV)
    tb.SetCompany('SQMeter'); tb.SetDate('2026-10-16')
    if design.PLUGIN:
        devkit_outline(board)
    pcbnew.SaveBoard(out, board)
    colours(out)
    silk_font(out)


def devkit_outline(board):
    """Silkscreen footprint of the plugged-in DevKit plus a no-pour/no-via area under its antenna."""
    x0, x1, y0, y1 = DK['x0'], DK['x1'], DK['y0'], DK['y1']
    m = 0.6  # silk drawn just outside the real outline so it clears the socket silk
    sx0, sx1, sy0, sy1 = max(x0 - m, 0.3), x1 + m, y0 - m, y1 + m
    for a, b in (((sx0, sy0), (sx1, sy0)), ((sx1, sy0), (sx1, sy1)), ((sx1, sy1), (sx0, sy1)), ((sx0, sy1), (sx0, sy0))):
        s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.F_SilkS); s.SetWidth(mm(0.15))
        s.SetStart(pcbnew.VECTOR2I(mm(a[0]), mm(a[1]))); s.SetEnd(pcbnew.VECTOR2I(mm(b[0]), mm(b[1]))); board.Add(s)
    cy = (y0 + y1) / 2
    txt(board, DK['title'], DK['tx'], cy - 1.5, 0, 1.3, 'center')
    txt(board, '<- USB this end', DK['tx'], cy + 1.5, 0, 1.1, 'center')
    txt(board, 'ANTENNA', x1 - DK['ant'] / 2, cy, 90, 1.0, 'center')
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True); z.SetLayerSet(pcbnew.LSET.AllCuMask())
    z.SetDoNotAllowZoneFills(True); z.SetDoNotAllowVias(True)
    z.SetDoNotAllowTracks(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    z.SetZoneName('DevKit antenna')
    o = z.Outline(); o.NewOutline()
    for x, y in ((x1 - DK['ant'], y0), (x1, y0), (x1, y1), (x1 - DK['ant'], y1)):
        o.Append(mm(x), mm(y))
    board.Add(z)


STACKUP = """		(stackup
			(layer "F.SilkS" (type "Top Silk Screen") (color "White"))
			(layer "F.Paste" (type "Top Solder Paste"))
			(layer "F.Mask" (type "Top Solder Mask") (color "Black") (thickness 0.01))
			(layer "F.Cu" (type "copper") (thickness 0.035))
			(layer "dielectric 1" (type "core") (thickness 1.51) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
			(layer "B.Cu" (type "copper") (thickness 0.035))
			(layer "B.Mask" (type "Bottom Solder Mask") (color "Black") (thickness 0.01))
			(layer "B.Paste" (type "Bottom Solder Paste"))
			(layer "B.SilkS" (type "Bottom Silk Screen") (color "White"))
			(copper_finish "HAL lead-free")
			(dielectric_constraints no)
		)
"""


def colours(path):
    """1.6 mm 2-layer stackup with black solder mask and white silkscreen (on brand; free at JLC for 2-layer).
    This only sets KiCad's 3D view; the real colours are picked on the JLC order form. pcbnew's Python
    bindings don't expose the stackup, so it's written into the saved file."""
    s = open(path).read()
    if '(stackup' not in s:
        i = s.index('(setup') + len('(setup')
        s = s[:i] + '\n' + STACKUP + s[i:].lstrip('\n')
        open(path, 'w').write(s)


def silk_font(path):
    """Set every silkscreen text (board text and footprint references) in Inter Bold and turn on font
    embedding. pcbnew's Python bindings can't set a TrueType face, so this edits the saved file; route.py's
    final save then embeds the font file in the board, so it opens the same without Inter installed."""
    from sexp import parse, dump, Sym, find, find1
    tree = parse(open(path).read())[0]

    def walk(node):
        for e in node:
            if isinstance(e, list) and e:
                walk(e)
        layer = find1(node, 'layer')
        eff = find1(node, 'effects')
        if layer and layer[1] in ('F.SilkS', 'B.SilkS') and eff:
            font = find1(eff, 'font')
            if font and not find1(font, 'face'):
                font[:] = [e for e in font if not (isinstance(e, list) and e and e[0] in ('thickness', 'bold'))]
                font.insert(1, [Sym('face'), FONT])
                font.append([Sym('bold'), Sym('yes')])
    walk(tree)
    for e in tree:
        if isinstance(e, list) and e and e[0] == 'embedded_fonts':
            e[1] = Sym('yes')
    open(path, 'w').write(dump(tree) + '\n')


def lockup(board, cx, cy, height):
    """SQMeter brand lockup (mark + name in Inter) from brand_silk.json, centred on (cx, cy)."""
    import json, os
    data = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'brand_silk.json')))
    k = height / data['height']
    x0, y0 = cx - data['width'] * k / 2, cy - height / 2
    def chain(pts):
        c = pcbnew.SHAPE_LINE_CHAIN()
        for x, y in pts[:-1]:
            c.Append(mm(x0 + x * k), mm(y0 + y * k))
        c.SetClosed(True)
        return c
    for p in data['polygons']:
        ps = pcbnew.SHAPE_POLY_SET()
        ps.AddOutline(chain(p['outline']))
        for h in p['holes']:
            ps.AddHole(chain(h))
        s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_POLY); s.SetLayer(pcbnew.F_SilkS)
        s.SetPolyShape(ps); s.SetFilled(True); s.SetWidth(0)
        board.Add(s)


# Silkscreen type: Inter (the brand font) in bold. JLC prints 0.15 mm lines and 1 mm text at minimum;
# Measured on plotted gerbers: Inter Bold at 1.0 mm keeps its stems above 0.15 mm (a 0.15 mm opening
# removes ~2% of area, all corners and tips); 1.2 mm leaves margin. Regular would print patchy.
# KiCad's text_thickness DRC flags every size of the variable Inter font, so it's ignored (netclasses.py).
FONT, MIN_SIZE = 'Inter', 1.2


def inter(t, size):
    size = max(size, MIN_SIZE)
    t.SetUnresolvedFontName(FONT); t.SetBold(True)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))


def txt(board, s, x, y, ang, size, just):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s); t.SetLayer(pcbnew.F_SilkS)
    t.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    t.SetTextAngleDegrees(ang)
    inter(t, size)
    t.SetHorizJustify({'left': pcbnew.GR_TEXT_H_ALIGN_LEFT, 'right': pcbnew.GR_TEXT_H_ALIGN_RIGHT,
                       'center': pcbnew.GR_TEXT_H_ALIGN_CENTER}[just])
    board.Add(t)


I2C = ['GND', '3V3', 'SDA', 'SCL']
# silkscreen titles/pin labels already identify these
HIDE_REF = {'J1', 'J2', 'J3', 'J4', 'J5', 'J6', 'J7', 'J8', 'J9', 'J10', 'J11', 'J12', 'J13', 'H1', 'H2', 'H3', 'H4'}
UP = ((0, -3.2), 90)      # vertical text above a horizontal pad row
PINLABELS = {
    'J1': (['+12V', 'GND'], (0, -3.6), 90, None),
    'J8': (['GND', 'V+', 'RG TX', 'RG RX'], UP[0], 90, ('RG-15', (65.25, 55.5, 0))),
    'J9': (['SPD', 'GND', 'DIR', 'GND', '3V3'], UP[0], 90, ('WIND', (89, 54.5, 0))),
    'J7': (['GND', '3V3', 'GPS TX', 'GPS RX'], (0, 4.6), 270, ('GPS', (85.75, 22, 0))),
    'J10': (['GND', '3V3', 'IO6', 'IO7'], (0, 4.6), 270, ('AUX', (99.25, 14.2, 0))),
    'J13': (I2C, (0, 4.6), 270, ('I2C-2', (112.75, 14.2, 0))),
    'J3': (I2C, (-3.6, 0), 0, ('TSL2591 #1', (110.5, 17.5, 0))),
    'J4': (I2C, (-3.6, 0), 0, ('MLX90614', (111, 31.5, 0))),
    'J5': (I2C, (-3.6, 0), 0, ('BME280', (111, 45.5, 0))),
    'J6': (I2C, (-3.6, 0), 0, ('I2C SPARE', (111, 59.5, 0))),
}


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
