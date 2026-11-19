#!/usr/bin/env python3
"""
Prove ops/preflight.py's newest_nightly_log_entry_missing_handoff_marker()
catches a newest ops/NIGHTLY-LOG.md entry that was hand-edited straight
into the file rather than written by `python ops/nightly_log.py
--handoff ...` (no HANDOFF-FILES: line at all).

Found live 2026-11-19: the two newest entries at the time both skipped
the marker, a regression back to the exact hand-edited free-text shape
the marker was built to retire, and the free-text fallback it bypasses
promptly misfired on the very next entry (see
cold_read_handoff_stale_files()'s own long docstring in ops/preflight.py
for that history). This tests the pure logic with synthetic text, so it
never touches the real committed log.

Run:  python ops/tests/test_gate_nightly_log_handoff_marker_present.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

HEADER = "# Nightly log\n\nOne entry per unattended pass, newest first.\n\n"


def main() -> int:
    fails = []
    f = preflight.newest_nightly_log_entry_missing_handoff_marker

    # 1. The real defect shape: newest entry has no HANDOFF-FILES line
    #    at all (hand-edited).
    log = HEADER + (
        "## 2026-11-19, cycle\n\n"
        "**Next:** re-check `room_guide_underperformance.py` for the "
        "next genuinely fresh row.\n\n"
        "## 2026-11-18, older cycle\n\n"
        "HANDOFF-FILES: none\n\n"
        "Nothing new.\n"
    )
    if f(log) is not True:
        fails.append("a newest entry with no HANDOFF-FILES line should "
                      "be flagged missing")

    # 2. Same newest entry, now carrying the marker ("none"): no longer
    #    missing, regardless of what an older entry does.
    log_fixed = HEADER + (
        "## 2026-11-19, cycle\n\n"
        "HANDOFF-FILES: none\n\n"
        "**Next:** re-check `room_guide_underperformance.py` for the "
        "next genuinely fresh row.\n\n"
        "## 2026-11-18, older cycle\n\n"
        "Nothing new.\n"
    )
    if f(log_fixed) is not False:
        fails.append("a newest entry carrying HANDOFF-FILES: none "
                      "should not be flagged missing")

    # 3. Same newest entry, marker present with real file names: still
    #    not missing (presence is all this checks; correctness is
    #    cold_read_handoff_stale_files()'s own job).
    log_named = HEADER + (
        "## 2026-11-19, cycle\n\n"
        "HANDOFF-FILES: `ops/dashboard.py`\n\n"
        "**Next:** read it.\n"
    )
    if f(log_named) is not False:
        fails.append("a newest entry carrying a populated HANDOFF-FILES "
                      "line should not be flagged missing")

    # 4. An older entry's marker must not satisfy the check for a newer
    #    entry that has none: only the newest (first) block counts.
    log_old_only = HEADER + (
        "## 2026-11-19, cycle\n\n"
        "**Next:** nothing new.\n\n"
        "## 2026-11-18, older cycle\n\n"
        "HANDOFF-FILES: none\n\n"
        "Older work.\n"
    )
    if f(log_old_only) is not True:
        fails.append("an older entry's marker must not satisfy the "
                      "newest entry's own missing check")

    # 5. Empty log / no blocks at all: nothing to flag.
    if f(HEADER) is not False:
        fails.append("a log with no entries should not be flagged "
                      "missing")

    # 6. The real, currently-committed log's newest entry, as of
    #    fixing this gate, must itself carry the marker (this test
    #    landed alongside the fix that makes that true).
    log_path = os.path.join(ROOT, "ops", "NIGHTLY-LOG.md")
    real_log = open(log_path, encoding="utf-8").read()
    if f(real_log) is not False:
        fails.append("the real NIGHTLY-LOG.md's newest entry is still "
                      "missing its own HANDOFF-FILES line")

    if fails:
        print("FAIL")
        for fmsg in fails:
            print("  -", fmsg)
        return 1
    print("OK  newest_nightly_log_entry_missing_handoff_marker: 6/6 cases pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
