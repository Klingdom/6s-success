"""Drawing primitives for ops/build_room_maps.py: house palette, walls, doors,
and the furniture each zone actually is, drawn plainly enough to recognise.

No text is drawn here except small italic notes, and no six-S hue is used:
those colours mean a pass of the method and are not spent on furniture
(PLAN-VISUAL-STRATEGY.md section 8).
"""
import math

PAPER = "#F7F2E9"
FLOOR = "#EFE7D6"
CARD = "#FBF7EF"
INK = "#2B2622"
SLATE = "#33474F"
SOFT = "#6A625A"
LINE = "#D9CDB8"
WOOD = "#E3CFA9"
STEEL = "#D6D3CC"
FABRIC = "#D9C9B0"
LEAF = "#B7B79A"
ZONE = "#9C8F7E"

SERIF = "Fraunces,Georgia,serif"
SANS = "Inter,sans-serif"


def f(v):
    return ("%.1f" % v).rstrip("0").rstrip(".")


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def rect(x, y, w, h, fill=CARD, stroke=INK, sw=2, rx=0, extra=""):
    return ('<rect x="%s" y="%s" width="%s" height="%s"%s fill="%s" '
            'stroke="%s" stroke-width="%s"%s/>'
            % (f(x), f(y), f(w), f(h), ' rx="%s"' % f(rx) if rx else "",
               fill, stroke, f(sw), extra))


def circle(cx, cy, r, fill=CARD, stroke=INK, sw=2):
    return ('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" '
            'stroke-width="%s"/>' % (f(cx), f(cy), f(r), fill, stroke, f(sw)))


def ellipse(cx, cy, rx, ry, fill=CARD, stroke=INK, sw=2):
    return ('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" stroke="%s" '
            'stroke-width="%s"/>' % (f(cx), f(cy), f(rx), f(ry), fill, stroke,
                                     f(sw)))


def line(x1, y1, x2, y2, stroke=INK, sw=2, dash=""):
    return ('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" '
            'stroke-width="%s"%s stroke-linecap="round"/>'
            % (f(x1), f(y1), f(x2), f(y2), stroke, f(sw),
               ' stroke-dasharray="%s"' % dash if dash else ""))


def path(d, fill="none", stroke=INK, sw=2, dash=""):
    return ('<path d="%s" fill="%s" stroke="%s" stroke-width="%s"%s '
            'stroke-linecap="round" stroke-linejoin="round"/>'
            % (d, fill, stroke, f(sw),
               ' stroke-dasharray="%s"' % dash if dash else ""))


def P(*pts, close=False):
    """Path data from points."""
    d = "M" + " L".join("%s %s" % (f(x), f(y)) for x, y in pts)
    return d + (" Z" if close else "")


def note(x, y, s, anchor="middle", size=13, fill=SOFT, italic=True):
    return ('<text x="%s" y="%s" text-anchor="%s" font-family="%s" '
            'font-size="%d"%s fill="%s">%s</text>'
            % (f(x), f(y), anchor, SANS, size,
               ' font-style="italic"' if italic else "", fill, esc(s)))


# ------------------------------------------------------------- architecture

def walls(x, y, w, h, gaps=(), sw=9, floor=FLOOR):
    """Room outline as thick ink walls with openings.

    gaps: (side, start, end), side in t/b/l/r, measured from the top or left
    end of that side.
    """
    sides = {"t": ((x, y), (x + w, y)), "b": ((x, y + h), (x + w, y + h)),
             "l": ((x, y), (x, y + h)), "r": ((x + w, y), (x + w, y + h))}
    out = [rect(x, y, w, h, fill=floor, stroke="none", sw=0)]
    for side, ((x1, y1), (x2, y2)) in sides.items():
        cuts = sorted((a, b) for s, a, b in gaps if s == side)
        horiz = y1 == y2
        length = (x2 - x1) if horiz else (y2 - y1)
        pos = 0
        for a, b in cuts + [(length, length)]:
            if a > pos:
                if horiz:
                    out.append(line(x1 + pos, y1, x1 + a, y1, sw=sw))
                else:
                    out.append(line(x1, y1 + pos, x1, y1 + a, sw=sw))
            pos = b
    return "".join(out)


