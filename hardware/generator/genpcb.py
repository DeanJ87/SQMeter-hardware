"""Build SQMeter-Hardware.kicad_pcb: outline, rules, footprints, nets, placement. Run with KiCad's bundled python."""
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
    'F1': (8, 58, 90), 'D1': (14, 58, 90), 'Q1': (20, 58, 0), 'D2': (21, 52, 0), 'R1': (25, 53.5, 90),
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
    'J10': (96, 4.5, 0),
    # I2C ports, right edge
    'J3': (120.5, 27, 90), 'J4': (120.5, 41, 90), 'J5': (120.5, 55, 90), 'J6': (120.5, 69, 90),
    'R7': (106, 38, 90), 'R8': (109, 38, 90), 'U4': (107.5, 45, 90),
    # mounting
    'H1': (4, 4, 0), 'H2': (121, 4, 0), 'H3': (4, 78, 0), 'H4': (121, 78, 0),
}


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
        for pad in fp.Pads():
            if pad.HasHole() and pad.GetDrillSize().x < mm(0.3):  # JLC standard min drill
                pad.SetDrillSize(pcbnew.VECTOR2I(mm(0.3), mm(0.3))); pad.SetSize(pcbnew.VECTOR2I(mm(0.6), mm(0.6)))
            n = p['pins'].get(pad.GetNumber())
            if n:
                n = pinnet[(p['ref'], pad.GetNumber())]
                if n == 'GND' and p['ref'].startswith('J'):
                    pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)  # edge connectors: spokes get starved
                pad.SetNet(net(n))
        if p['ref'] in HIDE_REF:
            fp.Reference().SetVisible(False)
        board.Add(fp)

    # pre-route: ESD chips have GND in the middle of a signal row -> stub + via outward before autorouting
    for ref in ('U2', 'U4', 'U5', 'U6'):
        fp = board.FindFootprintByReference(ref)
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
            txt(board, names[i], pcbnew.ToMM(pos.x) + off[0], pcbnew.ToMM(pos.y) + off[1], ang, 0.9,
                'right' if off[0] < 0 else ('left' if ang in (90, 270) else 'center'))
        if title:
            bb = fp.GetBoundingBox(False)
            tx, ty, tang = title[1]
            txt(board, title[0], tx, ty, tang, 1.1, 'center')
    txt(board, 'SQMeter v1.0', 55, 34.5, 0, 1.5, 'center')
    txt(board, 'I2C ports: 1 GND  2 3V3  3 SDA  4 SCL', 55, 37.5, 0, 1.0, 'center')
    pcbnew.SaveBoard(out, board)


def txt(board, s, x, y, ang, size, just):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s); t.SetLayer(pcbnew.F_SilkS)
    t.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    t.SetTextAngleDegrees(ang)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size))); t.SetTextThickness(mm(size * 0.15))
    t.SetHorizJustify({'left': pcbnew.GR_TEXT_H_ALIGN_LEFT, 'right': pcbnew.GR_TEXT_H_ALIGN_RIGHT,
                       'center': pcbnew.GR_TEXT_H_ALIGN_CENTER}[just])
    board.Add(t)


I2C = ['GND', '3V3', 'SDA', 'SCL']
# silkscreen titles/pin labels already identify these
HIDE_REF = {'J1', 'J2', 'J3', 'J4', 'J5', 'J6', 'J7', 'J8', 'J9', 'J10', 'H1', 'H2', 'H3', 'H4'}
UP = ((0, -3.2), 90)      # vertical text above a horizontal pad row
PINLABELS = {
    'J1': (['+12V', 'GND'], (0, -3.6), 90, None),
    'J8': (['GND', 'V+', 'RG TX', 'RG RX'], UP[0], 90, ('RG-15', (65.25, 55.5, 0))),
    'J9': (['SPD', 'GND', 'DIR', 'GND', '3V3'], UP[0], 90, ('WIND', (89, 54.5, 0))),
    'J7': (['GND', '3V3', 'GPS TX', 'GPS RX'], (0, 4.6), 270, ('GPS', (85.75, 22, 0))),
    'J10': (['GND', '3V3', 'IO6', 'IO7', 'IO10', 'IO11'], (0, 4.6), 270, ('AUX', (102.25, 15, 0))),
    'J3': (I2C, (-3.6, 0), 0, ('TSL2591', (113.5, 17.5, 0))),
    'J4': (I2C, (-3.6, 0), 0, ('MLX90614', (113.5, 31.5, 0))),
    'J5': (I2C, (-3.6, 0), 0, ('BME280', (113.5, 45.5, 0))),
    'J6': (I2C, (-3.6, 0), 0, ('I2C SPARE', (113.5, 59.5, 0))),
}


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
