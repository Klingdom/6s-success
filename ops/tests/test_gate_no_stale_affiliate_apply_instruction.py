#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_no_stale_affiliate_apply_instruction() catches
OWNER-ACTIONS.md and BACKLOG-2026-H2.md telling Phil to go apply to, confirm
or finish an affiliate application today, and catches either document naming
a declined programme as a near-term fit.

Found 2026-09-17, this operator, the end-to-end read of BACKLOG-2026-H2.md
the PM check-in handed off. Both documents' affiliate sections were written
2026-08 to 2026-09-01, before PLAN-AFFILIATE-MONETISATION.md (Phil, finalised
2026-09-07) held every affiliate application until trigger T2 fires.
GOALS.md's O4 already carried the hold (gate_no_stale_affiliate_blocker
protects it); neither sibling document had been told. Home Depot's inclusion
as a "near-term fit" was independently wrong: it is one of the five
Impact-routed programmes declined 29 August.

Run:  python ops/tests/test_gate_no_stale_affiliate_apply_instruction.py
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

ACCOUNTS = {"home-depot": {"status": "declined"},
            "amazon": {"status": "verification pending"},
            "etsy": {"status": "verification pending"}}


def _run(owner_text, h2_text, accounts=ACCOUNTS):
    tmp = tempfile.mkdtemp()
    try:
        io.open(os.path.join(tmp, "OWNER-ACTIONS.md"), "w",
                encoding="utf-8").write(owner_text)
        io.open(os.path.join(tmp, "BACKLOG-2026-H2.md"), "w",
                encoding="utf-8").write(h2_text)
        os.makedirs(os.path.join(tmp, "ops"))
        io.open(os.path.join(tmp, "ops", "affiliate-accounts.json"), "w",
                encoding="utf-8").write(json.dumps(accounts))
        old_root = preflight.ROOT
        preflight.ROOT = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_no_stale_affiliate_apply_instruction()
            return list(preflight.FAIL), list(preflight.WARN)
        finally:
            preflight.ROOT = old_root
    finally:
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. The real OWNER-ACTIONS.md regression shape: the retired
    #    instruction phrase reappears.
    r, w = _run(
        "### 4. Four affiliate applications\n"
        "**What to do:** open those four emails from 29 August and finish "
        "each one.\n",
        "nothing relevant here\n")
    if not r or "no-stale-affiliate-apply-instruction" != r[0][0]:
        fails.append("the OWNER-ACTIONS.md regression was not caught: %r" % (r,))

    # 2. The real BACKLOG-2026-H2.md regression shape: a declined programme
    #    named as a near-term fit.
    r, w = _run(
        "nothing relevant\n",
        "9. **Apply to retail affiliate programmes.** Etsy, Office Depot "
        "and the legacy Home Depot programme look like the best near-term "
        "fits.\n")
    if not r or "no-stale-affiliate-apply-instruction" != r[0][0]:
        fails.append("the BACKLOG-2026-H2.md regression was not caught: %r" % (r,))
    elif "Home Depot" not in r[0][1]:
        fails.append("failure message did not name the declined programme: "
                      "%r" % (r[0][1],))

    # 3. A dated correction narrating its own old, wrong wording in quotes
    #    must not trip this (the real fixed BACKLOG-2026-H2.md shape).
    r, w = _run(
        "nothing relevant\n",
        '9. **Apply to retail affiliate programmes: on hold.** This item '
        'used to name Home Depot as "the best near-term fits". Now held '
        'until T2 fires.\n')
    if r:
        fails.append("a quoted historical citation was wrongly flagged: %r" % (r,))

    # 4. Both documents genuinely clean (the real fixed shape): no failure.
    r, w = _run(
        "### 4. Three affiliate applications, on hold until T2 fires.\n"
        "**What to do: nothing, on purpose, until the T2 trigger fires.**\n",
        "9. **Apply to retail affiliate programmes: on hold.** held until "
        "T2 fires.\n")
    if r:
        fails.append("genuinely fixed documents wrongly flagged: %r" % (r,))

    # 5. No programme is actually declined: naming one as a fit is not an
    #    error (nothing to contradict), so no failure from that half.
    r, w = _run(
        "nothing relevant\n",
        "9. **Apply to retail affiliate programmes.** Home Depot looks "
        "like the best near-term fit.\n",
        accounts={"home-depot": {"status": "verification pending"}})
    if r:
        fails.append("a non-declined programme named as a fit was wrongly "
                      "flagged: %r" % (r,))

    # 6. The real, committed documents: clean, now that both have been
    #    corrected in place.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_no_stale_affiliate_apply_instruction()
    if preflight.FAIL:
        fails.append("the real committed documents failed: %r"
                     % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_no_stale_affiliate_apply_instruction, 6/6 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
