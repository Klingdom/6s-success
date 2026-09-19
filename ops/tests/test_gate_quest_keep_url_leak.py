#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_quest_keep_releases_urls_first() catches a
regression where renderKeep() (site/assets/js/quest.js) stops releasing the
previous visit's photograph blob URLs before repainting, and stays quiet on
the real, fixed committed file.

Found 2026-09-19: two of renderKeep()'s five real call sites (the #go-keep
nav button and the restore-backup flow) never called releaseUrls() first,
so the ordinary way anyone opens the Keep screen leaked one blob URL per
photograph shown, forever, for the life of the tab. Fixed by moving the
release inside renderKeep() itself. This is the pure-logic half of the
proof; ops/tests/test_quest_keep_url_leak.py drives the real browser.

Run:  python ops/tests/test_gate_quest_keep_url_leak.py
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

FIXED = """
  function renderKeep() {
    releaseUrls();
    var held = heldZones();
  }
"""

FIXED_WITH_COMMENT = """
  function renderKeep() {
    /* every repaint starts from zero live urls */
    releaseUrls();
    var held = heldZones();
  }
"""

REGRESSED_NO_RELEASE = """
  function renderKeep() {
    var held = heldZones();
  }
"""

REGRESSED_RELEASE_TOO_LATE = """
  function renderKeep() {
    var held = heldZones();
    releaseUrls();
  }
"""

MISSING_ENTIRELY = """
  function renderSomethingElse() {
    var held = heldZones();
  }
"""


def main() -> int:
    bad = []

    if preflight.check_quest_keep_releases_urls_first(FIXED) is not None:
        bad.append("false positive on a clean, unfixed-shape source")
    if preflight.check_quest_keep_releases_urls_first(FIXED_WITH_COMMENT) is not None:
        bad.append("false positive when a comment sits between the brace "
                    "and releaseUrls()")

    problem = preflight.check_quest_keep_releases_urls_first(REGRESSED_NO_RELEASE)
    if not problem:
        bad.append("missed a renderKeep() that never calls releaseUrls() at all")

    problem = preflight.check_quest_keep_releases_urls_first(REGRESSED_RELEASE_TOO_LATE)
    if not problem:
        bad.append("missed a renderKeep() that releases only after already "
                    "reading held zones (too late to protect a repaint that "
                    "happens before it)")

    problem = preflight.check_quest_keep_releases_urls_first(MISSING_ENTIRELY)
    if not problem:
        bad.append("missed renderKeep() being deleted or renamed entirely")

    real_path = os.path.join(ROOT, "site", "assets", "js", "quest.js")
    real_src = io.open(real_path, encoding="utf-8").read()
    problem = preflight.check_quest_keep_releases_urls_first(real_src)
    if problem:
        bad.append("the real committed quest.js fails clean: %s" % problem)

    if bad:
        print("  gate_quest_keep_releases_urls_first regression:")
        for b in bad:
            print("    - " + b)
        return 1

    print("  check_quest_keep_releases_urls_first: 2 clean shapes pass, 3 "
          "regression shapes caught by name, the real committed file is clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
