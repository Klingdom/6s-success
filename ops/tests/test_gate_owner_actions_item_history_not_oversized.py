#!/usr/bin/env python3
"""
Prove gate_owner_actions_item_history_not_oversized() can actually fail
(warn) on a real, unrotated "Start here" checklist or item -1 narrative,
and stays silent once both have been rotated down. A gate that cannot go
red is theatre (ops/preflight.py's own stated rule).

Run:  python ops/tests/test_gate_owner_actions_item_history_not_oversized.py
"""
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                      # noqa: E402
import rotate_owner_actions_item_history as roaih                     # noqa: E402

HEAD = "# Owner actions\n\n| # | Do | Time | Why it is first |\n|---|---|---|---|\n"


def _oa_text(checklist_body, neg1_why):
    return (
        HEAD
        + roaih.NEG1_ROW_START_AFTER + neg1_why + " |\n"
        + roaih.NEG1_ROW_END_BEFORE + " a later row. |\n\n"
        + roaih.CHECKLIST_START_AFTER + "\n\n" + checklist_body + "\n\n\n"
        + roaih.CHECKLIST_END_BEFORE + " no longer needed.\n"
    )


def _run_gate(tmp, oa_text):
    io.open(os.path.join(tmp, "OWNER-ACTIONS.md"), "w",
            encoding="utf-8").write(oa_text)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_owner_actions_item_history_not_oversized()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


def main() -> int:
    fails = []
    GATE = "owner-actions-item-history-not-oversized"

    # 1. A real, unrotated checklist and item -1 narrative must warn.
    #    This is the actual shape found 2026-11-03.
    stale_text = _oa_text(
        "- **1 (YouTube)** would have published videos with a stale "
        "checklist, a long bullet list narrating a one-time 2026-09-18 "
        "check across six items.",
        "**Added 2026-10-09, PM check-in.** A long blow-by-blow of a "
        "USAGE_LIMIT_REACHED stall, re-verifications and a refused "
        "update_trigger attempt, paragraph after paragraph.")
    with tempfile.TemporaryDirectory() as tmp:
        fails1, warns1 = _run_gate(tmp, stale_text)
    if fails1:
        fails.append("gate should WARN, not FAIL, on unrotated history: %r"
                      % (fails1,))
    if not any(g == GATE for g, _ in warns1):
        fails.append("gate did not warn on a synthetic unrotated file: %r"
                      % (warns1,))

    # 2. A freshly rotated file (both replacements live) stays silent.
    # NEG1_REPLACEMENT already carries its own trailing " |\n"; strip it
    # here since _oa_text appends " |\n" itself.
    clean_text = _oa_text(roaih.CHECKLIST_REPLACEMENT,
                           roaih.NEG1_REPLACEMENT[:-len(" |\n")])
    with tempfile.TemporaryDirectory() as tmp:
        fails2, warns2 = _run_gate(tmp, clean_text)
    if fails2:
        fails.append("gate should not FAIL on a clean file: %r" % (fails2,))
    if any(g == GATE for g, _ in warns2):
        fails.append("gate warned on a freshly rotated file: %r" % (warns2,))

    # 3. The real committed file, after a real --apply, stays silent too.
    real_path = os.path.join(ROOT, "OWNER-ACTIONS.md")
    if os.path.exists(real_path):
        real_text = io.open(real_path, encoding="utf-8").read()
        try:
            _, archived = roaih.plan_rotation(real_text)
        except ValueError as e:
            fails.append("plan_rotation raised on the real committed "
                          "file: %s" % e)
        else:
            if archived:
                fails.append("the real committed OWNER-ACTIONS.md still "
                              "has unrotated history: %r" %
                              ([label for label, _ in archived],))

    if fails:
        print("FAIL:")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 3/3")
    return 0


if __name__ == "__main__":
    sys.exit(main())
