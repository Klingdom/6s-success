#!/usr/bin/env python3
"""
Prove gate_rejected_zone_heroes_have_panels() in ops/preflight.py can both
fail and pass, against the REAL committed site, not a synthetic fixture.

WHY THIS EXISTS
----------------
Found 2026-09-29, independently by two concurrent sessions: wire_zone_heroes.
py's fallback_wire() (the code path that runs in every sandboxed/CI checkout)
had no path to restore the "no photo yet" panel for a rejected hero, the
exact shape main()'s own have>0 sweep already carries
(test_zone_hero_panel.py, fixed 2026-09-27). Two Home Office zone pages and
one Workshop zone page shipped with no image or panel at all, and only the
slow full test suite (gate_tests) ever caught it. This gate is the fast
equivalent; this file proves it actually works, the same way every other
gate in this line proves itself against real committed content rather than
a synthetic stand-in.

Run:  python ops/tests/test_gate_rejected_zone_heroes_have_panels.py
"""
import io
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight as P                                          # noqa: E402

TARGET = os.path.join(ROOT, "site", "zones",
                       "home-office-the-file-storage.html")

FIG_RE = re.compile(
    r'<figure class="zone-hero" id="zone-hero">.*?</figure>\n?', re.S)


def case_real_site_passes_clean():
    P.FAIL.clear()
    P.WARN.clear()
    P.gate_rejected_zone_heroes_have_panels()
    assert not P.FAIL, P.FAIL


def case_a_stripped_panel_fails_by_name():
    assert os.path.exists(TARGET), "fixture page missing: " + TARGET
    backup = TARGET + ".bak"
    shutil.copy(TARGET, backup)
    try:
        s = io.open(TARGET, encoding="utf-8").read()
        stripped = FIG_RE.sub("", s, count=1)
        assert stripped != s, "nothing removed; the fixture regex is stale"
        io.open(TARGET, "w", encoding="utf-8", newline="").write(stripped)

        P.FAIL.clear()
        P.WARN.clear()
        P.gate_rejected_zone_heroes_have_panels()
        assert P.FAIL, "gate did not fail on a page with no hero at all"
        assert any("home-office-the-file-storage.html" in msg
                   for _g, msg in P.FAIL), P.FAIL
    finally:
        shutil.copy(backup, TARGET)
        os.remove(backup)


def case_restored_page_passes_again():
    """Proves the fixture cleanup above actually restored the real file,
    not just that the assertions inside the try block happened to pass."""
    P.FAIL.clear()
    P.WARN.clear()
    P.gate_rejected_zone_heroes_have_panels()
    assert not P.FAIL, P.FAIL


def case_no_verdicts_file_is_silent():
    real = os.path.join(P.ROOT, "ops", "hero-verdicts.json")
    assert os.path.exists(real), "hero-verdicts.json should exist in this repo"
    # No separate fixture needed: an absent-file branch is exercised by
    # temporarily pointing the check at a path that cannot exist, without
    # touching the real committed verdicts file.
    orig = P.os.path.exists
    try:
        P.os.path.exists = lambda p: False if p.endswith(
            "hero-verdicts.json") else orig(p)
        P.FAIL.clear()
        P.WARN.clear()
        P.gate_rejected_zone_heroes_have_panels()
        assert not P.FAIL and not P.WARN
    finally:
        P.os.path.exists = orig


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