def door(hx, hy, length, leaf, swing):
    """A door drawn standing open toward swing, closing onto leaf.

    Both are unit vectors (dx, dy). The dashed arc runs from the tip of the
    open leaf to where that tip sits when the door is shut.
    """
    ox, oy = hx + swing[0] * length, hy + swing[1] * length
    cx, cy = hx + leaf[0] * length, hy + leaf[1] * length
    cross = swing[0] * leaf[1] - swing[1] * leaf[0]
    sweep = 1 if cross > 0 else 0
    return (line(hx, hy, ox, oy, sw=2.5)
            + path("M%s %s A%s %s 0 0 %d %s %s"
                   % (f(ox), f(oy), f(length), f(length), sweep, f(cx), f(cy)),
                   stroke=SOFT, sw=1.4, dash="4 4"))


def window(x1, y1, x2, y2):
    horiz = y1 == y2
    out = [line(x1, y1, x2, y2, stroke=PAPER, sw=10)]
    for o in (-3.5, 0, 3.5):
        out.append(line(x1, y1 + o, x2, y2 + o, sw=1.2) if horiz
                   else line(x1 + o, y1, x2 + o, y2, sw=1.2))
    return "".join(out)


def zone(x, y, w, h):
    return ('<rect x="%s" y="%s" width="%s" height="%s" rx="10" '
            'fill="#E2D6BF" fill-opacity="0.32" stroke="%s" '
            'stroke-width="1.6" stroke-dasharray="7 5"/>'
            % (f(x), f(y), f(w), f(h), ZONE))


# ---------------------------------------------------------------- furniture

