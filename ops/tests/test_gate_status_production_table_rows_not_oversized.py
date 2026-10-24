#!/usr/bin/env python3
"""
Prove gate_status_production_table_rows_not_oversized() can actually warn
on a STATUS.md whose "Public website" or "Production traceability" table
row has grown past its buffer, and stays silent once each row is down to
the newest entry plus a small buffer. A gate that cannot go red is
theatre (ops/preflight.py's own stated rule).

Run:  python ops/tests/test_gate_status_production_table_rows_not_oversized.py
"""
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402
import rotate_status_history as rsh                             # noqa: E402

TABLE_HEAD = "| Area | Status | Evidence / Notes |\n|---|---|---|\n"


def _row(label, n):
    entries = ["**E%d-%s: body text.** More body." % (i, label[:3])
               for i in range(n, 0, -1)]
    chain = rsh.TABLE_CHAIN_MARKER.join(entries)
    return "| %s | some status | %s |\n" % (label, chain)


def _status_text(public_n, traceability_n):
    return (TABLE_HEAD
            + _row("Public website", public_n)
            + _row("Production traceability", traceability_n))


def _run_gate(tmp, status_text):
    io.open(os.path.join(tmp, "STATUS.md"), "w", encoding="utf-8").write(
        status_text)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_status_production_table_rows_not_oversized()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


GATE = "status-production-table-rows-not-oversized"


def main() -> int:
    fails = []

    # 1. Both rows well past the buffer (newest + 3) must warn. This is
    #    the real defect found 2026-10-24: 21 live entries in each row,
    #    nothing before this gate ever caught either one.
    with tempfile.TemporaryDirectory() as tmp:
        f1, w1 = _run_gate(tmp, _status_text(10, 10))
    if f1:
        fails.append("should WARN, not FAIL, on oversized rows: %r"
                      % (f1,))
    msgs = [m for g, m in w1 if g == GATE]
    if not msgs:
        fails.append("did not warn on two 10-entry rows: %r" % (w1,))
    elif "Public website" not in msgs[0] or "Production traceability" not in msgs[0]:
        fails.append("warning did not name both oversized rows: %r"
                      % (msgs,))

    # 2. Both rows down to just the newest entry: silent.
    with tempfile.TemporaryDirectory() as tmp2:
        f2, w2 = _run_gate(tmp2, _status_text(1, 1))
    if f2 or any(g == GATE for g, _ in w2):
        fails.append("warned on rows already down to 1 entry each: "
                      "fails=%r warns=%r" % (f2, w2))

    # 3. Right at the buffer (newest + 3 = 4 entries) in both rows: still
    #    silent, so a handoff can add a follow-on note without
    #    immediately tripping this gate.
    with tempfile.TemporaryDirectory() as tmp3:
        f3, w3 = _run_gate(tmp3, _status_text(4, 4))
    if f3 or any(g == GATE for g, _ in w3):
        fails.append("warned on rows still inside the buffer: "
                      "fails=%r warns=%r" % (f3, w3))

    # 4. Only ONE row one past the buffer (5 entries), the other clean:
    #    still warns, naming only the oversized one.
    with tempfile.TemporaryDirectory() as tmp4:
        f4, w4 = _run_gate(tmp4, _status_text(5, 1))
    msgs4 = [m for g, m in w4 if g == GATE]
    if f4 or not msgs4:
        fails.append("did not warn when only one row is one past the "
                      "buffer: fails=%r warns=%r" % (f4, w4))
    elif "Production traceability" in msgs4[0]:
        fails.append("warning named the clean row too: %r" % (msgs4,))

    # 5. No STATUS.md at all: must not crash.
    with tempfile.TemporaryDirectory() as tmp5:
        old_root = preflight.ROOT
        preflight.ROOT = tmp5
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_status_production_table_rows_not_oversized()
        except Exception as exc:  # noqa: BLE001
            fails.append("gate crashed with no STATUS.md present: %r"
                          % (exc,))
        finally:
            preflight.ROOT = old_root

    # 6. A STATUS.md whose rows do not match this script's expectations
    #    (renamed, or a stray literal `|` breaking the 4-pipe shape) must
    #    not crash: the gate should stay silent rather than guess.
    with tempfile.TemporaryDirectory() as tmp6:
        f6, w6 = _run_gate(tmp6, "# Some other file entirely\n\nno table "
                           "here.\n")
    if f6 or w6:
        fails.append("gate reacted to a file with no recognisable row: "
                      "fails=%r warns=%r" % (f6, w6))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_status_production_table_rows_not_oversized, "
          "fail-then-pass proved, 6/6 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
