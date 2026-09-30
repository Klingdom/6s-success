#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_affiliate_trigger_citation_current() catches
GOALS.md or OWNER-ACTIONS.md citing a stale T2 affiliate-trigger click count
against ops/state.json's own live reading.

Found 2026-09-30, scheduled operator: both files cited "reading 0 of 60 as
of 2026-09-09" for ops/check_affiliate_trigger.py's T2 trigger, three weeks
after a session with real database access last measured it at "1 of 60"
(ops/state.json's affiliate_trigger, 2026-09-30 12:25). Corrected by hand;
this gate stops it drifting back.

Run:  python ops/tests/test_gate_affiliate_trigger_citation_current.py
"""
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

GOALS_TEMPLATE = (
    "when trigger T2 fires (60 real outbound retailer clicks in a\n"
    "trailing 90 days, `ops/check_affiliate_trigger.py`). `ops/state.json`'s "
    "own\n`affiliate_trigger`, measured today, reads **%s of 60\noutbound "
    "retailer click(s)** in the last 90 days.\n"
)


def _run(state_value, goals_n, owner_n=None):
    tmp = tempfile.mkdtemp()
    io.open(os.path.join(tmp, "GOALS.md"), "w", encoding="utf-8").write(
        GOALS_TEMPLATE % goals_n)
    if owner_n is not None:
        io.open(os.path.join(tmp, "OWNER-ACTIONS.md"), "w",
                encoding="utf-8").write(GOALS_TEMPLATE % owner_n)
    os.makedirs(os.path.join(tmp, "ops"), exist_ok=True)
    json.dump({"affiliate_trigger_last_measured":
               "T2 not fired: %s of 60 outbound retailer click(s) in the "
               "last 90 days" % state_value},
              io.open(os.path.join(tmp, "ops", "state.json"), "w",
                      encoding="utf-8"))
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_affiliate_trigger_citation_current()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. The real regression shape: GOALS.md cites 0, state.json now says 1.
    #    Must fail.
    r, w = _run(state_value=1, goals_n=0)
    if not r or "affiliate-trigger-citation-current" != r[0][0]:
        fails.append("the real regression shape was not caught: %r" % (r,))

    # 2. GOALS.md and OWNER-ACTIONS.md both agree with state.json: no
    #    failure.
    r, w = _run(state_value=3, goals_n=3, owner_n=3)
    if r:
        fails.append("genuine agreement wrongly flagged: %r" % (r,))

    # 3. Only OWNER-ACTIONS.md is stale, GOALS.md agrees: must still fail,
    #    naming the stale file.
    r, w = _run(state_value=5, goals_n=5, owner_n=2)
    if not r or "OWNER-ACTIONS.md" not in r[0][1]:
        fails.append("a stale OWNER-ACTIONS.md alone was not caught: %r"
                     % (r,))

    # 4. state.json has no affiliate_trigger reading at all: silent, never a
    #    crash or a false fail.
    tmp = tempfile.mkdtemp()
    io.open(os.path.join(tmp, "GOALS.md"), "w", encoding="utf-8").write(
        GOALS_TEMPLATE % 0)
    os.makedirs(os.path.join(tmp, "ops"), exist_ok=True)
    json.dump({}, io.open(os.path.join(tmp, "ops", "state.json"), "w",
                          encoding="utf-8"))
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_affiliate_trigger_citation_current()
        r, w = list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root
        shutil.rmtree(tmp)
    if r or w:
        fails.append("a missing state.json reading was not silent: %r/%r"
                     % (r, w))

    # 5. The real, committed documents: clean, now that both files have been
    #    corrected in place.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_affiliate_trigger_citation_current()
    if preflight.FAIL:
        fails.append("the real committed documents failed: %r"
                     % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_affiliate_trigger_citation_current, 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
