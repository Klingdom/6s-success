#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_nav_canonical() catches a page whose primary
nav does not match ops/wire_nav.py's own NAV list of five items, in order.

Found 2026-09-10, reading ops/wire_nav.py cold (a 2-mention file) per
CLAUDE.md step 5d: wire_nav.py holds the one canonical nav list but nothing
calls it, not one other ops/build_*.py file, not preflight.py, not any CI
workflow. Every page's nav in fact stays correct today only because it is
scraped, at build time, from an already-committed sibling page, a chain
that happens to still terminate on the right five items, not because
anything ties it to wire_nav.py's own list. One generator
(ops/build_kitchen_deck_page.py) does not scrape at all and hardcodes its
own independent copy of the identical five links. No live drift exists
today, but nothing before this gate would have caught a hand edit, a future
hardcoded copy going stale, or wire_nav.NAV itself changing without every
copy following it.

Run:  python ops/tests/test_gate_nav_canonical.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import wire_nav                                                # noqa: E402

GOOD_NAV = (
    '<nav class="nav" aria-label="Primary">\n'
    '      <a href="zones/">Start a reset</a>\n'
    '      <a href="method.html">How 6S works</a>\n'
    '      <a href="resources.html">Rooms</a>\n'
    '      <a href="book.html">Cards and book</a>\n'
    '      <a href="consulting.html">Get help</a>\n'
    '    </nav>'
)

GOOD_NAV_WITH_CURRENT = GOOD_NAV.replace(
    '<a href="book.html">Cards and book</a>',
    '<a href="book.html" aria-current="page">Cards and book</a>')

STALE_SEVEN_ITEM_NAV = (
    '<nav class="nav" aria-label="Primary">\n'
    '      <a href="method.html">The Method</a>\n'
    '      <a href="resources.html">Rooms</a>\n'
    '      <a href="zones/">Micro zones</a>\n'
    '      <a href="quest.html">The Quest</a>\n'
    '      <a href="shop.html">Shop</a>\n'
    '      <a href="consulting.html">Consulting</a>\n'
    '      <a href="book.html">The Book</a>\n'
    '    </nav>'
)

PAGE_TPL = (
    '<!doctype html><html><head><title>t</title></head>'
    '<body><header class="site-header">%s</header>'
    '<main id="main">content</main></body></html>'
)


def _write(tmp, rel, nav_html):
    path = os.path.join(tmp, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", encoding="utf-8").write(PAGE_TPL % nav_html)


def _run(pages):
    """pages: {relative_path: nav_html_or_None}. None means no nav at all."""
    tmp = tempfile.mkdtemp()
    for rel, nav_html in pages.items():
        _write(tmp, rel, nav_html if nav_html is not None else "")
    old_site = preflight.SITE
    preflight.SITE = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_nav_canonical()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.SITE = old_site
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. A single top-level page with the exact canonical nav: no failure.
    f, w = _run({"index.html": GOOD_NAV})
    if f:
        fails.append("clean top-level nav wrongly flagged: %r" % (f,))

    # 2. The same nav with aria-current added to the active page's own link:
    #    still correct, aria-current is not part of what this gate checks
    #    (gate_nav_current owns that).
    f, w = _run({"book.html": GOOD_NAV_WITH_CURRENT})
    if f:
        fails.append("nav with aria-current wrongly flagged: %r" % (f,))

    # 3. A page one directory down using "../" prefixes on every href: still
    #    correct, since the prefix is stripped before comparing.
    nested = GOOD_NAV.replace('href="', 'href="../')
    f, w = _run({"rooms/kitchen.html": nested})
    if f:
        fails.append("correctly-prefixed nested nav wrongly flagged: %r" % (f,))

    # 4. The real-world regression shape: a stale seven-item nav, the exact
    #    kind wire_nav.py itself exists to have cut down from.
    f, w = _run({"index.html": GOOD_NAV, "old-page.html": STALE_SEVEN_ITEM_NAV})
    if not f or "old-page.html" not in f[0][1]:
        fails.append("stale seven-item nav not caught by name: %r" % (f,))

    # 5. A wrong label only (hrefs correct, text drifted): still caught,
    #    since the label is part of what has to match exactly.
    wrong_label = GOOD_NAV.replace("Cards and book", "Cards & Book")
    f, w = _run({"index.html": wrong_label})
    if not f or "index.html" not in f[0][1]:
        fails.append("drifted label not caught by name: %r" % (f,))

    # 6. deck/ pages are deliberately excluded, the same skip wire_nav.py's
    #    own main() applies, so a stale nav there must not fail the gate.
    f, w = _run({"index.html": GOOD_NAV, "deck/card.html": STALE_SEVEN_ITEM_NAV})
    if f:
        fails.append("deck/ page wrongly checked: %r" % (f,))

    # 7. No page anywhere carries a primary nav: unchecked, not a pass.
    f, w = _run({"index.html": None})
    if f or not w or "nothing was checked" not in w[0][1]:
        fails.append("nav-less site did not report unchecked: fail=%r warn=%r"
                      % (f, w))

    # 8. The real committed site: clean.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_nav_canonical()
    if preflight.FAIL:
        fails.append("the real committed site failed: %r" % (preflight.FAIL,))

    # 9. wire_nav.NAV itself is still five items, the count this whole gate
    #    assumes. If a future edit changes that count deliberately, this
    #    assertion is the reminder to re-read this test's fixtures too.
    if len(wire_nav.NAV) != 5:
        fails.append("wire_nav.NAV is no longer 5 items (%d); this test's "
                     "fixtures assume the current list" % len(wire_nav.NAV))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_nav_canonical, 9/9 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
