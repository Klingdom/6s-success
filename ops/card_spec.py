#!/usr/bin/env python3
"""
The print specification for a 6S Success card. One source of truth.

WHY THIS FILE EXISTS
--------------------
The cards were laid out in CSS pixels by somebody thinking in screen pixels,
on a canvas that is not a screen. The canvas is 750 x 1050, which is 2.5 x 3.5
inches at 300 dpi, so a CSS pixel on this canvas is 1/300 of a printed inch and
one printed point is 4.1667 of them.

Body copy was set at 8.5px to 13.5px. That is 2.0pt to 3.2pt on the card in a
person's hand, against a print floor of about 6 to 7pt. The deck was not
slightly tight, it was unreadable, and nothing in the pipeline could say so
because every size was written as a bare number with no unit attached to a
physical thing.

So sizes are declared here in POINTS and converted once. Nothing downstream is
allowed to invent a px value.

THE RULE
--------
    FLOOR_PT      7.0   nothing printed on a card is smaller than this
    BODY_MIN_PT   8.5   anything that is a sentence a person reads

If content does not fit at those sizes, the content is too long for a 2.5 by
3.5 inch card and gets cut or moved to the back. A card that cannot be read is
worth less than a card that says less. Shrinking type to make text fit is
forbidden here, which is the mistake this file exists to prevent recurring.

BLEED AND SAFE AREA
-------------------
A printed card is cut with a tolerance of roughly a sixteenth of an inch, and
these have rounded corners, so:

    TRIM     750 x 1050    2.50 x 3.50 in    the finished card
    BLEED    825 x 1125    2.75 x 3.75 in    trim plus 0.125 in on every side
    SAFE     654 x  954    inset 0.16 in from trim, where all text must live
    RADIUS   37.5 px       0.125 in, a real poker-card corner

Backgrounds and photographs run to the bleed edge. Text never leaves SAFE.
"""
from __future__ import annotations

# ---------------------------------------------------------------- geometry
DPI = 300
PX_PER_PT = DPI / 72.0                       # 4.166666...

CARD_W, CARD_H = 750, 1050                   # trim, 2.5 x 3.5 in
BLEED_PX = int(round(0.125 * DPI))           # 37.5 -> 37 px each side
BLEED_W, BLEED_H = CARD_W + 2 * BLEED_PX, CARD_H + 2 * BLEED_PX
SAFE_INSET = 48                              # 0.16 in from trim
CORNER_R = 37                                # 0.125 in
SAFE_W = CARD_W - 2 * SAFE_INSET             # 654
SAFE_H = CARD_H - 2 * SAFE_INSET             # 954


def pt(points: float) -> float:
    """Points to canvas pixels at 300 dpi. The only legal way to get a size."""
    return round(points * PX_PER_PT, 2)


# ------------------------------------------------------------- type scale
FLOOR_PT = 7.0        # absolute minimum for any printed glyph
BODY_MIN_PT = 8.5     # minimum for running sentences

SCALE_PT = {
    "display":   27.0,   # card title, one line
    "display2":  21.0,   # card title, two lines or a long name
    "id":        11.0,   # the card code in the band
    "kind":       8.0,   # the family word in the band
    "lead":      10.0,   # tagline under the title
    "body":       9.5,   # front action copy
    "body_sm":    8.5,   # back list copy  (== BODY_MIN_PT)
    "label":      7.5,   # eyebrow labels over a block
    "micro":      7.0,   # footer meta     (== FLOOR_PT)
}
assert min(SCALE_PT.values()) >= FLOOR_PT, "a scale token is below the floor"

SCALE_PX = {k: pt(v) for k, v in SCALE_PT.items()}


# ------------------------------------------------------------------ colour
# The six-S palette, identical to ops/video_zone.py. One brand, one set of
# hues; the cards do not get their own.
INK, PAPER, LINE = "#2B2622", "#F7F2E9", "#E2D8C4"
DEEP, BRONZE = "#22323C", "#B07A18"

SIX_S = {
    "Sort":        "#BC4B2A",
    "Straighten":  "#DDA63A",
    "Shine":       "#4E7A57",
    "Safety":      "#CB4B36",
    "Standardize": "#3C5A6B",
    "Sustain":     "#6E5B8B",
}

