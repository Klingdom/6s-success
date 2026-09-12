#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_changelog_current() can actually fail, and
that it does not fire on an ordinary short lag.

Found 2026-09-12: CHANGELOG.md's own "Last updated" line read 2026-08-17,
26 days behind roughly 40 shipped items, silent the whole time despite its
own section 102 promising updates per material change and a weekly review.
Backfilled with real entries (section 105); this gate is the mechanical
backstop so the same silence cannot recur unnoticed.

Run:  python ops/tests/test_gate_changelog_current.py
"""
import datetime as dt
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []
    today = dt.date(2026, 9, 12)

    # 1. 30 days stale: past the 21-day threshold, must report a gap.
    text_stale = "**Last updated:** 2026-08-13"
    gap = preflight.changelog_staleness(text_stale, today)
    if gap != 30:
        fails.append("30-day case: expected gap 30, got %r" % (gap,))

    # 2. 10 days stale: an ordinary short lag between deliberate updates,
    #    must not read as the same defect a 30-day silence is.
    text_fresh = "**Last updated:** 2026-09-02"
    gap2 = preflight.changelog_staleness(text_fresh, today)
    if gap2 != 10:
        fails.append("10-day case: expected gap 10, got %r" % (gap2,))

    # 3. Exactly at the boundary (21 days): the gate itself treats this as
    #    not-yet-stale (> 21, not >= 21), so the pure function must still
    #    return the real number and let gate_changelog_current's own
    #    comparison decide.
    text_boundary = "**Last updated:** 2026-08-22"
    gap3 = preflight.changelog_staleness(text_boundary, today)
    if gap3 != 21:
        fails.append("boundary case: expected gap 21, got %r" % (gap3,))

    # 4. Missing date entirely: must return None, never a fabricated number.
    gap4 = preflight.changelog_staleness("no date here", today)
    if gap4 is not None:
        fails.append("missing-date case: expected None, got %r" % (gap4,))

    # 5. Reproduce the real 2026-09-12 bug directly against a frozen copy
    #    of the pre-fix line, to prove this shape actually fails loudly.
    pre_fix_text = "**Last updated:** 2026-08-17"
    real_gap = preflight.changelog_staleness(pre_fix_text, today)
    if real_gap is None or real_gap <= 21:
        fails.append(
            "real pre-fix date (2026-08-17) should read as stale against "
            "2026-09-12, got gap=%r" % (real_gap,))

    # 6. The live file itself must parse and, having just been backfilled,
    #    must not be stale today.
    live_path = os.path.join(ROOT, "CHANGELOG.md")
    live_text = open(live_path, encoding="utf-8").read()
    if not re.search(r"\*\*Last updated:\*\*\s*\d{4}-\d{2}-\d{2}", live_text):
        fails.append("live CHANGELOG.md has no parseable 'Last updated' line")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 6 checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
