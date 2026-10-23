#!/usr/bin/env python3
"""
Prove gate_status_blocker001_not_oversized() can actually warn on a
STATUS.md whose BLOCKER-001 chain has grown past its buffer, and stays
silent once it is down to the newest entry plus a small buffer. A gate
that cannot go red is theatre (ops/preflight.py's own stated rule).

Run:  python ops/tests/test_gate_status_blocker001_not_oversized.py
"""
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402

HEADING = ("## BLOCKER-001: Production State Verifiable Only From a "
            "Session With Real Access")
AFTER = ("## BLOCKER-002: Live Business Data Established, Not Yet a Live "
         "Feed\n\nUnrelated content.\n")


def _chain_text(n):
    entries = ["**CLOSED day-%d, PM check-in: body text.** More body." % i
               for i in range(n)]
    return ("# 17. Current Blockers\n\n" + HEADING + "\n\n"
            + "\n\n".join(entries) + "\n\n" + AFTER)


def _run_gate(tmp, status_text):
    io.open(os.path.join(tmp, "STATUS.md"), "w", encoding="utf-8").write(
        status_text)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_status_blocker001_not_oversized()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


GATE = "status-blocker001-not-oversized"


def main() -> int:
    fails = []

    # 1. A chain well past the buffer (newest + 3) must warn. This is the
    #    real defect found 2026-10-23: 97 live entries, nothing before
    #    this gate ever caught it.
    with tempfile.TemporaryDirectory() as tmp:
        f1, w1 = _run_gate(tmp, _chain_text(10))
    if f1:
        fails.append("should WARN, not FAIL, on an oversized chain: %r"
                      % (f1,))
    if not any(g == GATE for g, _ in w1):
        fails.append("did not warn on a 10-entry chain: %r" % (w1,))

    # 2. Down to just the newest entry: silent.
    with tempfile.TemporaryDirectory() as tmp2:
        f2, w2 = _run_gate(tmp2, _chain_text(1))
    if f2 or any(g == GATE for g, _ in w2):
        fails.append("warned on a chain already down to 1 entry: "
                      "fails=%r warns=%r" % (f2, w2))

    # 3. Right at the buffer (newest + 3 = 4 entries): still silent, so a
    #    handoff can add a follow-on note without immediately tripping
    #    this gate.
    with tempfile.TemporaryDirectory() as tmp3:
        f3, w3 = _run_gate(tmp3, _chain_text(4))
    if f3 or any(g == GATE for g, _ in w3):
        fails.append("warned on a chain still inside the buffer: "
                      "fails=%r warns=%r" % (f3, w3))

    # 4. One past the buffer (5 entries): warns.
    with tempfile.TemporaryDirectory() as tmp4:
        f4, w4 = _run_gate(tmp4, _chain_text(5))
    if f4 or not any(g == GATE for g, _ in w4):
        fails.append("did not warn one entry past the buffer: "
                      "fails=%r warns=%r" % (f4, w4))

    # 5. No STATUS.md at all: must not crash.
    with tempfile.TemporaryDirectory() as tmp5:
        old_root = preflight.ROOT
        preflight.ROOT = tmp5
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_status_blocker001_not_oversized()
        except Exception as exc:  # noqa: BLE001
            fails.append("gate crashed with no STATUS.md present: %r"
                          % (exc,))
        finally:
            preflight.ROOT = old_root

    # 6. A STATUS.md whose anchors do not match this script's expectations
    #    (e.g. mid-edit, or the section was renamed) must not crash: the
    #    gate should stay silent rather than guess.
    with tempfile.TemporaryDirectory() as tmp6:
        f6, w6 = _run_gate(tmp6, "# Some other file entirely\n\nno chain "
                           "here.\n")
    if f6 or w6:
        fails.append("gate reacted to a file with no recognisable chain: "
                      "fails=%r warns=%r" % (f6, w6))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_status_blocker001_not_oversized, "
          "fail-then-pass proved, 6/6 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
