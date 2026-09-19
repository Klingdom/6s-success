#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_dashboard_covers_top_owner_actions() catches
OWNER-ACTIONS.md's own top-ranked "Start here" items going unmentioned in
EXECUTIVE-DASHBOARD-LIVE.md's "What needs you" section.

Found 2026-09-19, PM check-in: the dashboard is the one document CLAUDE.md
24 says exists specifically so the owner does not need to inspect dozens of
operational files, yet "What needs you" only ever listed a stale deployment
and the GitHub decision queue, never Google Search Console verification,
YouTube upload authorisation or the Stripe business description, the three
items OWNER-ACTIONS.md's own "Start here" table ranks above everything else
on that page. The identical gap in ops/send_questions.py was fixed
2026-09-18; this proves the same fix one document over, and that a future
edit dropping the section again gets caught.

Run:  python ops/tests/test_gate_dashboard_covers_top_owner_actions.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

START_HERE = """### Start here: 20 minutes, in this order

Some intro paragraph that explains why these three come first.

| # | Do | Time | Why it is first |
|---|---|---|---|
| **1a** | Verify the site in Google Search Console | 3 min | some reason |
| **1** | Authorise YouTube uploads | 5 min | some reason |
| **1d** | Paste the business description into Stripe | 2 min | some reason |

The rest of this file stays as it is, in its original order.
"""

DASH_ALL = """# 6S Success: Live Executive Dashboard

## The 60-second read

some table

## What needs you

- **Redeploy the site.** some copy.
- **Verify the site in Google Search Console** (3 min). some reason.
- **Authorise YouTube uploads** (5 min). some reason.
- **Paste the business description into Stripe** (2 min). some reason.
- **#33** Decide: something

## Open issues

some table
"""

DASH_MISSING_TWO = """# 6S Success: Live Executive Dashboard

## What needs you

- **Redeploy the site.** some copy.
- **Verify the site in Google Search Console** (3 min). some reason.
- **#33** Decide: something

## Open issues

some table
"""


def _run(oa_body, dash_body):
    tmp = tempfile.mkdtemp()
    if oa_body is not None:
        io.open(os.path.join(tmp, "OWNER-ACTIONS.md"), "w",
                encoding="utf-8").write(oa_body)
    if dash_body is not None:
        io.open(os.path.join(tmp, "EXECUTIVE-DASHBOARD-LIVE.md"), "w",
                encoding="utf-8").write(dash_body)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_dashboard_covers_top_owner_actions()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. All three top-ranked items mentioned: no failure.
    r, w = _run(START_HERE, DASH_ALL)
    if r:
        fails.append("a dashboard covering all three was wrongly "
                     "flagged: %r" % (r,))

    # 2. The exact real-world regression: YouTube and Stripe missing.
    r, w = _run(START_HERE, DASH_MISSING_TWO)
    if not r:
        fails.append("missing YouTube/Stripe items were not caught at all")
    else:
        msg = r[0][1]
        if "Authorise YouTube uploads" not in msg:
            fails.append("YouTube omission not named: %r" % msg)
        if "Paste the business description into Stripe" not in msg:
            fails.append("Stripe description omission not named: %r" % msg)

    # 3. OWNER-ACTIONS.md missing entirely: unchecked warning, not a failure.
    r, w = _run(None, DASH_ALL)
    if r:
        fails.append("absent OWNER-ACTIONS.md should warn, not fail: %r" % (r,))
    if not w:
        fails.append("absent OWNER-ACTIONS.md produced no warning at all")

    # 4. The dashboard missing entirely: same, warn not fail.
    r, w = _run(START_HERE, None)
    if r:
        fails.append("absent dashboard should warn, not fail: %r" % (r,))
    if not w:
        fails.append("absent dashboard produced no warning at all")

    # 5. The dashboard present but with no "What needs you" section at all:
    #    warn, not fail, since this is a document-shape gap.
    r, w = _run(START_HERE, "# 6S Success\n\n## Something else\n\nno needs "
                             "section here\n\n## Open issues\n\nx\n")
    if r:
        fails.append("a missing \"What needs you\" section should warn, "
                     "not fail: %r" % (r,))
    if not w:
        fails.append("a missing \"What needs you\" section produced no "
                     "warning at all")

    # 6. The real, committed files: clean today.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_dashboard_covers_top_owner_actions()
    if preflight.FAIL:
        fails.append("the real committed files failed: %r" % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: dashboard-covers-owner-actions, 6/6 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
