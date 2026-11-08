#!/usr/bin/env python3
"""
Prove ops/preflight.py's ensure_pillow() actually retries a broken/missing
install and reports its real result, rather than assuming Pillow is fine
because ensure_pymupdf() already ran.

Found 2026-11-08: a cold sandbox's apt-installed `python3-pil` (Pillow
10.2.0) imported its pure-Python `__init__.py` but was missing the compiled
`_imaging` extension, so `from PIL import Image` raised `ImportError:
cannot import name '_imaging' from 'PIL'`. `gate_kdp_cover_current` read
that as a real FAIL and `gate_etsy_listing_valid` WARNed the same way, both
looking like content defects. `bootstrap_fresh_sandbox()` only ran
`ensure_pymupdf()`, whose install call is skipped entirely once pymupdf is
already importable, so a sandbox with pymupdf already present (left over
from an earlier partial bootstrap) never touched the broken Pillow at all.
Mirrors test_ensure_pymupdf.py's four cases against the new, separate
ensure_pillow() function with fake importable()/install() callables.

Run:  python ops/tests/test_ensure_pillow.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    # 1. Already importable: no install call at all.
    calls = []
    ok = preflight.ensure_pillow(
        importable=lambda: True,
        install=lambda: calls.append(1),
        attempts=3,
    )
    if not ok or calls:
        fails.append("already-importable case installed anyway: "
                      "ok=%r calls=%r" % (ok, calls))

    # 2. Broken on first check (the real 2026-11-08 shape), fixed on retry.
    state = {"tries": 0}

    def flaky_importable():
        # False before any install call, False on the first post-install
        # check (still broken), True from the second onward.
        return state["tries"] >= 2

    def flaky_install():
        state["tries"] += 1

    ok = preflight.ensure_pillow(
        importable=flaky_importable, install=flaky_install, attempts=3)
    if not ok:
        fails.append("a transient failure that recovers on retry still "
                     "reported False")
    if state["tries"] != 2:
        fails.append("expected exactly 2 install attempts before success, "
                     "got %d" % state["tries"])

    # 3. Never succeeds: must report False, not swallow the failure.
    ok = preflight.ensure_pillow(
        importable=lambda: False,
        install=lambda: None,
        attempts=3,
    )
    if ok:
        fails.append("a genuinely unavailable package was reported "
                     "importable")

    # 4. attempts is honoured exactly, not off by one.
    count = {"n": 0}
    preflight.ensure_pillow(
        importable=lambda: False,
        install=lambda: count.__setitem__("n", count["n"] + 1),
        attempts=2,
    )
    if count["n"] != 2:
        fails.append("attempts=2 should install exactly twice, got %d"
                     % count["n"])

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: ensure_pillow, 4/4 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
