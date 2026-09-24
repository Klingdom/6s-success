#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_dashboard_owner_actions_traffic_citation_
current() catches a real regression found live 2026-09-24, PM check-in:
OWNER-ACTIONS.md's "Last measured" header was reworded from "traffic
re-measured by a direct database read: N visitors/N visits/30 days" (the
exact phrase dashboard._owner_actions_traffic_citation() requires) to
"traffic re-read (N visitors/N visits/30 days, ...)". The number stayed
right there in the text, so nothing reading the file by eye would notice
anything wrong, but the parser that exists specifically to let the
dashboard prefer a fresher OWNER-ACTIONS.md reading over a stale carried
one returned None, silently, and EXECUTIVE-DASHBOARD-LIVE.md kept showing
an older traffic figure with no warning anywhere.

Also runs against the real, committed OWNER-ACTIONS.md, so a future
rewording of this header ships this test failing, not silently.

Run:  python ops/tests/test_gate_dashboard_owner_actions_traffic_citation_current.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402

GOOD = ("# Owner actions\n\n**Last measured:** 2026-09-23 12:50 UTC, traffic "
        "re-measured by a direct database read: 68 visitors/160 visits/30 "
        "days (2.3 a day). Production deployed and current.\n")

BAD_REWORDED = ("# Owner actions\n\n**Last measured:** 2026-09-23 12:50 UTC, "
                "traffic re-read (68 visitors/160 visits/30 days, 2.3 a "
                "day; trailing week 12 after 10, 14, 18). Production "
                "deployed and current.\n")

NO_TRAFFIC_CITED = ("# Owner actions\n\n**Last measured:** 2026-09-23, item "
                     "1h resolved. Nothing traffic-related in this header "
                     "today.\n")

NO_HEADER = "# Owner actions\n\nNo Last measured header at all.\n"


def _write(d, name, text):
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def main() -> int:
    fails = []
    with tempfile.TemporaryDirectory() as d:
        # 1. The exact defect shape: reworded header, real regression.
        bad_fp = _write(d, "bad.md", BAD_REWORDED)
        preflight.FAIL.clear()
        preflight.gate_dashboard_owner_actions_traffic_citation_current(bad_fp)
        if len(preflight.FAIL) != 1:
            fails.append(f"expected exactly 1 FAIL for the reworded header, "
                          f"got {preflight.FAIL!r}")
        elif "68 visitors" not in preflight.FAIL[0][1] and \
                "could not parse" not in preflight.FAIL[0][1]:
            fails.append(f"FAIL message did not explain the parse failure: "
                          f"{preflight.FAIL[0]!r}")

        # 2. The fix: correctly phrased header, must pass clean.
        good_fp = _write(d, "good.md", GOOD)
        preflight.FAIL.clear()
        preflight.gate_dashboard_owner_actions_traffic_citation_current(good_fp)
        if preflight.FAIL:
            fails.append(f"correctly phrased header must not fail: "
                          f"{preflight.FAIL!r}")

        # 3. A header with no traffic reading at all: nothing to catch,
        #    must not fail (the parser correctly returning None here is
        #    not a defect).
        none_fp = _write(d, "none.md", NO_TRAFFIC_CITED)
        preflight.FAIL.clear()
        preflight.gate_dashboard_owner_actions_traffic_citation_current(none_fp)
        if preflight.FAIL:
            fails.append(f"a header naming no traffic reading must not "
                          f"fail: {preflight.FAIL!r}")

        # 4. No "Last measured" header at all: same, nothing to catch.
        noheader_fp = _write(d, "noheader.md", NO_HEADER)
        preflight.FAIL.clear()
        preflight.gate_dashboard_owner_actions_traffic_citation_current(noheader_fp)
        if preflight.FAIL:
            fails.append(f"a missing header must not fail: {preflight.FAIL!r}")

        # 5. A missing file entirely: must not fail (unmeasurable, not
        #    a defect in this file).
        preflight.FAIL.clear()
        preflight.gate_dashboard_owner_actions_traffic_citation_current(
            os.path.join(d, "does-not-exist.md"))
        if preflight.FAIL:
            fails.append(f"a missing file must not fail: {preflight.FAIL!r}")

    # 6. The real, committed OWNER-ACTIONS.md must parse clean today.
    preflight.FAIL.clear()
    preflight.gate_dashboard_owner_actions_traffic_citation_current()
    if preflight.FAIL:
        fails.append(f"the real committed OWNER-ACTIONS.md must parse "
                      f"clean: {preflight.FAIL!r}")

    if fails:
        print("FAIL:")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: 6/6 cases (fail-then-pass proved against the real defect shape)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
