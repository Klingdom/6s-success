#!/usr/bin/env python3
"""
Prove ops/send_questions.py's SITE STATUS block is live-checked, not
hardcoded, and never claims deploys are automatic.

Found 2026-09-09, reading the file cold: it hardcoded "10 of 10 checks
passing, TLS valid" (never measured at send time) and "Deploys are
automatic: push to main and the host pulls within five minutes," which is
false against DEPLOYMENT.md's own canonical description ("The one step no
autonomous session can perform is the Redeploy click"). Both would have told
Phil something this repository could not have verified in that run, the
exact class of defect gate_send_questions_current already exists to catch
for three other stale claims in this same file. Fixed by deriving the line
from ops/deploy_freshness.check()'s live verdict, honestly "unknown" when
the site could not be reached, and by correcting the deploy claim.

Run:  python ops/tests/test_send_questions.py
"""
import os
import sys
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import send_questions as sq                                      # noqa: E402
import deploy_freshness                                          # noqa: E402


def main() -> int:
    fails = []

    # 1. Unreachable site: must read as unknown, never as healthy.
    with mock.patch.object(deploy_freshness, "check",
                            return_value={"reachable": False, "verdict": "unknown"}):
        lines = sq.site_status_lines()
    text = "\n".join(lines)
    if "could not be reached" not in text or "unknown" not in text:
        fails.append("unreachable case did not read as unknown: %r" % text)
    if "checks passing" in text or "is live," in text:
        fails.append("unreachable case must not claim health: %r" % text)

    # 2. Reachable and current: says so plainly.
    with mock.patch.object(deploy_freshness, "check",
                            return_value={"reachable": True, "verdict": "current"}):
        lines = sq.site_status_lines()
    text = "\n".join(lines)
    if "current build" not in text:
        fails.append("current case did not say so: %r" % text)

    # 3. Reachable but stale: the real defect deploy_freshness.py exists to
    #    catch (a green HTTP check on an out-of-date build) must be visible
    #    here too, not silently read as fine.
    with mock.patch.object(deploy_freshness, "check",
                            return_value={"reachable": True, "verdict": "stale"}):
        lines = sq.site_status_lines()
    text = "\n".join(lines)
    if "OUT-OF-DATE" not in text:
        fails.append("stale case did not say so: %r" % text)

    # 4. The exact regression: no path may claim deploys are automatic, and
    #    every path must mention the real Redeploy-click mechanism.
    for verdict in ({"reachable": True, "verdict": "current"},
                     {"reachable": True, "verdict": "stale"},
                     {"reachable": False, "verdict": "unknown"}):
        with mock.patch.object(deploy_freshness, "check", return_value=verdict):
            text = "\n".join(sq.site_status_lines())
        if "automatic" in text and "still needs a Redeploy click" not in text:
            fails.append("deploy claim regressed for %r: %r" % (verdict, text))
        if "Redeploy click" not in text:
            fails.append("missing the real deploy mechanism for %r" % verdict)

    # 5. A raised exception (deploy_freshness itself broken, or genuinely no
    #    network) must degrade to unknown, never raise out of build().
    with mock.patch.object(deploy_freshness, "check", side_effect=RuntimeError("boom")):
        try:
            text = "\n".join(sq.site_status_lines())
        except Exception as e:                                   # noqa: BLE001
            fails.append("site_status_lines() raised on a broken check: %r" % e)
            text = ""
    if text and "could not be reached" not in text:
        fails.append("broken-check case did not degrade to unknown: %r" % text)

    # 6. build() itself must not crash and must fold the block in.
    with mock.patch.object(deploy_freshness, "check",
                            return_value={"reachable": True, "verdict": "current"}):
        full = sq.build()
    if "SITE STATUS" not in full or "current build" not in full:
        fails.append("build() did not include the live-checked status block")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: send_questions site-status honesty, 6/6 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
