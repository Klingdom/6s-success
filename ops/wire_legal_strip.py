#!/usr/bin/env python3
"""
Own the legal strip at the bottom of every footer, in one place.

WHY THIS EXISTS
---------------
The strip that reads "Privacy - How we make money - Terms - Accessibility -
Safety notice" appears on 188 pages and was never owned by anything. Twenty
three pages carry it hand written, and the other 165 have it only because
ops/build_articles.py, ops/build_zone_pages.py, ops/build_kit_page.py and
their siblings lift the whole footer verbatim out of resources.html or
method.html at build time. So adding one link meant editing 23 files by hand
and hoping every generator was re-run afterwards, and nothing checked.

That is exactly the drift ops/preflight.py's generator-ownership gate exists
to catch, arriving through the one part of the page no generator claims.

WHAT IT DOES
------------
Rebuilds the second span of <div class="foot-bottom"> from the table below,
on every page that has one, at whatever relative depth that page sits. It is
idempotent: it replaces the strip rather than appending to it, so running it
twice produces the same bytes as running it once. Run it after any builder
that writes HTML, and before ops/fingerprint_assets.py.

WHAT ALREADY WATCHES IT
----------------------
ops/preflight.py's gate_footer_consistent compares every page's whole footer
against resources.html and fails on any difference, so once this script has
run, a page that later loses the strip is caught. That gate could not tell you
the strip was missing from the entire site, because "consistently missing" is
consistent. This script is the half that decides what the strip should say;
that gate is the half that keeps all 188 pages agreeing with it.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
It does not touch the copyright span, the footer columns, or any page with no
strip at all. site/invest.html, the print-and-play deck sheet and the two
files under site/downloads/ are documents rather than site pages and are left
exactly as they are.

Run:  python ops/wire_legal_strip.py
      python ops/wire_legal_strip.py --check     (fails if any page is stale)
"""
from __future__ import annotations

import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

# (href without prefix, label). Order is the order shown.
#
# The affiliate disclosure sits next to How we make money because they answer
# the same question from two directions, and it is in the strip at all
# because the FTC asks for a disclosure a reader can find from the page they
# are on, not one they have to know the name of.
LINKS = [
    ("privacy.html", "Privacy"),
    ("how-we-make-money.html", "How we make money"),
    ("affiliate-disclosure.html", "Affiliate disclosure"),
    ("terms.html", "Terms"),
    ("accessibility.html", "Accessibility"),
    ("disclaimer.html", "Safety notice"),
]

STRIP_RE = re.compile(
    r'(<div class="foot-bottom">\s*<span>.*?</span>\s*<span>)(.*?)(</span>\s*</div>)',
    re.S)


def span(prefix: str) -> str:
    return " &middot; ".join(
        f'<a href="{prefix}{href}">{label}</a>' for href, label in LINKS)


def main(check: bool = False) -> int:
    changed, stale = 0, []
    for f in sorted(glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(f, SITE).replace(os.sep, "/")
        if rel.startswith("downloads/"):
            continue
        s = io.open(f, encoding="utf-8").read()
        m = STRIP_RE.search(s)
        if not m:
            continue

        # The prefix the page already uses, read off its own markup rather
        # than derived from its path, so a page in a directory nobody
        # anticipated still gets working links.
        depth = re.search(r'href="((?:\.\./)+)', m.group(2))
        prefix = depth.group(1) if depth else "../" * rel.count("/")

        new = m.group(1) + span(prefix) + m.group(3)
        if new == m.group(0):
            continue
        if check:
            stale.append(rel)
            continue
        io.open(f, "w", encoding="utf-8", newline="").write(
            s[:m.start()] + new + s[m.end():])
        changed += 1

    if check:
        if stale:
            print(f"  FAIL  {len(stale)} page(s) carry a stale legal strip: "
                  f"{stale[:4]}")
            return 1
        print("  every legal strip matches the table")
        return 0

    print(f"  legal strip rewritten on {changed} pages, {len(LINKS)} links")

    # A footer link that 404s is worse than a missing one, and this strip is
    # the only route to four of these pages from most of the site.
    bad = []
    for f in glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True):
        s = io.open(f, encoding="utf-8").read()
        m = STRIP_RE.search(s)
        if not m:
            continue
        for href in re.findall(r'href="([^"]+)"', m.group(2)):
            target = os.path.normpath(os.path.join(os.path.dirname(f), href))
            if not os.path.exists(target):
                bad.append((os.path.relpath(f, ROOT), href))
    assert not bad, f"legal strip links that resolve to nothing: {bad[:4]}"
    print("  every legal-strip link on every page resolves")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--check" in sys.argv))
