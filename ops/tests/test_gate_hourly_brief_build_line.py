#!/usr/bin/env python3
"""
The hourly BUILD line and send_brief's subject must not report a real zero
when GitHub was actually unreachable.

dashboard.py sets open_p0 and needs_phil to 0, not missing, the same moment
it sets issues_available False, so a bare .get(key, '?') on either field
never sees its own fallback: the one credentialed hourly mail Phil reads
would have shown "P0 0   needs Phil 0" on a run where GitHub answered
nothing, a confident false all-clear on exactly the field CLAUDE.md 0.4
says must never default to passing. ops/send_brief.py (currently unused by
any scheduled workflow, but a real, cold-read defect all the same) had the
identical shape in its subject line, the one thing a locked phone screen
shows without opening the mail.

No network, no key, no money: both functions are pure given a state dict.

Run:  python ops/tests/test_gate_hourly_brief_build_line.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import hourly_brief as hb   # noqa: E402
import send_brief as sb     # noqa: E402

REACHABLE = {"overall": "YELLOW", "open_p0": 3, "needs_phil": 5,
             "commits_7d": 403, "issues_available": True}
UNREACHABLE = {"overall": "YELLOW", "open_p0": 0, "needs_phil": 0,
                "commits_7d": 403, "issues_available": False}

SB_BASE = {"overall": "YELLOW", "overall_why": "test", "revenue_text": "$0",
           "customers_text": "0", "email_list": 0, "can_take_payment": True,
           "constraint": "test", "chapters": 50, "book_sellable": True,
           "rooms": 20, "zones": 114, "commits_7d": 1,
           "generated": "2026-01-01 00:00"}


def main() -> int:
    fails = []

    line = hb.build_line(REACHABLE)
    if "P0 3" not in line:
        fails.append(f"reachable case: open_p0=3 missing from {line!r}")
    if "needs Phil 5" not in line:
        fails.append(f"reachable case: needs_phil=5 missing from {line!r}")
    if "commits 7d 403" not in line:
        fails.append(f"reachable case: commits_7d=403 missing from {line!r}")

    line = hb.build_line(UNREACHABLE)
    if "P0 0" in line or "needs Phil 0" in line:
        fails.append(f"unreachable case: reported a real 0 instead of "
                     f"unknown: {line!r}")
    if "unknown" not in line.lower():
        fails.append(f"unreachable case: did not say unknown: {line!r}")

    reachable_s = dict(SB_BASE, needs_phil=5, issues_available=True, issues=[])
    subj = sb.build(reachable_s)[0]
    if "5 need you" not in subj:
        fails.append(f"reachable case: send_brief subject missing '5 need "
                     f"you': {subj!r}")

    unreachable_s = dict(SB_BASE, needs_phil=0, issues_available=False, issues=[])
    subj = sb.build(unreachable_s)[0]
    if "0 need you" in subj:
        fails.append(f"unreachable case: send_brief subject reported a "
                     f"real '0 need you': {subj!r}")
    if "unreachable" not in subj.lower() and "?" not in subj:
        fails.append(f"unreachable case: send_brief subject does not flag "
                     f"GitHub as unreachable: {subj!r}")

    for f in fails:
        print("FAIL", f)
    print("ok" if not fails else "%d failure(s)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
