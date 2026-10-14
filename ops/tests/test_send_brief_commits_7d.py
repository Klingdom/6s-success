#!/usr/bin/env python3
"""
The morning brief must never print Python's own None where a measurement is
missing.

Found 2026-10-14, scheduled operator cycle, reading send_brief.py cold: a
real ops/state.json generated the same day carried commits_7d: null (the
repo was shallow and could not be unshallowed when dashboard.py ran, which
dashboard.py's own commits_7d_text() handles honestly everywhere else:
"unknown (shallow clone, could not verify)"). send_brief.py skipped that
helper and interpolated s['commits_7d'] straight into both the plain-text
and HTML bodies, so the brief Phil reads every morning would have read
"Commits   None in seven days" verbatim, the exact "unchecked read as a
value" shape CLAUDE.md 0.4 and dashboard.py's own docstrings warn about.

No network, no mail credential: build() is pure given a state dict.

Run:  python ops/tests/test_send_brief_commits_7d.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import send_brief as SB                                        # noqa: E402

STATE = {
    "overall": "YELLOW", "overall_why": "2 P0 items still open.",
    "revenue_text": "$0 of $20,000 target (0.0%)",
    "customers_text": "0", "email_list": 0, "can_take_payment": True,
    "constraint": "Discovery, not what can be bought, is the constraint.",
    "issues_available": True, "needs_phil": 0, "issues": [],
    "chapters": 50, "book_sellable": True, "rooms": 20, "zones": 114,
    "commits_7d": None, "generated": "2026-10-14 17:35",
}


def main() -> int:
    fails = []
    subject, text, html = SB.build(dict(STATE))
    if "None" in text:
        fails.append("plain-text brief contains the literal word None: %r"
                     % next(l for l in text.splitlines() if "None" in l))
    if "unknown (shallow clone" not in text:
        fails.append("plain-text brief does not explain the missing commit count")
    if "None" in html:
        fails.append("html brief contains the literal word None")
    if "unknown (shallow clone" not in html:
        fails.append("html brief does not explain the missing commit count")

    # A real count must still render as itself, not as the fallback string.
    present = dict(STATE, commits_7d=42)
    _, text2, html2 = SB.build(present)
    if "42" not in text2 or "42" not in html2:
        fails.append("a real commits_7d value did not render")
    if "unknown" in text2.split("Commits")[1][:60]:
        fails.append("a real commits_7d value was reported as unknown")

    for f in fails:
        print("FAIL", f)
    print("ok" if not fails else "%d failure(s)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
