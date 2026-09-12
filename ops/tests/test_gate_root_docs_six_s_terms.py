#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_root_docs_six_s_terms() catches the two real
shapes of defect found 2026-09-12: the retired term "Set in Order" used as
a bare list item, and a six-item 6S list with Safety out of its fourth
position (D-014).

Found reading AUTONOMY-MEMORY-ARCHITECTURE.md and AUTONOMY-ORCHESTRATION.md
cold, per CLAUDE.md step 5d, as part of a standing handoff to check every
zero-nightly-log-mention 2026-08-17 planning document for stale claims.
Both files listed the 6S steps as a bare six-line block (one word per
line); AUTONOMY-MEMORY-ARCHITECTURE.md also placed Safety last on a second
list. ops/preflight.py's own gate_card_corpus already caught this exact
term once before on a different surface (the card text corpus), a
different surface each time, so this widens the check to every root-level
*.md operating document rather than waiting for a fourth surface.

The naive version of this check (a whole-document substring search for
"set in order", and an unanchored sliding window over every six-word hit)
produced real false positives before shipping: this project's own style
and history docs (CONTENT-STANDARDS.md, RISKS.md, STATUS.md, STRIPE.md,
BACKLOG-2026-H2.md, OWNER-ACTIONS.md, PLAN-MEDIA-2026-09-07.md, LOOP.md,
EXECUTIVE-DASHBOARD-LIVE.md, RETRO-2026-08-30-cycle2.md) correctly quote
or narrate the retired term in running prose to document the rule or
record a past fix, and two separate, correctly-ordered lists sitting a
few lines apart in AUTONOMY-ORCHESTRATION.md looked like one list rotated
out of order to an unanchored window. Both are covered as cases below.

Run:  python ops/tests/test_gate_root_docs_six_s_terms.py
"""
import glob
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    # 1. A bare "Set in Order" list-item line must be caught.
    bad = preflight.check_six_s_terms("SORT\nSET IN ORDER\nSHINE\n")
    if not bad:
        fails.append("a bare 'SET IN ORDER' list-item line was not caught")

    # 2. A six-item list with Safety last (the AUTONOMY-MEMORY-ARCHITECTURE.md
    #    shape, correctly spelled otherwise) must be caught.
    safety_last = "\n".join(
        ["SORT", "x", "STRAIGHTEN", "x", "SHINE", "x",
         "STANDARDIZE", "x", "SUSTAIN", "x", "SAFETY", "x"])
    bad2 = preflight.check_six_s_terms(safety_last)
    if not bad2:
        fails.append("a six-item list with Safety last was not caught")

    # 3. A correctly ordered, correctly spelled list must pass clean.
    clean = "\n".join(
        ["SORT", "x", "STRAIGHTEN", "x", "SHINE", "x",
         "SAFETY", "x", "STANDARDIZE", "x", "SUSTAIN", "x"])
    if preflight.check_six_s_terms(clean):
        fails.append("a correctly ordered list was wrongly flagged")

    # 4. Running prose that quotes or narrates the retired term must not
    #    trip the bare-line check (the real false positive found across ten
    #    files before this was narrowed to line-shape).
    prose_cases = [
        'The term "Set in Order" is rejected across all 6S Success material.',
        'grep -rn "Set in Order" --include="*.html" --include="*.md" .',
        "> **Wrong:** Sort, Set in Order, Shine, Standardize, Sustain, "
        "and Safety.",
        "945 uses of the rejected term \"Set in Order\" swept to "
        "\"Straighten\".",
    ]
    for text in prose_cases:
        if preflight.check_six_s_terms(text):
            fails.append("prose mention wrongly flagged: %r" % text[:60])

    # 5. Two separate, correctly-ordered six-item lists sitting a few lines
    #    apart (AUTONOMY-ORCHESTRATION.md's real shape after the fix) must
    #    not look like one list rotated out of order to an unanchored
    #    window.
    two_lists = "\n".join(
        ["SORT", "STRAIGHTEN", "SHINE", "SAFETY", "STANDARDIZE", "SUSTAIN",
         "", "filler line", "",
         "SORT", "STRAIGHTEN", "SHINE", "SAFETY", "STANDARDIZE", "SUSTAIN"])
    if preflight.check_six_s_terms(two_lists):
        fails.append("two adjacent correct lists were wrongly flagged "
                      "as one rotated list")

    # 6. A lone word many lines from an unrelated list must not complete a
    #    false set (the real AUTONOMY-ORCHESTRATION.md shape: a standalone
    #    "SUSTAIN" heading 49 lines before an unrelated correct list).
    far_apart = "SUSTAIN\n" + ("filler\n" * 40) + "\n".join(
        ["SORT", "STRAIGHTEN", "SHINE", "SAFETY", "STANDARDIZE"])
    if preflight.check_six_s_terms(far_apart):
        fails.append("a lone word far from an unrelated list was wrongly "
                      "counted into a false six-item set")

    # 7. Prove the real gate runs clean against the live, already-fixed
    #    repository, not just the pure function in isolation.
    preflight.FAIL.clear()
    preflight.gate_root_docs_six_s_terms()
    if preflight.FAIL:
        fails.append("real gate run against the live repo found problems "
                     "(expected clean): %s" % preflight.FAIL)
    preflight.FAIL.clear()

    # 8. Prove the real gate CAN fail: plant the exact pre-fix regression in
    #    a throwaway copy of one real file's known-good six-item block and
    #    confirm check_six_s_terms() on that text reports it.
    real_files = glob.glob(os.path.join(ROOT, "*.md"))
    if real_files:
        sample = io.open(real_files[0], encoding="utf-8",
                          errors="replace").read()
        planted = sample + "\n\nSORT\nSET IN ORDER\nSHINE\n"
        if not preflight.check_six_s_terms(planted):
            fails.append("planting the real defect shape onto a live file "
                         "did not get caught")

    if fails:
        print("FAILED %d case(s):" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("PASSED 8 cases (bare retired term caught, Safety-last caught, "
          "correct order passes, four real prose shapes do not false "
          "positive, two adjacent correct lists are not read as one "
          "rotated list, a distant lone word does not complete a false "
          "set, the real repo runs clean, and the real defect shape "
          "planted onto a live file is caught)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
