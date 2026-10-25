#!/usr/bin/env python3
"""
Prove gate_owner_actions_gemini_billing_not_oversized() can actually fail
(warn) on a real, regrown item-1b correction chain, and stays silent once
that chain has been rotated down. A gate that cannot go red is theatre
(ops/preflight.py's own stated rule).

Run:  python ops/tests/test_gate_owner_actions_gemini_billing_not_oversized.py
"""
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                      # noqa: E402
import rotate_owner_actions_gemini_billing as roagb                   # noqa: E402

HEAD = "# Owner actions\n\n### 1b. Turn on Gemini API billing.\n\n"
TAIL = "\n\n### 1. Authorise YouTube uploads.\n"


def _oa_text(span1_body, span2_body="", span3_body="", zone_rows=None):
    if zone_rows is None:
        zone_rows = roagb.RESOLVED_ZONE_ROWS[:1]  # one stale row by default
    table = ("| Zone | Page | What the image must show |\n"
              "|---|---|---|\n"
              + "".join(zone_rows) +
              "| Workshop, Material Rack | `/zones/workshop-the-material-"
              "rack` | timber planks |\n")
    return (
        HEAD
        + roagb.SPAN_1_START_AFTER + "\n\n" + span1_body + "\n\n"
        + roagb.SPAN_1_END_BEFORE + " body text.\n\n"
        + roagb.SPAN_2_START_AFTER + "\n\n" + span2_body + "\n\n"
        + roagb.SPAN_2_END_BEFORE + " more text.\n\n"
        + roagb.SPAN_3_START_AFTER + "\n\n" + span3_body + "\n\n"
        + table
        + "\n" + roagb.SEVEN_PAGES_OLD + ", correctly.\n"
        + TAIL
    )


def _run_gate(tmp, oa_text):
    io.open(os.path.join(tmp, "OWNER-ACTIONS.md"), "w",
            encoding="utf-8").write(oa_text)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_owner_actions_gemini_billing_not_oversized()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


def main() -> int:
    fails = []
    GATE = "owner-actions-gemini-billing-not-oversized"

    # 1. A regrown chain (a real body in span 1, a stale row in the
    #    table) must warn. This is the actual defect found 2026-10-25.
    stale_text = _oa_text(
        "**Corrected 2026-09-11:** a lot of now-dead reasoning about a "
        "changing count of broken images, paragraph after paragraph.",
        span2_body="**Corrected 2026-09-07:** a superseded recount.",
        span3_body="a stale claim about an empty folder.")
    with tempfile.TemporaryDirectory() as tmp:
        fails1, warns1 = _run_gate(tmp, stale_text)
    if fails1:
        fails.append("gate should WARN, not FAIL, on a regrown chain: %r"
                      % (fails1,))
    if not any(g == GATE for g, _ in warns1):
        fails.append("gate did not warn on a synthetic regrown chain: %r"
                      % (warns1,))

    # 2. A fully rotated file (REPLACEMENT_1 live, spans 2/3 empty, no
    #    stale zone rows) stays silent.
    rotated_text = _oa_text(roagb.REPLACEMENT_1, zone_rows=[])
    rotated_text = rotated_text.replace(roagb.SEVEN_PAGES_OLD,
                                         roagb.SEVEN_PAGES_NEW)
    with tempfile.TemporaryDirectory() as tmp2:
        fails2, warns2 = _run_gate(tmp2, rotated_text)
    if fails2 or any(g == GATE for g, _ in warns2):
        fails.append("gate warned on a freshly rotated file: "
                      "fails=%r warns=%r" % (fails2, warns2))

    # 3. The real, committed OWNER-ACTIONS.md (after this cycle's own
    #    --apply) must itself stay silent, not just a synthetic fixture.
    real_path = os.path.join(ROOT, "OWNER-ACTIONS.md")
    if os.path.exists(real_path):
        real_text = io.open(real_path, encoding="utf-8").read()
        with tempfile.TemporaryDirectory() as tmp3:
            fails3, warns3 = _run_gate(tmp3, real_text)
        if fails3 or any(g == GATE for g, _ in warns3):
            fails.append("gate warned on the real, already-rotated "
                          "OWNER-ACTIONS.md: fails=%r warns=%r"
                          % (fails3, warns3))

    # 4. No OWNER-ACTIONS.md at all: must not crash.
    with tempfile.TemporaryDirectory() as tmp4:
        old_root = preflight.ROOT
        preflight.ROOT = tmp4
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_owner_actions_gemini_billing_not_oversized()
        except Exception as exc:  # noqa: BLE001
            fails.append("gate crashed with no OWNER-ACTIONS.md present: "
                          "%r" % (exc,))
        finally:
            preflight.ROOT = old_root

    # 5. A file missing this item's anchors entirely (drifted past
    #    recognition) warns rather than silently passing: unchecked is
    #    not passing, CLAUDE.md 0.4.
    unrelated_text = "# Owner actions\n\nnothing recognisable here.\n"
    with tempfile.TemporaryDirectory() as tmp5:
        fails5, warns5 = _run_gate(tmp5, unrelated_text)
    if fails5:
        fails.append("gate should WARN, not FAIL, on a file missing its "
                      "anchors: %r" % (fails5,))
    if not any(g == GATE for g, _ in warns5):
        fails.append("gate stayed silent on a file missing its anchors "
                      "instead of warning unchecked: %r" % (warns5,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_owner_actions_gemini_billing_not_oversized, "
          "fail-then-pass proved, 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
