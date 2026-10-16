"""brand_silk.py <inter-sqm.woff2> <out.json>: SQMeter lockup (silkscreen mark + "SQMeter" in Inter 600) as polygons.

Rebuilds the brand lockup from the brand kit (SQMeter repo, brand/src/logo/sqmeter-mark-silkscreen.svg and
sqmeter-lockup-horizontal-mono.svg) as plain polygons, so the board needs no fonts installed and the gerbers
come out identical everywhere. The output is committed as brand_silk.json; genpcb.py only reads that.

Needs fonttools, brotli and shapely (not KiCad's Python):
    python3 -m venv .venv && .venv/bin/pip install fonttools brotli shapely
    .venv/bin/python brand_silk.py inter-sqm.woff2 brand_silk.json
The font is the app's copy of Inter: web/src/assets/fonts/inter-sqm.woff2 in the SQMeter repo.
"""
import json, math, sys
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.basePen import BasePen
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity

STEPS = 12  # segments per curve


def rrect(x, y, w, h, r):
    return box(x + r, y + r, x + w - r, y + h - r).buffer(r, quad_segs=16)


def quad(p0, p1, p2):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in (i / STEPS for i in range(1, STEPS + 1))]


def mark():
    """sqmeter-mark-silkscreen.svg on its 24-unit grid (y down). White = silk."""
    frame = rrect(2.25, 2.25, 19.5, 19.5, 2.75).difference(rrect(3.75, 3.75, 16.5, 16.5, 1.25))  # rect rx2, stroke 1.5
    stars = [Point(6.4, 6.6).buffer(.65, quad_segs=8), Point(9.8, 5.5).buffer(.65, quad_segs=8)]
    clip = rrect(3.75, 3.75, 16.5, 16.5, 1.25)
    # beam: wedge centred on (12.8, 13.1), r 10, from (13.67, 3.14) clockwise to (20.99, 7.36)
    c = (12.8, 13.1)
    a1, a2 = math.atan2(3.14 - c[1], 13.67 - c[0]), math.atan2(7.36 - c[1], 20.99 - c[0])
    beam = Polygon([c] + [(c[0] + 10 * math.cos(a1 + (a2 - a1) * i / 32), c[1] + 10 * math.sin(a1 + (a2 - a1) * i / 32))
                          for i in range(33)])
    p, q1 = (2.25, 19.7), (7.5, 18.75)
    m = (12, 19.35)
    q2 = (2 * m[0] - q1[0], 2 * m[1] - q1[1])  # T reflects the control point
    horizon = Polygon([p] + quad(p, q1, m) + quad(m, q2, (21.75, 18.9)) + [(21.75, 21.75), (2.25, 21.75)])
    head = affinity.rotate(affinity.scale(Point(7.1, 12.45).buffer(1, quad_segs=16), 1.5, 1.7), 14, origin=(7.1, 12.45))
    neck = box(6.45, 13.8, 7.55, 15.5)
    body = Polygon([(5.25, 21.75), (4.5, 17.1)] + quad((4.5, 17.1), (4.3, 15.5), (5.8, 15.2)) + [(8.2, 15.2)]
                   + quad((8.2, 15.2), (9.6, 15.4), (9.5, 16.9)) + [(8.75, 21.75)])
    arm = LineString([(9, 15.9), (10.75, 16.15), (12.15, 13.85)]).buffer(1.35 / 2, cap_style='round', join_style='round')
    hand = LineString([(11.85, 14.15), (12.8, 13.1)]).buffer(1.1 / 2, cap_style='round')
    scene = unary_union([beam, horizon, head, neck, body, arm, hand]).intersection(clip)
    return unary_union([frame, *stars, scene])


class FlatPen(BasePen):
    def __init__(self, glyphset):
        super().__init__(glyphset); self.contours = []; self.cur = []

    def _moveTo(self, p): self.cur = [p]
    def _lineTo(self, p): self.cur.append(p)
    def _qCurveToOne(self, p1, p2): self.cur += quad(self.cur[-1], p1, p2)

    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        self.cur += [tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t * t * c_ + t ** 3 * d
                           for a, b, c_, d in zip(p0, p1, p2, p3)) for t in (i / STEPS for i in range(1, STEPS + 1))]

    def _closePath(self):
        if len(self.cur) > 2: self.contours.append(self.cur)
        self.cur = []
    _endPath = _closePath


def text(font, s, size, x0, baseline, tracking_em=0.0):
    """Even-odd fill of each glyph's contours, laid out with advance widths (y down)."""
    gs, cmap, upm = font.getGlyphSet(), font.getBestCmap(), font['head'].unitsPerEm
    k, x, shapes = size / upm, x0, []
    for ch in s:
        g = cmap.get(ord(ch))
        if g is None:  # the app's subset has no space glyph
            x += 0.28 * size; continue
        pen = FlatPen(gs); gs[g].draw(pen)
        # Nonzero fill: variable-font instances keep overlapping contours, so even-odd would punch holes.
        # In font units (y up) outer contours run clockwise (negative area); each hole is cut only from the
        # smallest outer that contains it.
        outers, holes = [], []
        for c in pen.contours:
            area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(c, c[1:] + c[:1])) / 2
            poly = Polygon([(x + px * k, baseline - py * k) for px, py in c]).buffer(0)
            (outers if area < 0 else holes).append(poly)
        for h in holes:
            owners = [o for o in outers if o.contains(h.representative_point())]
            if owners:
                o = min(owners, key=lambda p: p.area)
                outers[outers.index(o)] = o.difference(h)
        if outers: shapes.append(unary_union(outers))
        x += font['hmtx'][g][0] * k + tracking_em * size
    return unary_union(shapes), x


def polys(geom, scale):
    geoms = getattr(geom, 'geoms', [geom])
    return [{'outline': [[round(x * scale, 4), round(y * scale, 4)] for x, y in g.exterior.coords],
             'holes': [[[round(x * scale, 4), round(y * scale, 4)] for x, y in h.coords] for h in g.interiors]}
            for g in geoms if g.area > 0]


def main(woff2, out):
    font = TTFont(woff2)
    font = instantiateVariableFont(font, {'wght': 600})
    # Lockup (sqmeter-lockup-horizontal-mono.svg): 48-unit mark, name at x 64, baseline 34, 30 px, tracking -0.3 px
    m = affinity.scale(mark(), 2, 2, origin=(0, 0))          # 24 -> 48 units
    name, end = text(font, 'SQMeter', 30, 64, 34, -0.3 / 30)
    lockup = unary_union([m, name]).simplify(0.02)
    unit = 1 / 48                                               # 1.0 = mark height
    json.dump({'source': 'brand kit: sqmeter-mark-silkscreen.svg + Inter 600 "SQMeter" (lockup-horizontal)',
               'height': 1.0, 'width': round(end * unit, 4), 'polygons': polys(lockup, unit)}, open(out, 'w'))
    print(f'lockup: {len(polys(lockup, unit))} polygons, aspect {end / 48:.2f}:1')


if __name__ == '__main__':
    main(*sys.argv[1:3])
