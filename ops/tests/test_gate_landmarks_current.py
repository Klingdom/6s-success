#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_landmarks_current() catches a page missing the
skip link and/or the <main id="main"> landmark ops/wire_landmarks.py exists
to guarantee: the exact accessibility regression found live 2026-09-25 on a
scratch copy of site/index.html, which ops/wire_landmarks.py's own --check
mode could not catch (it printed "0 left alone" and exited 0).

Run:  python ops/tests/test_gate_landmarks_current.py
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

SKIP = ('<!-- SKIP:BEGIN -->\n<a class="skip-link" href="#main">Skip to '
        'content</a>\n<!-- SKIP:END -->\n')
GOOD = f"<html><body>{SKIP}<main id=\"main\"><p>hi</p></main></body></html>"


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
        preflight.gate_landmarks_current()
        return list(preflight.FAIL)
    finally:
        preflight.SITE = real_site
        shutil.rmtree(tmpdir)


def main():
    # 1. A clean page: skip link to #main, plus the landmark. Must pass.
    fails = run_gate_against({"good.html": GOOD})
    check("a correctly wired page passes", fails == [])

    # 2. The exact live shape: skip link stripped entirely, id="main"
    # stripped from an otherwise-present <main> tag. Must fail, naming both.
    broken = "<html><body><main><p>hi</p></main></body></html>"
    fails = run_gate_against({"index.html": broken})
    msg = " ".join(m for _, m in fails)
    check("missing skip link is named", "no skip link to #main" in msg)
    check("missing main id is named", 'no <main id="main">' in msg)
    check("the broken file is named", "index.html" in msg)

    # 3. A skip link present but pointing somewhere other than #main must
    # still fail: a skip link to the wrong target helps nobody.
    wrong_target = ('<html><body><!-- SKIP:BEGIN -->\n'
                     '<a class="skip-link" href="#top">Skip to content</a>\n'
                     '<!-- SKIP:END -->\n<main id="main"></main></body></html>')
    fails = run_gate_against({"wrong.html": wrong_target})
    check("a skip link to the wrong target fails",
          any("wrong.html" in m for _, m in fails))

    # 4. A page under deck/ or downloads/ with neither element must never be
    # flagged: ops/wire_landmarks.py itself deliberately skips these.
    fails = run_gate_against({
        "deck/entryway-print-and-play.html": "<html><body><p>sheet</p></body></html>",
        "downloads/sample.html": "<html><body><p>doc</p></body></html>",
    })
    check("deck/ and downloads/ pages are never flagged", fails == [])

    # 5. Multiple broken pages at once: every one must be named.
    fails = run_gate_against({"a.html": broken, "b.html": broken, "c.html": GOOD})
    msgs = " ".join(m for _, m in fails)
    check("both broken pages named, the clean one is not",
          "a.html" in msgs and "b.html" in msgs and "c.html" not in msgs)

    # 6. Sanity: the real committed site/ passes today.
    preflight.FAIL.clear()
    preflight.gate_landmarks_current()
    check("real site/ directory clean today", preflight.FAIL == [])

    print(f"\n{PASS} of {PASS + FAILCOUNT} cases pass")
    return 1 if FAILCOUNT else 0


if __name__ == "__main__":
    sys.exit(main())
