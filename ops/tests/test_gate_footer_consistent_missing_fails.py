#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_footer_consistent() FAILS (not just warns) on a
page with no site footer at all, the exact live defect found 2026-09-25:
commit 6ba42a27 dropped the footer from all 114 zone pages and all 20 room
pages when build_zone_pages.py lifted its chrome from a resources.html that
had been temporarily broken by an unrelated bug elsewhere in the same
commit. The gate only warned at the time, so it did not stop that merge.

Run:  python ops/tests/test_gate_footer_consistent_missing_fails.py
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

CANON_FOOTER = ('<footer class="site-footer"><div class="wrap">'
                '<a href="privacy.html">Privacy</a></div></footer>')


def check(name, condition):
    global PASS, FAILCOUNT
    if condition:
        PASS += 1
    else:
        FAILCOUNT += 1
        print(f"  FAIL: {name}")


def run_gate_against(pages: dict) -> tuple:
    """pages: {relative_path: html_text}, always including resources.html as
    the canonical source. Writes into a scratch site/ directory, points
    preflight.SITE at it, runs the real gate, restores. Returns (fails, warns)."""
    tmpdir = tempfile.mkdtemp()
    scratch_site = os.path.join(tmpdir, "site")
    os.makedirs(scratch_site)
    all_pages = {"resources.html": f"<html><body>{CANON_FOOTER}</body></html>"}
    all_pages.update(pages)
    for rel, html in all_pages.items():
        full = os.path.join(scratch_site, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        io.open(full, "w", encoding="utf-8").write(html)
    real_site = preflight.SITE
    try:
        preflight.SITE = scratch_site
        preflight.FAIL.clear()
        preflight.WARN.clear()
        preflight.gate_footer_consistent()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.SITE = real_site
        shutil.rmtree(tmpdir)


def main():
    # 1. A page with no footer at all must FAIL, naming the file, not warn.
    fails, warns = run_gate_against({
        "rooms/kitchen.html": "<html><body><main>No footer here.</main></body></html>",
    })
    check("page with no footer fails",
          any("kitchen.html" in m for _, m in fails))
    check("page with no footer is not merely warned about",
          not any("kitchen.html" in m for _, m in warns))

    # 2. The fix: insert the exact canonical footer. Must pass clean.
    fails, warns = run_gate_against({
        "rooms/kitchen.html": f"<html><body><main>Content.</main>{CANON_FOOTER}</body></html>",
    })
    check("page with the canonical footer passes", fails == [] and warns == [])

    # 3. A page with a DIFFERENT (drifted) footer must still fail too, same
    # as before this change; missing and drifted are both a fail now.
    fails, warns = run_gate_against({
        "rooms/kitchen.html": ('<html><body><main>Content.</main>'
                                '<footer class="site-footer">'
                                '<div class="wrap">Old copy, no privacy link.'
                                '</div></footer></body></html>'),
    })
    check("page with a drifted footer still fails",
          any("kitchen.html" in m for _, m in fails))

    # 4. The two by-design footer-less pages must never be flagged.
    fails, warns = run_gate_against({
        "invest.html": "<html><body><main>Investor page.</main></body></html>",
        "deck/entryway-print-and-play.html":
            "<html><body><main>Moved notice.</main></body></html>",
    })
    check("by-design footer-less pages are never flagged",
          fails == [] and warns == [])

    # 5. Multiple pages missing a footer at once: every one named.
    fails, warns = run_gate_against({
        "rooms/a.html": "<html><body><main>A</main></body></html>",
        "rooms/b.html": "<html><body><main>B</main></body></html>",
        "rooms/c.html": f"<html><body><main>C</main>{CANON_FOOTER}</body></html>",
    })
    msgs = " ".join(m for _, m in fails)
    check("both missing pages named, the clean one is not",
          "a.html" in msgs and "b.html" in msgs and "c.html" not in msgs)

    # 6. Sanity: the real committed site/ passes today, after this cycle's
    # fix (ops/wire_footer.py) inserted the footer on all 134 pages.
    preflight.FAIL.clear()
    preflight.WARN.clear()
    preflight.gate_footer_consistent()
    check("real site/ directory clean today",
          preflight.FAIL == [] and preflight.WARN == [])

    print(f"\n{PASS} of {PASS + FAILCOUNT} cases pass")
    return 1 if FAILCOUNT else 0


if __name__ == "__main__":
    sys.exit(main())
