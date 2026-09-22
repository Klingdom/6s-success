#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_consult_cta_current() catches the defect
class REVIEW-COMMERCE-2026-09-07.md C8 exists to hold: a zone, room or
article page with no real consult button, or one whose button links to
consulting.html with no origin query string. Fixed 2026-09-22 in
ops/build_zone_pages.py's offer()/room_offer(), ops/build_articles.py's
offer(), and ops/wire_consult_cta.py for the remaining hand-authored
articles; site/assets/js/measure.js records the click as a "service-cta"
event.

Also runs against the real, committed site/zones/, site/rooms/ and
site/articles/ files, so a future hand edit or a regeneration that drops
the button, downgrades it back to a plain text link, or strips its
origin query string fails this test directly.

Run:  python ops/tests/test_gate_consult_cta_current.py
"""
import glob
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

GOOD_ZONE = ('<p style="margin:0"><a class="btn btn-ghost btn-sm" '
             'data-sku="CN-VIRTUAL" '
             'href="../consulting.html?from=zone:entryway-the-landing-spot">'
             'See what a consult covers, 250 dollars</a></p>')

GOOD_ROOM = ('<p style="margin:0"><a class="btn btn-ghost btn-sm" '
             'data-sku="CN-VIRTUAL" href="../consulting.html?from=room:entryway">'
             'See what a consult covers, 250 dollars</a></p>')

GOOD_ARTICLE = ('<a class="btn btn-ghost btn-sm" data-sku="CN-VIRTUAL" '
                'href="../consulting.html?from=article:why-you-always-lose-your-keys">'
                'Talk it through, 250 dollars</a>')

# The one article that skips consulting.html entirely and goes straight to
# the Stripe payment link (why-you-cant-see-your-own-clutter.html's real,
# committed shape). No "from=" needed: measure.js's buy-click handler
# already records this button's origin page via page().
GOOD_DIRECT_BUY = ('<a class="btn btn-primary" data-sku="CN-VIRTUAL" '
                    'href="https://buy.stripe.com/5kQaEQ9vMacq63E2FG0kF2a" '
                    'rel="noopener">Book a Virtual Consult, $250</a>')

OLD_TEXT_LINK = ('<p style="margin:0;font-size:14.5px;opacity:.85">A one '
                  'hour virtual consult is 250 dollars. '
                  '<a href="../consulting.html" style="color:#DDA63A">'
                  'See what a consult covers</a>.</p>')


def main() -> int:
    fails = []

    # 1. Clean set: one zone, one room, one article, all with a real,
    #    origin-carrying button, plus the direct-buy shape. No problems.
    pages = {
        "zone": {"entryway-the-landing-spot.html": GOOD_ZONE},
        "room": {"entryway.html": GOOD_ROOM},
        "article": {"why-you-always-lose-your-keys.html": GOOD_ARTICLE,
                    "why-you-cant-see-your-own-clutter.html": GOOD_DIRECT_BUY},
    }
    problems = preflight.check_consult_cta_current(pages)
    if problems:
        fails.append("clean set flagged: %s" % problems)

    # 2. The exact pre-fix regression: a plain text link, no real button.
    pages_regressed = {
        "zone": {"entryway-the-landing-spot.html": OLD_TEXT_LINK},
        "room": {}, "article": {},
    }
    problems = preflight.check_consult_cta_current(pages_regressed)
    if not any("no real consult button" in p for p in problems):
        fails.append("text-link regression not caught: %s" % problems)

    # 3. A button present but with no page at all (missing entirely).
    pages_missing = {"zone": {"some-zone.html": "<main>nothing here</main>"},
                     "room": {}, "article": {}}
    problems = preflight.check_consult_cta_current(pages_missing)
    if not any("no real consult button" in p for p in problems):
        fails.append("missing button not caught: %s" % problems)

    # 4. A real button whose origin query string has been stripped (the
    #    href points at consulting.html with no "from=").
    stripped = GOOD_ROOM.replace("?from=room:entryway", "")
    pages_stripped = {"zone": {}, "room": {"entryway.html": stripped},
                      "article": {}}
    problems = preflight.check_consult_cta_current(pages_stripped)
    if not any("no origin query string" in p for p in problems):
        fails.append("stripped origin not caught: %s" % problems)

    # 5. Real site: every committed zone/room/article page (minus the
    #    deliberately excluded indexes and the two B2B articles) must
    #    already pass clean.
    real_pages = {}
    for label, subdir, skip in (
        ("zone", "zones", {"index.html"}),
        ("room", "rooms", set()),
        ("article", "articles", preflight.CONSULT_CTA_SKIP_ARTICLES),
    ):
        files = {}
        for f in sorted(glob.glob(os.path.join(ROOT, "site", subdir, "*.html"))):
            name = os.path.basename(f)
            if name in skip or name.startswith("_"):
                continue
            files[name] = io.open(f, encoding="utf-8", errors="replace").read()
        real_pages[label] = files
    if not any(real_pages.values()):
        print("  no real site pages found here; skipping the live-site case")
    else:
        problems = preflight.check_consult_cta_current(real_pages)
        if problems:
            fails.append("real committed site is not clean: %s" % problems[:6])
        n = sum(len(v) for v in real_pages.values())
        print(f"  real site: {n} page(s) checked")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print(f"PASS ({5} cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
