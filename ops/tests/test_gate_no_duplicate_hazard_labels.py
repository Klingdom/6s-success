#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_no_duplicate_hazard_labels() catches the real
regression shape found 2026-09-19: a zone whose watch_for entries share a
hazard category (there are only five; ops/hazard_icons.py) rendering the
identical bold heading twice in the "Check these before you start" list, once
per hazard, instead of once per category with both hazards merged under it.

Found by a narrative read of the rendered pages, not by any prior mechanical
check, on 6 of 114 real zones (kitchen-the-cooking-zone among them). Fixed in
ops/build_zone_pages.py with _grouped_watch_for(); this gate re-derives the
defect independently, straight from the shipped HTML.

Run:  python ops/tests/test_gate_no_duplicate_hazard_labels.py
"""
import glob
import io
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

CLEAN = (
    '<h2>Check these before you start</h2><ul class="hazard-list">'
    '<li><b>Burn or fire</b>Oil left unattended.</li>'
    '<li><b>Fall, cut, or crush</b>A pan handle turned out.</li>'
    '</ul>'
)

DUPLICATE = (
    '<h2>Check these before you start</h2><ul class="hazard-list">'
    '<li><b>Burn or fire</b>Oil left unattended.</li>'
    '<li><b>Fall, cut, or crush</b>A pan handle turned out.</li>'
    '<li><b>Burn or fire</b>A gas burner that will not light.</li>'
    '</ul>'
)

MERGED = (
    '<h2>Check these before you start</h2><ul class="hazard-list">'
    '<li><b>Burn or fire</b>Oil left unattended. A gas burner that will '
    'not light.</li>'
    '<li><b>Fall, cut, or crush</b>A pan handle turned out.</li>'
    '</ul>'
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
        preflight.gate_no_duplicate_hazard_labels()
        return list(preflight.FAIL)
    finally:
        preflight.SITE = old_site
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. A clean page with no repeated category: no failure.
    r = _run({"clean.html": CLEAN})
    if r:
        fails.append("clean page wrongly flagged: %r" % (r,))

    # 2. The exact regression shape: two <b> hazard labels the same on one
    #    page, caught by name.
    r = _run({"kitchen-the-cooking-zone.html": DUPLICATE})
    if not r or "kitchen-the-cooking-zone.html" not in r[0][1]:
        fails.append("duplicate-heading regression not caught: %r" % (r,))

    # 3. The real fix (one heading, both sentences merged underneath): clean.
    r = _run({"kitchen-the-cooking-zone.html": MERGED})
    if r:
        fails.append("merged (fixed) page wrongly flagged: %r" % (r,))

    # 4. A page with no hazard list at all: not a false positive.
    r = _run({"no-hazards.html": "<h2>Other stuff</h2><p>...</p>"})
    if r:
        fails.append("page with no hazard list wrongly flagged: %r" % (r,))

    # 5. Direct against the real pre-fix committed file, if HEAD still has
    #    the old shape (this repo, right after the fix, will not; a fresh
    #    clone before the fixing commit would). Not fatal either way: this
    #    proves the gate against real history when that history is reachable.
    try:
        old = subprocess.run(
            ["git", "show", "HEAD:site/zones/kitchen-the-cooking-zone.html"],
            cwd=ROOT, capture_output=True, text=True, timeout=20)
        if old.returncode == 0 and old.stdout.count("<b>Burn or fire</b>") >= 2:
            r = _run({"kitchen-the-cooking-zone.html": old.stdout})
            if not r:
                fails.append("real pre-fix committed file not caught")
        else:
            print("  (HEAD already carries the fix; skipping the "
                  "pre-fix-file check, real-corpus check below still runs)")
    except Exception as e:
        print("  (git show unavailable: %r, skipping pre-fix-file check)" % (e,))

    # 6. The real, committed site: clean on every one of the 114 zone pages.
    real_pages = sorted(glob.glob(os.path.join(ROOT, "site", "zones", "*.html")))
    if len(real_pages) < 100:
        print("  (skipped: fewer than 100 real zone pages found on disk)")
    else:
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_no_duplicate_hazard_labels()
        if preflight.FAIL:
            fails.append("real committed zone pages failed: %r" % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_no_duplicate_hazard_labels")
    return 0


if __name__ == "__main__":
    sys.exit(main())
