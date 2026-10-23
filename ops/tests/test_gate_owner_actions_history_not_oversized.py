#!/usr/bin/env python3
"""
Prove gate_owner_actions_history_not_oversized() can actually fail (warn)
on a real oversized preamble span and stays silent once it has been
rotated down to the pointer sentence. A gate that cannot go red is
theatre (ops/preflight.py's own stated rule).

Run:  python ops/tests/test_gate_owner_actions_history_not_oversized.py
"""
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402
import rotate_owner_actions as roa                               # noqa: E402

BEFORE = (
    "# Owner actions\n\n"
    "**Last measured:** some traffic sentence, untouched by this gate.\n\n"
    "**List reviewed:** some review sentence, also untouched. "
    "it says nothing about traffic."
)
AFTER = "\n\n---\n\n## Resolved today\n\n| # | Action | Outcome |\n"


def _history_text(n):
    entries = ["**Corrected day-%d:** body text for entry %d, nothing "
               "anyone still needs to read." % (i, i) for i in range(n)]
    return BEFORE + "\n\n" + "\n\n".join(entries) + AFTER


def _run_gate(tmp, oa_text):
    io.open(os.path.join(tmp, "OWNER-ACTIONS.md"), "w",
            encoding="utf-8").write(oa_text)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_owner_actions_history_not_oversized()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


def main() -> int:
    fails = []

    # 1. A preamble with a real, oversized correction chain must warn.
    #    This is the actual defect found 2026-10-23: nothing before this
    #    gate ever caught OWNER-ACTIONS.md's own copy of the shape
    #    STATUS.md and CHECKIN-LOG.md both had.
    stale_text = _history_text(15)
    with tempfile.TemporaryDirectory() as tmp:
        fails1, warns1 = _run_gate(tmp, stale_text)
    if fails1:
        fails.append("gate should WARN, not FAIL, on an oversized "
                      "preamble: %r" % (fails1,))
    if not any(g == "owner-actions-history-not-oversized"
               for g, _ in warns1):
        fails.append("gate did not warn on a 15-entry synthetic chain: %r"
                      % (warns1,))

    # 2. A freshly rotated preamble (pointer sentence only) stays silent.
    rotated_text = BEFORE + "\n\n" + roa.REPLACEMENT + AFTER
    with tempfile.TemporaryDirectory() as tmp2:
        fails2, warns2 = _run_gate(tmp2, rotated_text)
    if fails2 or any(g == "owner-actions-history-not-oversized"
                     for g, _ in warns2):
        fails.append("gate warned on a freshly rotated preamble: "
                      "fails=%r warns=%r" % (fails2, warns2))

    # 3. A single short follow-on note within the buffer stays silent,
    #    so a handoff can add one line without immediately tripping this.
    small_text = _history_text(1)
    with tempfile.TemporaryDirectory() as tmp3:
        fails3, warns3 = _run_gate(tmp3, small_text)
    if fails3 or any(g == "owner-actions-history-not-oversized"
                     for g, _ in warns3):
        fails.append("gate warned on a single-entry note still inside "
                      "the buffer: fails=%r warns=%r" % (fails3, warns3))

    # 4. No OWNER-ACTIONS.md at all: must not crash.
    with tempfile.TemporaryDirectory() as tmp4:
        old_root = preflight.ROOT
        preflight.ROOT = tmp4
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_owner_actions_history_not_oversized()
        except Exception as exc:  # noqa: BLE001
            fails.append("gate crashed with no OWNER-ACTIONS.md present: "
                          "%r" % (exc,))
        finally:
            preflight.ROOT = old_root

    # 5. A file missing the "it says nothing about traffic." anchor (a
    #    differently-shaped document) is skipped, not crashed on.
    unrelated_text = "# Owner actions\n\nnothing recognisable here.\n"
    with tempfile.TemporaryDirectory() as tmp5:
        fails5, warns5 = _run_gate(tmp5, unrelated_text)
    if fails5 or warns5:
        fails.append("gate reported something on a file with no "
                      "recognisable anchors: fails=%r warns=%r"
                      % (fails5, warns5))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_owner_actions_history_not_oversized, fail-then-pass "
          "proved, 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
