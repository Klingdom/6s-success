#!/usr/bin/env python3
"""
Prove ops/wire_landmarks.py --check actually fails when a page's skip link
or main id would change, and exits clean when nothing would.

Found live 2026-09-25: main()'s exit code only ever depended on whether
site.css still carries a .skip-link rule. add_main() silently repairs a
missing id="main" in memory and reports "had one" either way, so a page
missing its skip link entirely or its main id printed "0 left alone" and
exited 0 in --check mode. site/index.html and its siblings are hand
maintained (no generator re-runs wire_landmarks.main() over them), so this
was the only thing that would ever have caught a hand edit stripping either
one, and it could not.

Run:  python ops/tests/test_wire_landmarks_check.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS, FAILCOUNT = 0, 0


def check(name, condition):
    global PASS, FAILCOUNT
    if condition:
        PASS += 1
    else:
        FAILCOUNT += 1
        print(f"  FAIL: {name}")


GOOD = ('<!-- SKIP:BEGIN -->\n<a class="skip-link" href="#main">Skip to '
        'content</a>\n<!-- SKIP:END -->\n<body></body>'
        '<main id="main"><p>hi</p></main><footer></footer>')


def run_check_in_place(page_html: str):
    """wire_landmarks.SITE is ROOT/site, fixed at import time, so exercise
    the real module functions directly against a scratch page instead of
    shelling out (mirrors ops/tests/test_gate_nav_toggle_wired.py's own
    SITE-swap pattern rather than trying to relocate the script)."""
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import importlib
    import wire_landmarks
    importlib.reload(wire_landmarks)

    tmpdir = tempfile.mkdtemp()
    site = os.path.join(tmpdir, "site")
    os.makedirs(os.path.join(site, "assets", "css"))
    io.open(os.path.join(site, "index.html"), "w", encoding="utf-8").write(page_html)
    io.open(os.path.join(site, "assets", "css", "site.css"),
            "w", encoding="utf-8").write(".skip-link{position:absolute}")
    real_site, real_argv = wire_landmarks.SITE, sys.argv
    try:
        wire_landmarks.SITE = site
        sys.argv = ["wire_landmarks.py", "--check"]
        return wire_landmarks.main()
    finally:
        wire_landmarks.SITE = real_site
        sys.argv = real_argv
        shutil.rmtree(tmpdir)


def main():
    # 1. A fully correct page: --check must exit 0.
    check("a correctly wired page exits 0", run_check_in_place(GOOD) == 0)

    # 2. The live defect shape: skip link stripped, main id stripped.
    # --check must exit 1.
    broken = "<body></body><main><p>hi</p></main><footer></footer>"
    check("missing skip link and main id exits 1",
          run_check_in_place(broken) == 1)

    # 3. Only the main id missing (skip link present): must still exit 1.
    only_id_missing = (
        '<!-- SKIP:BEGIN -->\n<a class="skip-link" href="#main">Skip to '
        'content</a>\n<!-- SKIP:END -->\n<body></body>'
        '<main><p>hi</p></main><footer></footer>')
    check("main id alone missing exits 1",
          run_check_in_place(only_id_missing) == 1)

    # 4. Sanity: the real committed site/ passes today.
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import wire_landmarks
    real_argv = sys.argv
    try:
        sys.argv = ["wire_landmarks.py", "--check"]
        check("real site/ passes --check today", wire_landmarks.main() == 0)
    finally:
        sys.argv = real_argv

    print(f"\n{PASS} of {PASS + FAILCOUNT} cases pass")
    return 1 if FAILCOUNT else 0


if __name__ == "__main__":
    sys.exit(main())
