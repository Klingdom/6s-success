#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_no_false_zone_order_claim() catches a page
claiming its zone list is "the order to work them" when the page's own
"Start here" notice says otherwise. The exact live shape found 2026-10-01
on 18 of 20 rooms, 114 zone pages, resources.html, the printable Micro
Zone Map and two hand-authored articles; the card decks' own ROOM CARD
objective text stated outright "This card is the map and the order."

Run:  python ops/tests/test_gate_no_false_zone_order_claim.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

PASS, FAILCOUNT = 0, 0


def check(name, condition):
    global PASS, FAILCOUNT
    if condition:
        PASS += 1
    else:
        FAILCOUNT += 1
        print(f"  FAIL: {name}")


def run_gate_against(files: dict) -> list:
    """files: {relative_path: html_text}. Writes them into a scratch site/
    directory, points preflight.SITE at it, runs the real gate, restores."""
    tmpdir = tempfile.mkdtemp()
    scratch_site = os.path.join(tmpdir, "site")
    os.makedirs(scratch_site)
    for rel, html in files.items():
        full = os.path.join(scratch_site, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        io.open(full, "w", encoding="utf-8").write(html)
    real_site = preflight.SITE
    try:
        preflight.SITE = scratch_site
        preflight.FAIL.clear()
        preflight.gate_no_false_zone_order_claim()
        return list(preflight.FAIL)
    finally:
        preflight.SITE = real_site
        shutil.rmtree(tmpdir)


def main():
    # 1. An honest page, no ordering claim. Must pass.
    honest = ('<html><body><h2>The 6 micro zones</h2>'
              '<p class="notice"><b>Start here.</b> Do the floor first.</p>'
              '</body></html>')
    fails = run_gate_against({"rooms/living-room.html": honest})
    check("an honest page passes", fails == [])

    # 2. The exact live regression: "in working order" heading immediately
    # above a "Start here" notice naming a different zone. Must fail,
    # naming the file and the phrase.
    broken = ('<html><body><h2>The 6 micro zones, in working order</h2>'
               '<p class="notice"><b>Start here.</b> Do the floor first, '
               'not the sofa.</p></body></html>')
    fails = run_gate_against({"rooms/living-room.html": broken})
    msg = " ".join(m for _, m in fails)
    check("the regression is caught", "in working order" in msg)
    check("the broken file is named", "living-room.html" in msg)

    # 3. The zone-page sibling-list shape and the figcaption/meta-description
    # shape must each be caught independently.
    fails = run_gate_against({
        "zones/a.html": "<h2>The rest of the kitchen, in working order</h2>",
        "b.html": '<meta name="description" content="worth its own hour, '
                  'in the order to work them.">',
    })
    check("both pages are named",
          all(n in " ".join(m for _, m in fails) for n in ("a.html", "b.html")))

    # 4. The card-deck shape: "This card is the map and the order."
    fails = run_gate_against({"kitchen-deck.html": "This card is the map and the order."})
    check("the card-deck phrasing is caught",
          any("kitchen-deck.html" in m for _, m in fails))

    # 5. consulting.html is the one legitimate survivor: a real, paid,
    # human-determined deliverable, not a template describing a fixed list.
    # Must never be flagged even though it carries the same words.
    fails = run_gate_against({
        "consulting.html": "<p>the zones in the order to work them</p>",
    })
    check("consulting.html is excused", fails == [])

    print(f"\n{PASS} passed, {FAILCOUNT} failed")
    return 1 if FAILCOUNT else 0


if __name__ == "__main__":
    sys.exit(main())
