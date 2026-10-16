"""route.py <pcb> <stage>: stage 'export' adds GND pours + writes DSN; stage 'import' reads SES, fills zones, saves."""
import sys
import pcbnew

mm = pcbnew.FromMM
W, H, INSET = 125.0, 82.0, 0.4


def add_gnd_zones(board):
    gnd = board.FindNet('GND')
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(board)
        z.SetLayer(layer)
        z.SetNet(gnd)
        z.SetIsRuleArea(False)
        z.SetLocalClearance(mm(0.3))
        z.SetMinThickness(mm(0.25))
        z.SetThermalReliefGap(mm(0.3))
        z.SetThermalReliefSpokeWidth(mm(0.5))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THT_THERMAL)
        z.SetAssignedPriority(0)
        o = z.Outline()
        o.NewOutline()
        for x, y in ((INSET, INSET), (W - INSET, INSET), (W - INSET, H - INSET), (INSET, H - INSET)):
            o.Append(mm(x), mm(y))
        board.Add(z)


def stitch(board, pitch=5.0, margin=0.75):
    """GND vias on a grid wherever nothing else is nearby (keeps antenna area and courtyards clear)."""
    gnd = board.FindNet('GND')
    obstacles = [p for p in board.GetPads()] + [t for t in board.GetTracks()]
    court = []
    for fp in board.GetFootprints():
        for layer in (pcbnew.F_CrtYd,):
            poly = fp.GetCourtyard(layer)
            if poly.OutlineCount():
                court.append(poly)
    n = 0
    y = 3.0
    while y < H - 2.5:
        x = 3.0
        while x < W - 2.5:
            pos = pcbnew.VECTOR2I(mm(x), mm(y))
            ok = not (31 <= x <= 79 and y <= 8)  # antenna
            ok = ok and not any(c.Contains(pos) for c in court)
            ok = ok and not any(o.HitTest(pos, mm(margin)) for o in obstacles)
            if ok:
                v = pcbnew.PCB_VIA(board)
                v.SetPosition(pos); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3)); v.SetNet(gnd)
                board.Add(v); n += 1
            x += pitch
        y += pitch
    return n


def free(board, pos, margin):
    if any(o.HitTest(pos, mm(margin)) for o in list(board.GetPads()) + list(board.GetTracks())):
        return False
    return True


def stitch_islands(board):
    """Put a GND via inside every filled GND fragment so no pour island is left floating."""
    gnd = board.FindNet('GND')
    n = 0
    for z in board.Zones():
        if z.GetNetname() != 'GND':
            continue
        layer = z.GetLayer()
        other = pcbnew.B_Cu if layer == pcbnew.F_Cu else pcbnew.F_Cu
        oz = next(o for o in board.Zones() if o.GetNetname() == 'GND' and o.GetLayer() == other)
        fill = z.GetFilledPolysList(layer)
        ofill = oz.GetFilledPolysList(other)
        for i in range(fill.OutlineCount()):
            frag = pcbnew.SHAPE_POLY_SET(); frag.AddOutline(fill.Outline(i))
            # already has a via?
            if any(isinstance(t, pcbnew.PCB_VIA) and t.GetNetname() == 'GND' and frag.Contains(t.GetPosition())
                   for t in board.GetTracks()):
                continue
            bb = fill.Outline(i).BBox()
            step = mm(0.5)
            done = False
            yy = bb.GetTop()
            while yy < bb.GetBottom() and not done:
                xx = bb.GetLeft()
                while xx < bb.GetRight() and not done:
                    pos = pcbnew.VECTOR2I(int(xx), int(yy))
                    if frag.Contains(pos) and ofill.Contains(pos) and frag.Collide(pos, -mm(0.45)) and free(board, pos, 0.55):
                        inner = pcbnew.SHAPE_POLY_SET(frag); inner.Deflate(mm(0.35), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, mm(0.01))
                        if inner.Contains(pos):
                            v = pcbnew.PCB_VIA(board)
                            v.SetPosition(pos); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3)); v.SetNet(gnd)
                            board.Add(v); n += 1; done = True
                    xx += step
                yy += step
    return n


def fanout_islands(board):
    """For GND fragments with no via and no through-hole pad, drop a via beside one of their SMD pads."""
    import math
    gnd = board.FindNet('GND')
    vias = [t for t in board.GetTracks() if isinstance(t, pcbnew.PCB_VIA) and t.GetNetname() == 'GND']
    pads = [p for p in board.GetPads() if p.GetNetname() == 'GND']
    n = 0
    for z in list(board.Zones()):
        if z.GetNetname() != 'GND':
            continue
        L = z.GetLayer(); f = z.GetFilledPolysList(L)
        for i in range(f.OutlineCount()):
            frag = pcbnew.SHAPE_POLY_SET(); frag.AddOutline(f.Outline(i))
            if any(frag.Contains(v.GetPosition()) for v in vias):
                continue
            inside = [p for p in pads if p.IsOnLayer(L) and frag.Collide(p.GetPosition(), 0)]
            if not inside or any(p.HasHole() for p in inside):
                continue
            placed = False
            for p in inside:
                c = p.GetPosition(); r = max(p.GetSize().x, p.GetSize().y) / 2 + mm(0.75)
                for k in range(16):
                    a = k * math.pi / 8
                    pos = pcbnew.VECTOR2I(int(c.x + r * math.cos(a)), int(c.y + r * math.sin(a)))
                    others = [o for o in list(board.GetPads()) + list(board.GetTracks()) if o.GetNetname() != 'GND']
                    if any(o.HitTest(pos, mm(0.55)) for o in others):
                        continue
                    t = pcbnew.PCB_TRACK(board); t.SetStart(c); t.SetEnd(pos); t.SetWidth(mm(0.4)); t.SetLayer(L); t.SetNet(gnd)
                    seg_ok = not any(o.HitTest(pcbnew.VECTOR2I((c.x + pos.x) // 2, (c.y + pos.y) // 2), mm(0.45)) for o in others)
                    if not seg_ok:
                        continue
                    v = pcbnew.PCB_VIA(board); v.SetPosition(pos); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3)); v.SetNet(gnd)
                    board.Add(t); board.Add(v); vias.append(v); n += 1; placed = True
                    break
                if placed:
                    break
    return n


def main(path, stage, side):
    board = pcbnew.LoadBoard(path)
    if stage == 'export':
        if not any(z.GetNetname() == 'GND' for z in board.Zones()):
            add_gnd_zones(board)
        pcbnew.SaveBoard(path, board)
        board = pcbnew.LoadBoard(path)
        ok = pcbnew.ExportSpecctraDSN(board, side)
        print('dsn', ok)
    else:
        ok = pcbnew.ImportSpecctraSES(board, side)
        print('ses', ok)
        print('stitch vias', stitch(board))
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(board.Zones())
        print('island vias', stitch_islands(board))
        filler.Fill(board.Zones())
        print('fanout vias', fanout_islands(board))
        filler.Fill(board.Zones())
        pcbnew.SaveBoard(path, board)
        print('tracks', len(board.GetTracks()))


if __name__ == '__main__':
    main(*sys.argv[1:4])
