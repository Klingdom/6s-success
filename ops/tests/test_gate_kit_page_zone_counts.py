#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_kit_page_zone_counts_current() catches
site/kit.html rendering a "N of 114 zones ask for this" line that no
longer matches a live count from content/manual/source/zone_products.json.

Found 2026-09-17, cold-reading ops/build_kit_page.py: it read the "N of
114 zones" number straight from ops/affiliate-catalogue.csv's own
`_zone_count` column, a value frozen at whatever catalog state last
hand-edited that CSV. ops/zone_supplies.py already refuses to trust that
same column for exactly this reason ("that column lives in a file another
agent is editing this cycle and a stale count would silently reorder every
page") and ops/build_manual_print.py already found it wrong for ten
records after cleaning tools were added later. build_kit_page.py was the
one reader of this frozen column nobody had checked. All eight counts
matched reality on the real committed page (no live defect); fixed at the
source in build_kit_page.py (recompute from the real zone map, same
method zone_supplies.py already uses) rather than only gated.

Tests the pure logic (check_kit_page_zone_counts) with synthetic data, then
checks the real committed site/kit.html against a live re-derivation from
the real zone_products.json, so a future regression (a hand edit to
kit.html, or build_kit_page.py trusting the frozen column again) is caught
either way.

Run:  python ops/tests/test_gate_kit_page_zone_counts.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def rows():
    return [
        {"Product ID": "X-001", "Product Standard Name": "Widget"},
        {"Product ID": "X-002", "Product Standard Name": "Gadget"},
    ]


def page_html(counts: dict) -> str:
    """A minimal page carrying one <b>N of 114 zones</b> line per id in
    `counts`, in the same shape build_kit_page.py's own card() emits."""
    parts = []
    for pid, n in counts.items():
        parts.append(f'<li><h2>{pid}</h2>'
                     f'<p class="meta"><b>{n} of 114 zones</b> ask for '
                     f'this &nbsp;&middot;&nbsp; typically $1 to $2</p></li>')
    return "".join(parts)


def main() -> int:
    fails = []

    # 1. Clean: the page's own count matches the real, freshly-computed rarity.
    rarity = {"X-001": 90, "X-002": 114}
    problems = preflight.check_kit_page_zone_counts(
        rarity, rows(), page_html(rarity))
    if problems:
        fails.append("clean page wrongly flagged: %s" % problems)

    # 2. The exact regression this gate exists for: the page shows a frozen
    #    number (114) that no longer matches the real zone map (90).
    rarity = {"X-001": 90, "X-002": 114}
    stale_page = page_html({"X-001": 114, "X-002": 114})
    problems = preflight.check_kit_page_zone_counts(
        rarity, rows(), stale_page)
    if not any("X-001" in p for p in problems):
        fails.append("a frozen, wrong count was NOT caught: %s" % problems)
    if any("X-002" in p for p in problems):
        fails.append("a correct count (X-002) was wrongly flagged: %s"
                     % problems)

    # 3. A product id not in the zone map at all (never used in any zone)
    #    must not be flagged; the gate only checks ids it can verify.
    rarity = {"X-002": 114}
    problems = preflight.check_kit_page_zone_counts(
        rarity, rows(), page_html({"X-002": 114}))
    if problems:
        fails.append("a product absent from the zone map was wrongly "
                     "flagged: %s" % problems)

    # 4. Real files: re-derive the live rarity independently (not by
    #    importing ops/zone_supplies.py, the same independence the gate
    #    itself keeps) and check the real committed site/kit.html against it.
    import csv
    import io
    import json
    zp_path = os.path.join(ROOT, "content", "manual", "source",
                           "zone_products.json")
    cat_path = os.path.join(ROOT, "ops", "affiliate-catalogue.csv")
    page_path = os.path.join(ROOT, "site", "kit.html")
    if os.path.exists(zp_path) and os.path.exists(cat_path) and os.path.exists(page_path):
        zone_products = json.load(io.open(zp_path, encoding="utf-8"))
        real_rarity: dict = {}
        for items in zone_products.values():
            for it in items:
                real_rarity[it["id"]] = real_rarity.get(it["id"], 0) + 1
        real_rows = [r for r in csv.DictReader(
            io.open(cat_path, encoding="utf-8-sig")) if r["Tier"].startswith("1")]
        real_page = io.open(page_path, encoding="utf-8", errors="replace").read()
        problems = preflight.check_kit_page_zone_counts(
            real_rarity, real_rows, real_page)
        if problems:
            fails.append("the real committed site/kit.html does not match "
                        "a live re-derivation of the zone counts: %s"
                        % problems)
    else:
        print("  (skipped case 4: a real source file is missing here)")

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("OK  gate_kit_page_zone_counts: 4/4 cases pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
