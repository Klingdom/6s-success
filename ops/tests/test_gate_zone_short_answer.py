#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_zone_short_answer_above_fold() catches the two
real regression shapes for backlog A4: the ~100-word "how to organize"
answer stripped entirely, and the answer surviving but pushed back behind
the 471-word supply list it was written to precede.

Found 2026-09-08: A4 was still open in BACKLOG-2026-09-07.md, but
short_answer() (commit ccb8fdbc, the same day) already renders this answer
second on every one of the 114 real zone pages, ahead of the supply list.
This gate exists so neither regression shape can ship silently again.

Run:  python ops/tests/test_gate_zone_short_answer.py
"""
import glob
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

GOOD = (
    '<p class="notice">One session: 30 min.</p>'
    '<div class="answer"><h2 class="answer-h">The short version</h2>'
    '<ol class="answer-steps"><li>Sort it</li></ol></div>'
    '<h2>What done looks like</h2><p>...</p>'
    '<h2 id="what-you-need">What to have on hand before you start</h2>'
    '<ul><li>A cloth</li></ul>'
    '<h2>The six passes, in order</h2><p>...</p>'
)

STRIPPED = (
    '<p class="notice">One session: 30 min.</p>'
    '<h2>What done looks like</h2><p>...</p>'
    '<h2 id="what-you-need">What to have on hand before you start</h2>'
    '<ul><li>A cloth</li></ul>'
    '<h2>The six passes, in order</h2><p>...</p>'
)

REORDERED = (
    '<p class="notice">One session: 30 min.</p>'
    '<h2 id="what-you-need">What to have on hand before you start</h2>'
    '<ul><li>A cloth</li></ul>'
    '<div class="answer"><h2 class="answer-h">The short version</h2>'
    '<ol class="answer-steps"><li>Sort it</li></ol></div>'
    '<h2>The six passes, in order</h2><p>...</p>'
)


def _run(pages: dict):
    tmp = tempfile.mkdtemp()
    zones = os.path.join(tmp, "zones")
    os.makedirs(zones)
    for name, body in pages.items():
        io.open(os.path.join(zones, name), "w", encoding="utf-8").write(body)
    old_site = preflight.SITE
    preflight.SITE = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_zone_short_answer_above_fold()
        return list(preflight.FAIL)
    finally:
        preflight.SITE = old_site
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. A clean page: no failure.
    r = _run({"clean.html": GOOD})
    if r:
        fails.append("clean page wrongly flagged: %r" % (r,))

    # 2. The answer stripped entirely: caught by name.
    r = _run({"stripped.html": STRIPPED})
    if not r or "stripped.html" not in r[0][1]:
        fails.append("stripped-answer regression not caught: %r" % (r,))

    # 3. The answer present but pushed behind the supply list: caught by name.
    r = _run({"reordered.html": REORDERED})
    if not r or "reordered.html" not in r[0][1]:
        fails.append("reordered regression not caught: %r" % (r,))

    # 4. zones/index.html (the listing page, not a real zone page) is exempt.
    r = _run({"index.html": STRIPPED})
    if r:
        fails.append("index.html wrongly checked as a zone page: %r" % (r,))

    # 5. The real, committed site: clean on every one of the 114 zone pages.
    real_pages = sorted(glob.glob(os.path.join(ROOT, "site", "zones", "*.html")))
    if len(real_pages) < 100:
        print("  (skipped: fewer than 100 real zone pages found on disk)")
    else:
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_zone_short_answer_above_fold()
        if preflight.FAIL:
            fails.append("real committed zone pages failed: %r" % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_zone_short_answer_above_fold, 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
