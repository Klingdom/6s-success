#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_chapter_svgs_current() catches a wired
chapter figure drifting from a fresh extraction of its own book chapter.

Found 2026-09-19, cold-reading ops/import_chapter_svgs.py per the standing
low-mention ops/*.py lane. It imports six hand-authored SVG diagrams out of
the book's chapter HTML onto their zone pages, once each, by design: wire()
skips a figure the moment its id already exists on the page, so rerunning
the importer is safe. That same design means nothing would notice if a
chapter's own SVG were hand-edited after the import ran; the page would
keep showing the old figure forever with no error from anything, the same
"source corrected, artifact never re-derived" shape this repository's own
gates keep closing elsewhere (hero-fallback, the Standards Pack, the
pre-rendered shop grid, the KDP cover). Checked directly first: today, all
six wired figures are byte-identical to a fresh extraction, so this closes
a latent gap, not a live one.

Run:  python ops/tests/test_gate_chapter_svgs_current.py
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import import_chapter_svgs as ICS                              # noqa: E402


def main() -> int:
    fails = []

    fresh = {
        "fig-a": "<figure id=\"fig-a\" class=\"zone-figure\">\n<svg>A</svg>\n</figure>",
        "fig-b": "<figure id=\"fig-b\" class=\"zone-figure\">\n<svg>B</svg>\n</figure>",
    }

    # 1. Identical: no problems.
    r = preflight.check_chapter_svgs_current(fresh, dict(fresh))
    if r:
        fails.append("identical state wrongly flagged: %r" % (r,))

    # 2. A figure the fresh extraction expects but the committed page never
    #    got (or a marker the fresh chapter no longer contains at all):
    #    caught by name, not silently skipped.
    committed_missing_b = {"fig-a": fresh["fig-a"]}
    r = preflight.check_chapter_svgs_current(fresh, committed_missing_b)
    if not r or "fig-b" not in r[0]:
        fails.append("a figure missing from the committed page was not "
                      "caught by name: %r" % (r,))

    # 3. A wired figure whose committed content no longer matches a fresh
    #    extraction: the exact drift wire()'s own "id already exists" skip
    #    cannot detect, caught here as changed, not identical.
    committed_stale = {
        "fig-a": "<figure id=\"fig-a\" class=\"zone-figure\">\n<svg>OLD A</svg>\n</figure>",
        "fig-b": fresh["fig-b"],
    }
    r = preflight.check_chapter_svgs_current(fresh, committed_stale)
    if not r or not any("fig-a" in p for p in r):
        fails.append("a stale wired figure was not caught by name: %r"
                      % (r,))

    # 4. The real, committed chapters against the real, committed zone
    #    pages: clean today. Proves the gate as actually wired, not just
    #    the pure logic above.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_chapter_svgs_current()
    if preflight.FAIL:
        fails.append("the real committed chapter figures failed: %r"
                      % (preflight.FAIL,))

    # 5. The real gate genuinely catches drift, not just the pure function:
    #    plant a stale figure block into a real, committed zone page (the
    #    exact "chapter edited after import" shape), confirm the gate fails
    #    by name, then restore the page byte for byte so this test leaves
    #    no trace.
    fig = ICS.FIGURES[0]
    fid = ICS.fig_id(fig)
    path = os.path.join(ICS.SITE, fig["page"])
    original = io.open(path, encoding="utf-8").read()
    try:
        pattern = re.compile(
            re.escape(f'<figure id="{fid}" class="zone-figure">') +
            r'.*?</figure>', re.S)
        m = pattern.search(original)
        if not m:
            fails.append("setup: could not find the real committed figure "
                          "%r on %s to plant a drift into" % (fid, fig["page"]))
        else:
            stale = m.group(0).replace(fig["marker"], "STALE " + fig["marker"], 1)
            mutated = original[:m.start()] + stale + original[m.end():]
            io.open(path, "w", encoding="utf-8", newline="").write(mutated)

            preflight.FAIL, preflight.WARN = [], []
            preflight.gate_chapter_svgs_current()
            if not preflight.FAIL or fid not in preflight.FAIL[0][1]:
                fails.append("planting a real drift did not get caught by "
                              "name: %r" % (preflight.FAIL,))
    finally:
        io.open(path, "w", encoding="utf-8", newline="").write(original)

    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_chapter_svgs_current()
    if preflight.FAIL:
        fails.append("restoring the real page did not leave it clean: %r"
                      % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_chapter_svgs_current, 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
