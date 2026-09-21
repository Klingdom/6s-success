#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_deck_pdf_size_budget() catches the real
oversized-download shape `REVIEW-COMMERCE-2026-09-07.md` C16 measured live
(26,192,171 bytes against an 8 MB budget), and that it does not flag a file
that honestly fits.

Pure logic, no filesystem: check_deck_pdf_size_budget() takes a byte count,
not a path, so this proves the threshold itself without needing an 8 MB+
fixture file in the repository.

Run:  python ops/tests/test_gate_deck_pdf_size_budget.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []
    MB = 1024 * 1024

    # 1. The real, live defect this gate exists to catch: the deck as it
    #    shipped before the 2026-09-21 re-export.
    problem = preflight.check_deck_pdf_size_budget(26_192_171)
    if not problem or "25.0" not in problem:
        fails.append("the real 26 MB live-measured size was NOT caught: %r"
                     % problem)

    # 2. The real, live fix: the deck as it ships now, re-exported at
    #    210 dpi / quality 72.
    problem = preflight.check_deck_pdf_size_budget(7_907_789)
    if problem:
        fails.append("the real 7.5 MB fixed size was wrongly flagged: %s"
                     % problem)

    # 3. Boundary: exactly at budget is fine, one byte over is not.
    if preflight.check_deck_pdf_size_budget(8 * MB):
        fails.append("exactly-at-budget wrongly flagged")
    if not preflight.check_deck_pdf_size_budget(8 * MB + 1):
        fails.append("one byte over budget NOT caught")

    # 4. A small, honest file is fine.
    if preflight.check_deck_pdf_size_budget(1 * MB):
        fails.append("a small, honest file wrongly flagged")

    if fails:
        print("FAIL")
        for f in fails:
            print("  " + f)
        return 1
    print("  %d case(s) passed: real live defect caught, real live fix "
          "clean, boundary exact, no false positive on a small file"
          % 4)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
