#!/usr/bin/env python3
"""
Prove gate_owner_actions_preamble_not_oversized() can actually fail (warn)
when the "Last measured" or "List reviewed" paragraphs regrow a correction
chain after their own live sentence, and stays silent once either has been
rotated down to its pointer sentence. A gate that cannot go red is theatre
(ops/preflight.py's own stated rule).

Run:  python ops/tests/test_gate_owner_actions_preamble_not_oversized.py
"""
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402
import rotate_owner_actions as roa                               # noqa: E402

TAIL = (
    "\n\n**Deploy-gap and per-item history** stays untouched here.\n\n"
    "---\n\n## Resolved today\n\n| # | Action | Outcome |\n"
)


def _preamble(lm_tail, lr_tail):
    return (
        "# Owner actions\n\n"
        "**Last measured:** 2026-10-24 UTC, traffic re-measured by a "
        "direct database read: 49 visitors/121 visits/30 days." + lm_tail +
        "\n\n"
        "**List reviewed:** 2026-10-24" + lr_tail +
        TAIL
    )


def _run_gate(tmp, oa_text):
    io.open(os.path.join(tmp, "OWNER-ACTIONS.md"), "w",
            encoding="utf-8").write(oa_text)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_owner_actions_preamble_not_oversized()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


def main() -> int:
    fails = []

    # 1. A "Last measured" paragraph that regrew a correction chain past
    #    the buffer must warn.
    big_lm_tail = " **Corrected again:** " + "filler padding this out. " * 40
    text1 = _preamble(big_lm_tail, roa.LR_REPLACEMENT)
    with tempfile.TemporaryDirectory() as tmp:
        fails1, warns1 = _run_gate(tmp, text1)
    if fails1:
        fails.append("gate should WARN, not FAIL: %r" % (fails1,))
    if not any(g == "owner-actions-preamble-not-oversized"
               for g, _ in warns1):
        fails.append("gate did not warn on an oversized Last measured "
                     "paragraph: %r" % (warns1,))

    # 2. A "List reviewed" paragraph that regrew a changelog past the
    #    buffer must also warn, independently of Last measured.
    big_lr_tail = (", the marker drifted again. Earlier, 2026-10-20: " +
                    "something else changed, at length. " * 40)
    text2 = _preamble(roa.LM_REPLACEMENT, big_lr_tail)
    with tempfile.TemporaryDirectory() as tmp2:
        fails2, warns2 = _run_gate(tmp2, text2)
    if fails2:
        fails.append("gate should WARN, not FAIL: %r" % (fails2,))
    if not any(g == "owner-actions-preamble-not-oversized"
               for g, _ in warns2):
        fails.append("gate did not warn on an oversized List reviewed "
                     "paragraph: %r" % (warns2,))

    # 3. A freshly rotated preamble (both pointer sentences only) stays
    #    silent.
    rotated_text = _preamble(roa.LM_REPLACEMENT, roa.LR_REPLACEMENT)
    with tempfile.TemporaryDirectory() as tmp3:
        fails3, warns3 = _run_gate(tmp3, rotated_text)
    if fails3 or any(g == "owner-actions-preamble-not-oversized"
                     for g, _ in warns3):
        fails.append("gate warned on a freshly rotated preamble: "
                     "fails=%r warns=%r" % (fails3, warns3))

    # 4. No OWNER-ACTIONS.md at all: must not crash.
    with tempfile.TemporaryDirectory() as tmp4:
        old_root = preflight.ROOT
        preflight.ROOT = tmp4
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_owner_actions_preamble_not_oversized()
        except Exception as exc:  # noqa: BLE001
            fails.append("gate crashed with no OWNER-ACTIONS.md present: "
                         "%r" % (exc,))
        finally:
            preflight.ROOT = old_root

    # 5. A file whose citation sentence no longer matches the required
    #    shape (reworded away from what dashboard.py needs) is skipped,
    #    not crashed on.
    unrelated_text = "# Owner actions\n\nnothing recognisable here.\n"
    with tempfile.TemporaryDirectory() as tmp5:
        fails5, warns5 = _run_gate(tmp5, unrelated_text)
    if fails5 or warns5:
        fails.append("gate reported something on a file with no "
                     "recognisable anchors: fails=%r warns=%r"
                     % (fails5, warns5))

    # 6. The real, currently-committed OWNER-ACTIONS.md stays silent too
    #    (proves the real file is actually rotated, not just a synthetic
    #    copy of it).
    real_path = os.path.join(ROOT, "OWNER-ACTIONS.md")
    if os.path.exists(real_path):
        old_root = preflight.ROOT
        preflight.ROOT = ROOT
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_owner_actions_preamble_not_oversized()
            real_fails, real_warns = list(preflight.FAIL), list(preflight.WARN)
        finally:
            preflight.ROOT = old_root
        if real_fails or any(g == "owner-actions-preamble-not-oversized"
                              for g, _ in real_warns):
            fails.append("the real committed OWNER-ACTIONS.md is not "
                         "clean: fails=%r warns=%r"
                         % (real_fails, real_warns))

    # 7. Regression, 2026-10-24: a file that DOES carry a "**Last
    #    measured:**" header but whose citation sentence has drifted
    #    away from the shape dashboard.py/preflight.py both require must
    #    warn, not go quiet like case 5's completely foreign document.
    drifted_text = (
        "# Owner actions\n\n"
        "**Last measured:** reworded away from the shape this gate "
        "expects, no digits here at all.\n\n"
        "**List reviewed:** also reworded, no date." + TAIL)
    with tempfile.TemporaryDirectory() as tmp7:
        fails7, warns7 = _run_gate(tmp7, drifted_text)
    if fails7:
        fails.append("gate should WARN, not FAIL, on a drifted real-"
                     "shaped file: %r" % (fails7,))
    if not any(g == "owner-actions-preamble-not-oversized"
               for g, _ in warns7):
        fails.append("gate stayed silent on a drifted real-shaped file "
                     "instead of warning: %r" % (warns7,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_owner_actions_preamble_not_oversized, fail-then-pass "
          "proved, 7/7 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
