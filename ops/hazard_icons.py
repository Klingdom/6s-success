#!/usr/bin/env python3
"""
Five hazard icons, covering all 114 micro zones.

THE FINDING THAT MADE THIS CHEAP
--------------------------------
ops/build_image_prompts.py generated a bespoke AI safety illustration prompt for
every zone that has a hazard, which is all of them. That is 114 images to
generate, review and keep consistent.

Counted against content.json, the 114 zones contain exactly FIVE distinct hazard
categories:

    87  Fall, cut, or crush
    53  Poison, choke, or strangle
    51  Fall
    33  Burn or fire
    27  Water and electricity

So the real number of shapes needed is five, not 114. Drawn once, in SVG, from
the palette already in site.css, they cover every zone deterministically, cost
nothing per additional page, never drift when copy changes, and carry a real
accessible label instead of alt text describing a picture of a label.

WHY SVG AND NOT AN IMAGE FILE
-----------------------------
An icon that is code cannot go stale, cannot be the wrong size, inherits
currentColor so it works on any background this site has, and adds no network
request. The same reasoning already produced ops/build_icons.py for the brand
mark.

Run:  python ops/hazard_icons.py --check
"""
from __future__ import annotations

import json
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")

# Colour is carried by the category, not invented per zone. Spark is reserved
# for the sharpest hazards, honey for the rest, matching how the rest of the
# site uses those two.
SPARK, HONEY, SLATE = "#CB4B36", "#DDA63A", "#3C5A6B"

# Keyed by the exact watch_for question string. A category that stops matching
# is caught by the assertion at the bottom rather than silently losing its icon.
ICONS = {
    "Fall, cut, or crush": (SPARK, "A falling object above an open hand",
        '<path d="M4 3h9l-1.6 5.2H5.6z" fill="none" stroke="currentColor" '
        'stroke-width="1.7" stroke-linejoin="round"/>'
        '<path d="M8.5 10.4v2.2" stroke="currentColor" stroke-width="1.7" '
        'stroke-linecap="round"/>'
        '<path d="M3.4 19.3c0-2.4 2.3-4.3 5.1-4.3s5.1 1.9 5.1 4.3" fill="none" '
        'stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>'
        '<path d="M16 6.5l3.6 3.6M19.6 6.5L16 10.1" stroke="currentColor" '
        'stroke-width="1.7" stroke-linecap="round"/>'),

    "Poison, choke, or strangle": (SPARK, "A bottle with a hazard mark",
        '<path d="M9.4 2.6h4.2v2.9l2.5 3.3v11a1.6 1.6 0 0 1-1.6 1.6H8.5A1.6 1.6 '
        '0 0 1 6.9 19.8v-11l2.5-3.3z" fill="none" stroke="currentColor" '
        'stroke-width="1.7" stroke-linejoin="round"/>'
        '<path d="M11.5 11.4v4.1" stroke="currentColor" stroke-width="1.8" '
        'stroke-linecap="round"/>'
        '<circle cx="11.5" cy="18.1" r="1" fill="currentColor"/>'),

    "Fall": (HONEY, "A figure losing footing on a step",
        '<path d="M3 20.4h6.4V16h5.2v-4.4H20" fill="none" stroke="currentColor" '
        'stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round"/>'
        '<circle cx="15.6" cy="5.1" r="2" fill="none" stroke="currentColor" '
        'stroke-width="1.7"/>'
        '<path d="M13.2 9.1l4.6 1.4M15.5 10v3.4" stroke="currentColor" '
        'stroke-width="1.7" stroke-linecap="round"/>'),

    "Burn or fire": (SPARK, "A flame",
        '<path d="M12 21.2c3.4 0 5.9-2.4 5.9-5.6 0-4.3-4.3-6.2-4-12.4-2.6 1.7-4.6 '
        '4.6-4.6 7.3 0 1.4.5 2.3.5 2.3s-1.6-.6-2.3-2.2c-.9 1.5-1.4 3.2-1.4 5 0 '
        '3.2 2.5 5.6 5.9 5.6z" fill="none" stroke="currentColor" '
        'stroke-width="1.7" stroke-linejoin="round"/>'),

    "Water and electricity": (SLATE, "A water drop beside a power bolt",
        '<path d="M7.4 3.2c2.6 3.2 4 5.3 4 7a4 4 0 1 1-8 0c0-1.7 1.4-3.8 4-7z" '
        'fill="none" stroke="currentColor" stroke-width="1.7" '
        'stroke-linejoin="round"/>'
        '<path d="M16.6 3.4l-3 7.1h3.6l-2.4 8.4 5.6-9.6h-3.6l2.2-5.9z" '
        'fill="none" stroke="currentColor" stroke-width="1.7" '
        'stroke-linejoin="round"/>'),
}


def icon(question: str) -> str:
    """Inline SVG for a hazard category, or empty for an unknown one.

    Empty rather than a fallback glyph on purpose: a generic warning triangle on
    a hazard nobody classified would look deliberate and mean nothing.
    """
    hit = ICONS.get((question or "").strip())
    if not hit:
        return ""
    colour, label, body = hit
    return (f'<svg class="hz" viewBox="0 0 24 24" role="img" '
            f'aria-label="{label}" style="color:{colour}" focusable="false">'
            f'{body}</svg>')


CSS = """
/* Hazard icons. Colour comes from the category, size from the text beside it,
   so they scale with the reader's font settings rather than being pinned. */
.hz{width:1.35em;height:1.35em;flex:0 0 auto;vertical-align:-.28em}
.hazard-list{list-style:none;margin:0;padding:0}
.hazard-list li{display:flex;gap:11px;align-items:flex-start;padding:9px 0;
  border-bottom:1px solid var(--line,#E2D8C4)}
.hazard-list li:last-child{border-bottom:0}
.hazard-list b{display:block;font-family:var(--sans);font-size:12px;
  font-weight:700;letter-spacing:.08em;text-transform:uppercase;
  color:var(--soft,#6A625A);margin-bottom:2px}
"""


def main() -> int:
    d = json.load(io.open(SRC, encoding="utf-8"))
    seen = {}
    for r in d["rooms"]:
        for z in r["zones"]:
            for w in (z.get("watch_for") or []):
                q = str(w.get("question", "")).strip()
                seen[q] = seen.get(q, 0) + 1

    print(f"  {len(seen)} distinct hazard categories across 114 zones")
    covered = 0
    for q, n in sorted(seen.items(), key=lambda x: -x[1]):
        has = "yes" if q in ICONS else "NO ICON"
        covered += n if q in ICONS else 0
        print(f"    {n:>4}  {q:<32} {has}")
    total = sum(seen.values())
    print(f"\n  {covered} of {total} hazard entries covered "
          f"({covered/total:.0%}) by {len(ICONS)} drawn icons")

    # If content grows a sixth category, that hazard silently loses its icon on
    # every page it appears. Fail here instead, while somebody is looking.
    missing = [q for q in seen if q not in ICONS]
    assert not missing, (
        f"hazard categories with no icon: {missing}. Draw one in ICONS or the "
        "hazard renders bare on every zone that carries it.")
    assert covered == total, "coverage should be total once nothing is missing"
    print("  every category has an icon")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
