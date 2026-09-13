#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_page_ownership_registry() catches a top-level
site/*.html page that is not classified in exactly one of
GENERATED_TOP_LEVEL_PAGES or HAND_MAINTAINED_PAGES.

Found 2026-09-13: three consecutive ops/NIGHTLY-LOG.md entries treated
site/deck-gallery-mudroom.html as the next hand-maintained-page cold-read
candidate, each reached by grepping ops/build_*.py for the literal filename
and finding no hit. That grep missed ops/build_deck_gallery.py's real
f-string output path. Confirmed directly: running ops/build_deck_gallery.py
standalone reproduces the committed file byte for byte, and
gate_generator_ownership already protects it. No content was ever at risk,
but a future cycle acting on the wrong belief could have hand edited a
generator-owned page. This gate makes the classification itself checked
mechanically instead of re-derived by ad hoc grep every cycle.

Run:  python ops/tests/test_gate_page_ownership_registry.py
"""
import glob
import os
import sys
from unittest import mock

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


def run_gate_fresh(generated, hand, files):
    """Run the real gate against a fake site/ directory listing, with the
    two registries swapped for the case under test."""
    preflight.FAIL.clear()
    fake_paths = [os.path.join(preflight.SITE, f) for f in files]
    with mock.patch.object(preflight, "GENERATED_TOP_LEVEL_PAGES", generated), \
         mock.patch.object(preflight, "HAND_MAINTAINED_PAGES", hand), \
         mock.patch.object(preflight.glob, "glob", return_value=fake_paths):
        preflight.gate_page_ownership_registry()
    return list(preflight.FAIL)


def main():
    real_generated = dict(preflight.GENERATED_TOP_LEVEL_PAGES)
    real_hand = set(preflight.HAND_MAINTAINED_PAGES)
    all_real_files = sorted(set(real_generated) | real_hand)

    # 1. The exact real registries, against the exact files they name:
    # clean.
    fails = run_gate_fresh(real_generated, real_hand, all_real_files)
    check("real registries, real file list: no failure", fails == [])

    # 2. A new, unclassified page appears on disk: must fail by name.
    fails = run_gate_fresh(real_generated, real_hand,
                            all_real_files + ["surprise.html"])
    check("unclassified new page fails",
          any("surprise.html" in m for _, m in fails))

    # 3. The exact defect this gate exists to catch: a generator-written
    # page removed from GENERATED_TOP_LEVEL_PAGES (so it silently falls to
    # "unclassified", the same blind spot the literal grep had).
    generated_minus_mudroom = dict(real_generated)
    generated_minus_mudroom.pop("deck-gallery-mudroom.html", None)
    fails = run_gate_fresh(generated_minus_mudroom, real_hand, all_real_files)
    check("deck-gallery-mudroom.html unclassified if dropped from registry",
          any("deck-gallery-mudroom.html" in m for _, m in fails))

    # 4. A page listed in both registries: contradiction must fail.
    hand_plus_overlap = set(real_hand) | {"corporate.html"}
    fails = run_gate_fresh(real_generated, hand_plus_overlap, all_real_files)
    check("page in both registries fails",
          any("corporate.html" in m and "both registries" in m
              for _, m in fails))

    # 5. A registry entry for a file that no longer exists on disk: must
    # fail rather than stay silently stale.
    hand_plus_ghost = set(real_hand) | {"retired-page.html"}
    fails = run_gate_fresh(real_generated, hand_plus_ghost, all_real_files)
    check("stale registry entry for a deleted page fails",
          any("retired-page.html" in m for _, m in fails))

    # 6. Sanity: the real registries actually classify every real
    # site/*.html top-level file today, run against the real disk (not the
    # mocked glob), so this test would catch a genuinely new unclassified
    # page in the live repository, not just in the synthetic cases above.
    preflight.FAIL.clear()
    preflight.gate_page_ownership_registry()
    check("real site/ directory fully classified today", preflight.FAIL == [])

    print(f"\n{PASS} of {PASS + FAILCOUNT} cases pass")
    return 1 if FAILCOUNT else 0


if __name__ == "__main__":
    sys.exit(main())
