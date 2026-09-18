#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_send_questions_covers_top_owner_actions()
catches OWNER-ACTIONS.md's own top-ranked "Start here" items going
unmentioned in ops/send_questions.py's BLOCKING list.

Found 2026-09-18, reading ops/send_questions.py cold in the standing
low-mention ops/*.py lane. OWNER-ACTIONS.md's own "Start here" table ranked
Google Search Console, authorising YouTube uploads and pasting Stripe's
business description as the three highest-value single actions on the whole
page, and separately called YouTube "the biggest single lever on the
business right now". send_questions.py's BLOCKING list, the email whose own
opening line claims "This is only the list that cannot" be done without
Phil, had Search Console but not the other two. Fixed by adding both;
this gate stops the same drift recurring the next time the ranking moves.

Run:  python ops/tests/test_gate_send_questions_covers_top_owner_actions.py
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

BLOCKING_ALL = """BLOCKING = [
    ("Listmonk", "what", "why", "cost"),
    ("Google Search Console", "what", "why", "cost"),
    ("Authorise YouTube uploads", "what", "why", "cost"),
    ("Paste the business description into Stripe", "what", "why", "cost"),
]
"""

BLOCKING_MISSING_TWO = """BLOCKING = [
    ("Listmonk", "what", "why", "cost"),
    ("Google Search Console", "what", "why", "cost"),
]
"""


def _run(oa_body, sq_blocking):
    tmp = tempfile.mkdtemp()
    if oa_body is not None:
        io.open(os.path.join(tmp, "OWNER-ACTIONS.md"), "w",
                encoding="utf-8").write(oa_body)
    opsdir = os.path.join(tmp, "ops")
    os.makedirs(opsdir, exist_ok=True)
    if sq_blocking is not None:
        io.open(os.path.join(opsdir, "send_questions.py"), "w",
                encoding="utf-8").write(sq_blocking)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_send_questions_covers_top_owner_actions()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. All three top-ranked items mentioned: no failure.
    r, w = _run(START_HERE, BLOCKING_ALL)
    if r:
        fails.append("a BLOCKING list covering all three was wrongly "
                     "flagged: %r" % (r,))

    # 2. The exact real-world regression: YouTube and Stripe missing.
    r, w = _run(START_HERE, BLOCKING_MISSING_TWO)
    if not r:
        fails.append("missing YouTube/Stripe items were not caught at all")
    else:
        msg = r[0][1]
        if "Authorise YouTube uploads" not in msg:
            fails.append("YouTube omission not named: %r" % msg)
        if "Paste the business description into Stripe" not in msg:
            fails.append("Stripe description omission not named: %r" % msg)

    # 3. OWNER-ACTIONS.md missing entirely: unchecked warning, not a failure
    #    (this repository never reports unknown as passing, but this is a
    #    document-shape gap, not a live defect, so it warns rather than fails).
    r, w = _run(None, BLOCKING_ALL)
    if r:
        fails.append("absent OWNER-ACTIONS.md should warn, not fail: %r" % (r,))
    if not w:
        fails.append("absent OWNER-ACTIONS.md produced no warning at all")

    # 4. send_questions.py missing entirely: same, warn not fail.
    r, w = _run(START_HERE, None)
    if r:
        fails.append("absent send_questions.py should warn, not fail: %r" % (r,))
    if not w:
        fails.append("absent send_questions.py produced no warning at all")

    # 5. The real, committed files: clean today.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_send_questions_covers_top_owner_actions()
    if preflight.FAIL:
        fails.append("the real committed files failed: %r" % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: send-questions-covers-owner-actions, 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
