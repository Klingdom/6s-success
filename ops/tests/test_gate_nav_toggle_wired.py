#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_nav_toggle_wired() catches a page that ships a
.nav-toggle button with no assets/js/site.js reference anywhere on the page,
the exact defect found live on 5 pages on 2026-09-23 (deck-gallery.html,
404.html, corporate.html, kit.html, and the two B2B articles): a visible
hamburger button that does nothing on tap, because the script that wires its
click handler never loaded.

Run:  python ops/tests/test_gate_nav_toggle_wired.py
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
        preflight.gate_nav_toggle_wired()
        return list(preflight.FAIL)
    finally:
        preflight.SITE = real_site
        shutil.rmtree(tmpdir)


NAV_BTN = '<button class="nav-toggle" aria-label="Open menu">Menu</button>'


def main():
    # 1. A page with a nav-toggle button and no site.js reference anywhere:
    # the exact live defect shape. Must fail, naming the file.
    fails = run_gate_against({
        "no-script.html": f"<html><body>{NAV_BTN}</body></html>",
    })
    check("nav-toggle with no site.js reference fails",
          any("no-script.html" in m for _, m in fails))

    # 2. The fix: the same page, with the script tag added. Must pass.
    fails = run_gate_against({
        "fixed.html": (f"<html><body>{NAV_BTN}"
                        '<script src="assets/js/site.js?v=abc123"></script>'
                        "</body></html>"),
    })
    check("nav-toggle with site.js referenced passes", fails == [])

    # 3. A nested page using a relative ../assets/js/site.js path (the real
    # shape used by site/articles/*.html): must also pass, not just the
    # bare "assets/js/site.js" form.
    fails = run_gate_against({
        "articles/deep.html": (f"<html><body>{NAV_BTN}"
                                '<script src="../assets/js/site.js"></script>'
                                "</body></html>"),
    })
    check("nested page with ../assets/js/site.js passes", fails == [])

    # 4. A page with no nav-toggle button at all must never be flagged,
    # regardless of whether it loads site.js (most zone/room pages have no
    # nav-toggle of their own kind here; this proves the gate is scoped to
    # pages that actually need the wiring, not every page on the site).
    fails = run_gate_against({
        "no-nav.html": "<html><body><p>Nothing here needs a menu.</p></body></html>",
    })
    check("page with no nav-toggle at all is never flagged", fails == [])

    # 5. Multiple broken pages at once: every one must be named, not just
    # the first found.
    fails = run_gate_against({
        "a.html": f"<html><body>{NAV_BTN}</body></html>",
        "b.html": f"<html><body>{NAV_BTN}</body></html>",
        "c.html": (f"<html><body>{NAV_BTN}"
                    '<script src="assets/js/site.js"></script></body></html>'),
    })
    msgs = " ".join(m for _, m in fails)
    check("both broken pages named, the clean one is not",
          "a.html" in msgs and "b.html" in msgs and "c.html" not in msgs)

    # 6. Sanity: the real committed site/ passes today, after the 2026-09-23
    # fix to all five pages this gate was written for.
    preflight.FAIL.clear()
    preflight.gate_nav_toggle_wired()
    check("real site/ directory clean today", preflight.FAIL == [])

    print(f"\n{PASS} of {PASS + FAILCOUNT} cases pass")
    return 1 if FAILCOUNT else 0


if __name__ == "__main__":
    sys.exit(main())
