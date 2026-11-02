#!/usr/bin/env python3
"""
Prove gate_status_history_chain_not_collapsed() can actually warn when
STATUS.md's "Production Knowledge" or "BLOCKER-001" chain has its
superseded entries glued onto one physical line/paragraph via the
"Prior state, kept because the shape recurs: " handoff phrase (the real
shape found live 2026-11-02, which left ops/rotate_status_history.py's
own --check reporting "CLEAN" on a 13-entry, never-rotated chain), and
stays silent once each chain holds a single, unglued entry. A gate that
cannot go red is theatre (ops/preflight.py's own stated rule).

Run:  python ops/tests/test_gate_status_history_chain_not_collapsed.py
"""
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                          # noqa: E402

DELIM = "Prior state, kept because the shape recurs: "

PK_ANCHOR_START = "**Autonomous Execution Readiness:** FULL.\n"
PK_ANCHOR_END = "**Business Data Knowledge,** fine.\n"

B1_HEADING = ("## BLOCKER-001: Production State Verifiable Only From "
              "a Session With Real Access")
B1_END = "## BLOCKER-002: Live Business Data Established, Not Yet a Live Feed"


def _doc(pk_line: str, blocker1_span: str) -> str:
    return (
        "# STATUS.md\n\n"
        + PK_ANCHOR_START + "\n"
        + pk_line + "\n\n"
        + PK_ANCHOR_END + "\n\n"
        + B1_HEADING + "\n\n"
        + blocker1_span + "\n\n"
        + B1_END + "\n\nmore.\n"
    )


PK_GLUED = ("**Production Knowledge, CONFIRMED CURRENT 2026-11-02.** "
            "Newest entry. " + DELIM +
            "**Production Knowledge, CONFIRMED CURRENT 2026-11-01.** "
            "Older entry.")
PK_SINGLE = "**Production Knowledge, CONFIRMED CURRENT 2026-11-02.** Newest entry."

B1_GLUED = ("**CONFIRMED CURRENT 2026-11-02.** Newest entry. " + DELIM +
            "**STRUCTURALLY FIXED 2026-11-01.** Older entry.")
B1_SINGLE = "**CONFIRMED CURRENT 2026-11-02.** Newest entry."


def _run_gate(tmp, text):
    io.open(os.path.join(tmp, "STATUS.md"), "w",
            encoding="utf-8").write(text)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_status_history_chain_not_collapsed()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


def main() -> int:
    fails = []

    # 1. Both chains glued (the real shape found live) must warn for
    #    each field by name, not fail.
    with tempfile.TemporaryDirectory() as tmp:
        f1, w1 = _run_gate(tmp, _doc(PK_GLUED, B1_GLUED))
    if f1:
        fails.append("gate should WARN, not FAIL, on glued chains: %r" % f1)
    joined = " ".join(msg for _, msg in w1)
    if "Production Knowledge" not in joined:
        fails.append("gate did not name Production Knowledge for a glued "
                      "chain: %r" % w1)
    if "BLOCKER-001" not in joined:
        fails.append("gate did not name BLOCKER-001 for a glued chain: %r"
                      % w1)
    if len(w1) != 2:
        fails.append("expected exactly one warning per glued field, got "
                      "%r" % w1)

    # 2. Only Production Knowledge glued, BLOCKER-001 clean: warns once,
    #    names the right field.
    with tempfile.TemporaryDirectory() as tmp:
        f2, w2 = _run_gate(tmp, _doc(PK_GLUED, B1_SINGLE))
    if f2:
        fails.append("gate should WARN, not FAIL: %r" % f2)
    if len(w2) != 1 or "Production Knowledge" not in w2[0][1]:
        fails.append("expected exactly one Production Knowledge warning, "
                      "got %r" % w2)

    # 3. Both chains already rotated to a single, unglued entry: silent.
    with tempfile.TemporaryDirectory() as tmp:
        f3, w3 = _run_gate(tmp, _doc(PK_SINGLE, B1_SINGLE))
    if f3 or w3:
        fails.append("gate fired on properly rotated chains: fail=%r "
                      "warn=%r" % (f3, w3))

    # 4. A missing anchor (section restructured) is a silent skip for
    #    that field, not a crash, matching split_chain's own ValueError
    #    contract.
    broken = _doc(PK_SINGLE, B1_SINGLE).replace(
        "**Autonomous Execution Readiness:** FULL.", "rewritten")
    with tempfile.TemporaryDirectory() as tmp:
        try:
            f4, w4 = _run_gate(tmp, broken)
        except Exception as e:                                # noqa: BLE001
            fails.append("gate crashed on a missing PK anchor instead of "
                          "skipping: %r" % e)

    # 5. A missing STATUS.md is a silent no-op, not a crash.
    with tempfile.TemporaryDirectory() as tmp:
        old_root = preflight.ROOT
        preflight.ROOT = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_status_history_chain_not_collapsed()
        except Exception as e:                                # noqa: BLE001
            fails.append("gate crashed with no STATUS.md present: %r" % e)
        finally:
            preflight.ROOT = old_root

    if fails:
        print("FAIL (%d):" % len(fails))
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 5/5 cases ok.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