def shelf(x, y, w, h, items="bins", n=None, vertical=None, fill=CARD):
    out = [rect(x, y, w, h, fill=fill)]
    vertical = (h > w) if vertical is None else vertical
    span = h if vertical else w
    n = n or max(2, int(span // 26))
    step = span / n
    for i in range(n):
        if vertical:
            cx, cy, cw, ch = x + w / 2, y + step * (i + 0.5), w - 10, step - 6
        else:
            cx, cy, cw, ch = x + step * (i + 0.5), y + h / 2, step - 6, h - 10
        if items == "bins":
            out.append(rect(cx - cw / 2, cy - ch / 2, cw, ch, fill=FABRIC,
                            sw=1.3, rx=3))
        elif items == "bottles":
            r = max(min(cw, ch) / 2 - 1, 3)
            out.append(circle(cx, cy, r, fill=STEEL, sw=1.3))
            out.append(circle(cx, cy, max(r / 2.6, 1.5), fill=INK, sw=0))
        elif items == "books":
            out.append(line(x + 4, cy, x + w - 4, cy, sw=1.2) if vertical
                       else line(cx, y + 4, cx, y + h - 4, sw=1.2))
        elif items == "stacks":
            out.append(rect(cx - cw / 2, cy - ch / 2, cw, ch, fill=PAPER,
                            sw=1.3, rx=2))
            out.append(line(cx - cw / 2 + 3, cy, cx + cw / 2 - 3, cy, sw=1)
                       if not vertical else
                       line(cx, cy - ch / 2 + 3, cx, cy + ch / 2 - 3, sw=1))
        elif items == "drawers":
            out.append(rect(cx - cw / 2, cy - ch / 2, cw, ch, fill=STEEL,
                            sw=1.2, rx=1))
            out.append(line(cx - 5, cy, cx + 5, cy, sw=1.6) if vertical
                       else line(cx, cy - 4, cx, cy + 4, sw=1.6))
        elif items == "rolls":
            r = max(min(cw, ch) / 2 - 1, 3)
            out.append(circle(cx, cy, r, fill=PAPER, sw=1.3))
            out.append(circle(cx, cy, r / 2.8, fill=STEEL, sw=1))
    return "".join(out)


def bench(x, y, w, h):
    return (rect(x, y, w, h, fill=WOOD)
            + rect(x + w - 34, y + h - 4, 26, 15, fill=STEEL, sw=1.6)
            + rect(x + 18, y + 14, w * 0.38, h - 28, fill=CARD, sw=1.3)
            + line(x + 4, y + 7, x + w - 4, y + 7, stroke=SOFT, sw=1))


def pegboard(x, y, w, h=18, vertical=False):
    """A tool wall seen edge-on: a strip with tools hung along it."""
    out = [rect(x, y, w, h, fill=STEEL, sw=1.5)]
    span = h if vertical else w
    i, t = 0, 14
    while t < span - 10:
        k = i % 3
        if vertical:
            c, a0, a1 = y + t, x + 3, x + w - 3
            seg = lambda p, q, s: line(p, c, q, c, sw=s)
            tick = lambda p, s: line(p, c - 4, p, c + 4, sw=s)
            dot = lambda p: circle(p, c, 2.6, fill=STEEL, sw=1.5)
        else:
            c, a0, a1 = x + t, y + 3, y + h - 3
            seg = lambda p, q, s: line(c, p, c, q, sw=s)
            tick = lambda p, s: line(c - 4, p, c + 4, p, sw=s)
            dot = lambda p: circle(c, p, 2.6, fill=STEEL, sw=1.5)
        if k == 0:        # hammer
            out.append(seg(a0, a1, 2) + tick(a0 + 1, 3))
        elif k == 1:      # wrench
            out.append(seg(a0 + 5, a1, 2) + dot(a0 + 3))
        else:             # screwdriver
            out.append(seg(a0, a0 + 6, 3.4) + seg(a0 + 6, a1, 1.3))
        i += 1
        t += 15
    return "".join(out)


def car(x, y, w, h):
    r = w * 0.3
    wheels = "".join(rect(xx, y + h * fy, 8, 24, fill=INK, sw=0, rx=2)
                     for xx in (x - 4, x + w - 4) for fy in (0.15, 0.73))
    glass = lambda a, b, c, d: path(
        "M%s %s Q%s %s %s %s L%s %s Q%s %s %s %s Z"
        % (f(x + a), f(y + h * b), f(x + w / 2), f(y + h * c), f(x + w - a),
           f(y + h * b), f(x + w - (28 - a)), f(y + h * d), f(x + w / 2),
           f(y + h * (d - 0.03 if c < b else d + 0.03)), f(x + 28 - a),
           f(y + h * d)), fill=STEEL, sw=1.5)
    return (wheels + rect(x, y, w, h, fill=CARD, rx=r)
            + glass(12, 0.34, 0.27, 0.45)
            + rect(x + 16, y + h * 0.47, w - 32, h * 0.27, fill=CARD, sw=1.3,
                   rx=8)
            + glass(16, 0.76, 0.79, 0.85))


def bike(x, y, s=1.0):
    r = 13 * s
    return (circle(x, y, r, fill="none", sw=1.8)
            + circle(x + 44 * s, y, r, fill="none", sw=1.8)
            + path(P((x, y), (x + 16 * s, y - 16 * s), (x + 36 * s, y - 16 * s),
                     (x + 22 * s, y), close=True) + " "
                   + P((x + 36 * s, y - 16 * s), (x + 44 * s, y)), sw=1.8)
            + line(x + 14 * s, y - 20 * s, x + 20 * s, y - 20 * s, sw=2.4))


def mower(x, y):
    return (rect(x, y, 46, 40, fill=STEEL, rx=6)
            + circle(x + 23, y + 20, 12, fill=CARD, sw=1.5)
            + path(P((x + 6, y + 40), (x + 6, y + 68), (x + 40, y + 68),
                     (x + 40, y + 40)), sw=2.2))


def long_tools(x, y, n=4, length=86):
    out = []
    for i in range(n):
        cx = x + i * 14
        out.append(line(cx, y, cx, y + length, sw=2.2))
        if i % 2:
            out.append(path(P((cx - 6, y + length), (cx + 6, y + length),
                              (cx, y + length + 12), close=True),
                            fill=STEEL, sw=1.5))
        else:
            out.append(line(cx - 7, y + length, cx + 7, y + length, sw=3))
    return "".join(out)


def ball(x, y, r=9):
    return (circle(x, y, r, fill=CARD, sw=1.6)
            + path("M%s %s Q%s %s %s %s" % (f(x - r), f(y), f(x), f(y - r / 2),
                                            f(x + r), f(y)), sw=1.1))


def toilet(x, y, wall="t"):
    """Toilet from above with its tank against wall t, l or r."""
    if wall == "t":
        return (rect(x - 22, y, 44, 16, fill=CARD, rx=3)
                + ellipse(x, y + 40, 18, 25)
                + ellipse(x, y + 42, 10, 15, fill=FLOOR, sw=1.3))
    if wall == "l":
        return (rect(x, y - 22, 16, 44, fill=CARD, rx=3)
                + ellipse(x + 40, y, 25, 18)
                + ellipse(x + 42, y, 15, 10, fill=FLOOR, sw=1.3))
    return (rect(x - 16, y - 22, 16, 44, fill=CARD, rx=3)
            + ellipse(x - 40, y, 25, 18)
            + ellipse(x - 42, y, 15, 10, fill=FLOOR, sw=1.3))


def vanity(x, y, w, h, basins=1, wall="t"):
    out = [rect(x, y, w, h, fill=CARD)]
    for i in range(basins):
        if wall == "t":
            cx = x + w * (i + 1) / (basins + 1)
            out.append(ellipse(cx, y + h * 0.56, 22, h * 0.27, fill=PAPER,
                               sw=1.5))
            out.append(circle(cx, y + 9, 3, fill=INK, sw=0))
        else:
            cy = y + h * (i + 1) / (basins + 1)
            ex = x + w * (0.56 if wall == "l" else 0.44)
            out.append(ellipse(ex, cy, w * 0.27, 22, fill=PAPER, sw=1.5))
            out.append(circle(x + 9 if wall == "l" else x + w - 9, cy, 3,
                              fill=INK, sw=0))
    return "".join(out)


def tub(x, y, w, h):
    return (rect(x, y, w, h, fill=CARD, rx=6)
            + rect(x + 9, y + 9, w - 18, h - 18, fill=PAPER, rx=18, sw=1.5)
            + circle(x + w - 26, y + h / 2, 4, fill=INK, sw=0))


def shower(x, y, w, h):
    return (rect(x, y, w, h, fill=PAPER)
            + line(x, y, x + w, y + h, stroke=LINE, sw=1.4)
            + line(x + w, y, x, y + h, stroke=LINE, sw=1.4)
            + circle(x + w / 2, y + h / 2, 5, fill=INK, sw=0))


def towels(x, y, w, h, n=4):
    out = [rect(x, y, w, h, fill=CARD)]
    horiz = w >= h
    step = (w if horiz else h) / n
    for i in range(n):
        if horiz:
            out.append(rect(x + i * step + 4, y + 5, step - 8, h - 10,
                            fill=FABRIC, sw=1.2, rx=3))
            out.append(line(x + i * step + 7, y + h / 2,
                            x + (i + 1) * step - 7, y + h / 2, sw=1))
        else:
            out.append(rect(x + 5, y + i * step + 4, w - 10, step - 8,
                            fill=FABRIC, sw=1.2, rx=3))
            out.append(line(x + w / 2, y + i * step + 7, x + w / 2,
                            y + (i + 1) * step - 7, sw=1))
    return "".join(out)


def washer(x, y, s=62):
    return (rect(x, y, s, s, fill=CARD, rx=5)
            + line(x + 4, y + 12, x + s - 4, y + 12, sw=1.2)
            + circle(x + s - 12, y + 6, 2.5, fill=INK, sw=0)
            + circle(x + s / 2, y + s / 2 + 5, s * 0.3, fill=PAPER, sw=1.6)
            + circle(x + s / 2, y + s / 2 + 5, s * 0.17, fill=STEEL, sw=1.2))


def basket(x, y, r=20, fill=FABRIC):
    return (circle(x, y, r, fill=fill, sw=1.8)
            + circle(x, y, r - 6, fill="none", stroke=SOFT, sw=1))


def drying_rack(x, y, w, h):
    out = [rect(x, y, w, h, fill="none", sw=2)]
    for i in range(1, 6):
        out.append(line(x + 4, y + h * i / 6, x + w - 4, y + h * i / 6,
                        stroke=SOFT, sw=1.3))
    out.append(rect(x + 10, y + h * 0.18, w * 0.4, h * 0.22, fill=FABRIC,
                    sw=1.2, rx=2))
    out.append(rect(x + w * 0.5, y + h * 0.52, w * 0.36, h * 0.2, fill=FABRIC,
                    sw=1.2, rx=2))
    return "".join(out)


def desk(x, y, w, h):
    return (rect(x, y, w, h, fill=WOOD)
            + rect(x + w * 0.3, y + 8, w * 0.4, h * 0.42, fill=STEEL, sw=1.5,
                   rx=3)
            + rect(x + w * 0.34, y + h * 0.58, w * 0.32, h * 0.22, fill=CARD,
                   sw=1.2, rx=2)
            + rect(x + w - 40, y + 14, 26, 20, fill=PAPER, sw=1.2))


def chair(cx, cy, r=18, back="d"):
    """Desk chair from above, backrest on side back."""
    a = {"d": (0, 1), "u": (0, -1), "l": (-1, 0), "r": (1, 0)}[back]
    bx, by = cx + a[0] * (r + 3), cy + a[1] * (r + 3)
    bar = (line(bx - r, by, bx + r, by, sw=4) if a[1]
           else line(bx, by - r, bx, by + r, sw=4))
    return circle(cx, cy, r, fill=FABRIC, sw=1.8) + bar


def printer(x, y, w=64, h=44):
    return (rect(x, y + 10, w, h, fill=STEEL, rx=4)
            + rect(x + 10, y, w - 20, 12, fill=PAPER, sw=1.3)
            + rect(x + 8, y + h - 2, w - 16, 7, fill=CARD, sw=1.1))


def crib(x, y, w, h):
    out = [rect(x, y, w, h, fill=CARD, sw=2.5),
           rect(x + 8, y + 8, w - 16, h - 16, fill=PAPER, sw=1.2)]
    for i in range(1, 12):
        xx = x + w * i / 12
        out.append(line(xx, y, xx, y + 7, sw=1.3))
        out.append(line(xx, y + h - 7, xx, y + h, sw=1.3))
    return "".join(out)


def glider(cx, cy):
    return (rect(cx - 30, cy - 28, 60, 56, fill=FABRIC, rx=12)
            + rect(cx - 20, cy - 14, 40, 36, fill=CARD, sw=1.3, rx=8)
            + line(cx - 34, cy + 34, cx + 34, cy + 34, stroke=SOFT, sw=2))


def sofa(x, y, w, h):
    """A sofa from above, backrest along its bottom edge so it faces up the
    page, toward whatever the plan puts in front of it."""
    return (rect(x, y, w, h, fill=FABRIC, rx=8)
            + rect(x + 10, y + 4, w - 20, h - 16, fill=CARD, sw=1.3, rx=6)
            + line(x + w / 2, y + 4, x + w / 2, y + h - 12, stroke=SOFT,
                   sw=1.2))


def armchair(cx, cy, s=44):
    return (rect(cx - s / 2, cy - s / 2, s, s, fill=FABRIC, rx=8)
            + rect(cx - s / 2 + 8, cy - s / 2 + 10, s - 16, s - 14, fill=CARD,
                   sw=1.3, rx=5))


def round_table(cx, cy, r, chairs=4):
    out = []
    for i in range(chairs):
        a = 2 * math.pi * i / chairs + math.pi / 4
        out.append(rect(cx + (r + 14) * math.cos(a) - 12,
                        cy + (r + 14) * math.sin(a) - 12, 24, 24,
                        fill=FABRIC, sw=1.5, rx=5))
    out.append(circle(cx, cy, r, fill=WOOD))
    return "".join(out)


def grill(cx, cy, r=26):
    out = [circle(cx, cy, r, fill=STEEL, sw=2.2),
           circle(cx, cy, r - 6, fill=INK, sw=0)]
    for i in (-2, -1, 0, 1, 2):
        out.append(line(cx - r + 9, cy + i * 6, cx + r - 9, cy + i * 6,
                        stroke=STEEL, sw=1.3))
    return "".join(out)


def planter(cx, cy, r=16):
    return (circle(cx, cy, r, fill=WOOD, sw=1.8)
            + circle(cx - r * 0.3, cy - r * 0.2, r * 0.45, fill=LEAF, sw=1.1)
            + circle(cx + r * 0.32, cy + r * 0.15, r * 0.42, fill=LEAF, sw=1.1)
            + circle(cx, cy + r * 0.38, r * 0.3, fill=LEAF, sw=1.1))


def deck_box(x, y, w, h):
    return (rect(x, y, w, h, fill=WOOD, rx=4)
            + line(x + 5, y + h * 0.3, x + w - 5, y + h * 0.3, sw=1.4)
            + rect(x + w / 2 - 9, y + h * 0.3 - 4, 18, 8, fill=STEEL, sw=1.2))


def coat(cx, cy, d=(0, 1)):
    """A coat hanging from a hook at (cx, cy), falling in direction d."""
    dx, dy = d
    px, py = -dy, dx            # perpendicular, for the coat width

    def pt(a, b):               # a along the fall, b across it
        return f(cx + dx * a + px * b), f(cy + dy * a + py * b)
    return path("M%s %s Q%s %s %s %s Q%s %s %s %s Z"
                % (pt(6, -9) + pt(22, -14) + pt(34, -7) + pt(22, 14)
                   + pt(6, 9)), fill=FABRIC, sw=1.3)


def hooks_row(x1, x2, y, n, down=True):
    out = []
    d = (0, 1) if down else (0, -1)
    for i in range(n):
        cx = x1 + (x2 - x1) * (i + 0.5) / n
        out.append(circle(cx, y + d[1] * 3, 3.4, fill=INK, sw=0))
        if i % 3 != 2:
            out.append(coat(cx, y, d))
    return "".join(out)


def hooks_col(x, y1, y2, n, right=True):
    out = []
    d = (1, 0) if right else (-1, 0)
    for i in range(n):
        cy = y1 + (y2 - y1) * (i + 0.5) / n
        out.append(circle(x + d[0] * 3, cy, 3.4, fill=INK, sw=0))
        if i % 3 != 2:
            out.append(coat(x, cy, d))
    return "".join(out)


def shoe_pairs(x, y, w, h, pairs=4):
    out = [rect(x, y, w, h, fill=CARD)]
    horiz = w >= h
    step = (w if horiz else h) / pairs
    for i in range(pairs):
        c = (x if horiz else y) + step * (i + 0.5)
        for o in (-6, 6):
            if horiz:
                out.append(ellipse(c + o, y + h / 2, 4.6, h * 0.32,
                                   fill=FABRIC, sw=1.2))
            else:
                out.append(ellipse(x + w / 2, c + o, w * 0.32, 4.6,
                                   fill=FABRIC, sw=1.2))
    return "".join(out)


def pet_station(x, y):
    return (rect(x, y, 84, 46, fill=FABRIC, rx=8, sw=1.6)
            + circle(x + 24, y + 23, 13, fill=STEEL, sw=1.6)
            + circle(x + 24, y + 23, 7, fill=PAPER, sw=1)
            + circle(x + 60, y + 23, 13, fill=STEEL, sw=1.6)
            + circle(x + 60, y + 23, 7, fill=SLATE, sw=0))


def mat(x, y, w, h):
    out = [rect(x, y, w, h, fill=FABRIC, rx=4, sw=1.6)]
    for i in range(1, 6):
        out.append(line(x + w * i / 6, y + 4, x + w * i / 6, y + h - 4,
                        stroke=SOFT, sw=1))
    return "".join(out)


def bench_seat(x, y, w, h):
    return (rect(x, y, w, h, fill=WOOD)
            + rect(x + 8, y + 6, w - 16, h - 12, fill=FABRIC, sw=1.3, rx=5))


def bucket_top(cx, cy, r=14):
    return (circle(cx, cy, r, fill=STEEL, sw=1.8)
            + circle(cx, cy, r - 5, fill=PAPER, sw=1)
            + path("M%s %s Q%s %s %s %s" % (f(cx - r), f(cy), f(cx),
                                            f(cy - r - 8), f(cx + r), f(cy)),
                   sw=1.3))


def frames_on_wall(x1, x2, y, n, below=True):
    """Pictures on a wall, seen from above as thin slabs."""
    out = []
    w = (x2 - x1) / n
    for i in range(n):
        out.append(rect(x1 + i * w + 6, y if below else y - 8, w - 12, 8,
                        fill=WOOD, sw=1.4))
    return "".join(out)


def lamp(cx, cy, r=10):
    out = [circle(cx, cy, r, fill="#F3E3B8", sw=1.6),
           circle(cx, cy, 3, fill=INK, sw=0)]
    for k in range(8):
        a = k * math.pi / 4
        out.append(line(cx + (r + 3) * math.cos(a), cy + (r + 3) * math.sin(a),
                        cx + (r + 8) * math.cos(a), cy + (r + 8) * math.sin(a),
                        stroke=SOFT, sw=1.2))
    return "".join(out)


def stairs(x, y, w, h, treads, direction="u"):
    """A flight in plan: treads as lines, arrow pointing up the flight."""
    out = [rect(x, y, w, h, fill=CARD)]
    vert = direction in "ud"
    for i in range(1, treads):
        if vert:
            yy = y + h * i / treads
            out.append(line(x, yy, x + w, yy, sw=1.3))
        else:
            xx = x + w * i / treads
            out.append(line(xx, y, xx, y + h, sw=1.3))
    if direction == "u":
        ax = x + w / 2
        out.append(line(ax, y + h - 12, ax, y + 16, stroke=SLATE, sw=2))
        out.append(path(P((ax - 7, y + 27), (ax, y + 15), (ax + 7, y + 27)),
                        stroke=SLATE, sw=2))
        out.append(circle(ax, y + h - 12, 4, fill=SLATE, sw=0))
    else:
        ay = y + h / 2
        s, e = (x + 12, x + w - 15) if direction == "r" else (x + w - 12,
                                                              x + 15)
        k = 12 if direction == "r" else -12
        out.append(line(s, ay, e - (1 if direction == "r" else -1), ay,
                        stroke=SLATE, sw=2))
        out.append(path(P((e - k, ay - 7), (e, ay), (e - k, ay + 7)),
                        stroke=SLATE, sw=2))
        out.append(circle(s, ay, 4, fill=SLATE, sw=0))
    return "".join(out)


def rail(x1, y1, x2, y2, posts=8):
    out = [line(x1, y1, x2, y2, stroke=WOOD, sw=9),
           line(x1, y1, x2, y2, sw=1.4)]
    for i in range(posts + 1):
        t = i / posts
        cx, cy = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
        out.append(rect(cx - 5, cy - 5, 10, 10, fill=WOOD, sw=1.4))
    return "".join(out)


def boards(x, y, w, h, gap=18):
    out = []
    yy = y + gap
    while yy < y + h - 4:
        out.append(line(x + 3, yy, x + w - 3, yy, stroke="#D8C8A6", sw=1.2))
        yy += gap
    return "".join(out)


def lumber(x, y, w, n=5, gap=11):
    out = []
    for i in range(n):
        out.append(rect(x + (i % 2) * 14, y + i * gap,
                        w - (i % 3) * 30 - (i % 2) * 14, gap - 4,
                        fill=WOOD, sw=1.3, rx=1))
    return "".join(out)


def extinguisher(cx, cy):
    return (rect(cx - 7, cy - 16, 14, 32, fill="#E7B9AA", rx=6, sw=1.6)
            + line(cx, cy - 16, cx, cy - 22, sw=2.4)
            + line(cx, cy - 22, cx + 9, cy - 20, sw=2))


def goggles(cx, cy):
    return (ellipse(cx - 8, cy, 7, 5, fill=PAPER, sw=1.5)
            + ellipse(cx + 8, cy, 7, 5, fill=PAPER, sw=1.5)
            + line(cx - 1, cy, cx + 1, cy, sw=1.5))


def earmuffs(cx, cy):
    return (path("M%s %s A9 9 0 0 1 %s %s" % (f(cx - 9), f(cy), f(cx + 9),
                                               f(cy)), sw=2)
            + ellipse(cx - 9, cy + 3, 4, 6, fill=SLATE, sw=0)
            + ellipse(cx + 9, cy + 3, 4, 6, fill=SLATE, sw=0))