# Card family -> (colour, glyph, hue it borrows).
#
# There are eight playing families and six brand hues, so two families take a
# documented deep shade of a palette member rather than a ninth invented
# colour. Colour alone would not be enough anyway: the glyph carries the same
# distinction, because a player who cannot separate the gold from the bronze
# across a table can still separate an arrow from a star, and because meaning
# carried by colour alone fails for a colour-blind player.
FAMILY = {
    "Micro Zone":   ("#3C5A6B", "▣", "Standardize"),   # square in square
    "Problem":      ("#CB4B36", "▲", "Safety"),        # warning triangle
    "Event":        ("#BC4B2A", "◆", "Sort"),          # diamond
    "Upgrade":      ("#DDA63A", "▴", "Straighten"),    # up
    "Habit":        ("#4E7A57", "●", "Shine"),         # circle
    "Skill":        ("#6E5B8B", "✦", "Sustain"),       # spark
    "Tool":         (DEEP,      "▬", "Standardize deep"),
    "Win / Reward": (BRONZE,    "★", "Straighten deep"),
    "Win":          (BRONZE,    "★", "Straighten deep"),
    "Room":         (INK,       "⌂", "Ink"),
}


def _lum(hexcol: str) -> float:
    """WCAG relative luminance."""
    c = hexcol.lstrip("#")
    out = []
    for i in (0, 2, 4):
        v = int(c[i:i + 2], 16) / 255.0
        out.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * out[0] + 0.7152 * out[1] + 0.0722 * out[2]


def contrast(a: str, b: str) -> float:
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def on(colour: str) -> str:
    """Legible foreground for a band of this colour.

    Straighten gold is light. Paper text on it lands near 2:1 and prints as a
    smear, which is exactly the class of fault this rebuild is about, so the
    foreground is computed rather than assumed to be paper.
    """
    return PAPER if contrast(colour, PAPER) >= contrast(colour, INK) else INK


def readable_on(colour: str, ground: str = PAPER, target: float = 4.5) -> str:
    """Darken a family colour until it is legible as TEXT on paper.

    Straighten gold reads at 1.9:1 on cream. Setting a label in the raw family
    colour is how "on brand" quietly becomes "cannot be read", which is the
    same failure as 2pt type wearing a different hat. So the hue is kept and
    the value is walked toward ink until it clears the target.
    """
    r0, g0, b0 = (int(colour.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    r1, g1, b1 = (int(INK.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    for step in range(0, 21):
        k = step / 20.0
        c = "#%02X%02X%02X" % (round(r0 + (r1 - r0) * k),
                               round(g0 + (g1 - g0) * k),
                               round(b0 + (b1 - b0) * k))
        if contrast(c, ground) >= target:
            return c
    return INK


def family_of(type_string: str) -> str:
    """'EVENT CARD' -> 'Event'. Unknown families fall back to Room ink."""
    t = (type_string or "").upper().replace(" CARD", "").strip()
    for k in FAMILY:
        if k.upper() == t:
            return k
    return "Room"


if __name__ == "__main__":
    print(f"  {DPI} dpi, 1pt = {PX_PER_PT:.4f}px")
    print(f"  trim {CARD_W}x{CARD_H}  bleed {BLEED_W}x{BLEED_H}  "
          f"safe {SAFE_W}x{SAFE_H}  radius {CORNER_R}px")
    print(f"\n  {'token':10} {'pt':>6} {'px':>8}")
    for k, v in sorted(SCALE_PT.items(), key=lambda x: -x[1]):
        print(f"  {k:10} {v:6.1f} {pt(v):8.1f}")
    print(f"\n  floor {FLOOR_PT}pt, body minimum {BODY_MIN_PT}pt")
    print(f"\n  {'family':14} {'colour':9} {'hue':18} {'fg':9} contrast")
    for k, (col, _g, hue) in FAMILY.items():
        fg = on(col)
        print(f"  {k:14} {col:9} {hue:18} {fg:9} {contrast(col, fg):.2f}:1")
