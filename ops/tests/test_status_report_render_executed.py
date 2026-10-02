#!/usr/bin/env python3
"""
Prove ops/status_report.py's render() prints the real "executed" count in
the HTML summary table and the email subject, not a hardcoded 0.

Found 2026-10-02, second-pass cold-reading the 2026-09-26-dated ops/*.py
tier (ops/cold_read_ledger.py) per CLAUDE.md step 5d. test_status_report_
executed_count.py (2026-09-26) already fixed gather()'s dict to compute
`"executed": executed_count(exp)` instead of a bare 0 literal, but that fix
never reached render(): the HTML table's "Experiments run" row and the
email subject line both still hardcoded `f"0 of {len(x['designed'])}"`,
while the plain-text body (line ~537, `x['executed']`) read the real value
correctly. The two have agreed by coincidence every day since, because
every real EXPERIMENTS.md entry has stayed State: IDEA; the moment one
moves to RUNNING or DONE, the HTML table and subject would silently keep
reporting 0 while the plain-text body (and reality) report otherwise, the
exact "corrected source, unrederived artifact" defect class CLAUDE.md
0.4 and this repository's own BACKLOG-2026-09-07.md section 7 both name as
the dominant one here. Fixed by pointing both at x['executed'].

Run:  python ops/tests/test_status_report_render_executed.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import status_report as sr                                       # noqa: E402


def main() -> int:
    fails = []

    d = sr.gather()
    # Force a nonzero executed count that disagrees with "designed" length,
    # so a stale "0 of N" literal cannot coincidentally look correct.
    d["experiments"]["designed"] = [("EXP-0001", "A"), ("EXP-0002", "B"), ("EXP-0003", "C")]
    d["experiments"]["executed"] = 2

    subject, text, html = sr.render(d)

    if "2 of 3 experiments running" not in subject:
        fails.append("subject did not report the real executed count: %r" % (subject,))
    if "0 of 3 experiments" in subject:
        fails.append("subject still carries the stale hardcoded 0: %r" % (subject,))

    if "2 of 3 designed" not in html:
        fails.append("HTML summary table did not report the real executed "
                      "count in the 'Experiments run' row")
    if "0 of 3 designed" in html:
        fails.append("HTML summary table still carries the stale "
                      "hardcoded 0")

    # The plain-text body already read this correctly before this fix;
    # confirm all three surfaces now agree rather than just the two fixed.
    if "Executed                2" not in text:
        fails.append("plain-text body's own Executed line disagrees with "
                      "the forced executed=2 (sanity check on the fixture "
                      "itself, not the fix)")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: status_report.py render() experiment count, subject/HTML/"
          "text all agree, 3/3 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
