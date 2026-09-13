#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_risk_cross_references_current() catches one
RISKS.md entry citing a sibling RISK-ID as a live blocker after that
sibling's own status table row has moved to CLOSED, ACCEPTED or
TRANSFERRED.

Found live 2026-09-13, this operator, cold-reading ARCHITECTURE.md: RISK-0007
(still OPEN) named "recovery depends on RISK-0002 being fixed first" and its
own mitigation opened "Fix RISK-0002," but RISK-0002 itself closed
2026-08-18 (the VPS stopped cloning the repository at all, pulling a built
image from ghcr.io instead). Nothing re-derived one entry's citation from
another entry's own status line, so the stale dependency stood for three and
a half weeks. gate_risks_register_current and gate_risks_evidence_current
both already exist and neither covers this shape: one checks the section 8
summary counts against the table, the other checks numeric evidence against
ops/state.json, and neither reads a risk's own prose for a citation of
another risk's ID.

Run:  python ops/tests/test_gate_risk_cross_references_current.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

TABLE = """
| ID | Title | Severity | Status |
|---|---|---|---|
| RISK-0001 | Something closed | CRITICAL | CLOSED |
| RISK-0002 | Something else open | HIGH | OPEN |
"""


def run_gate(body_after_table):
    text = TABLE + "\n" + body_after_table
    tmp = tempfile.mkdtemp()
    with open(os.path.join(tmp, "RISKS.md"), "w", encoding="utf-8") as f:
        f.write(text)
    real_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL.clear()
    preflight.WARN.clear()
    try:
        preflight.gate_risk_cross_references_current()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = real_root


def case_clean_no_citation():
    fail, warn = run_gate("RISK-0002 is still open and needs real work.")
    assert fail == [], f"expected clean, got {fail}"
    print("PASS: no cross-reference at all does not trip the gate")


def case_clean_open_risk_cited():
    fail, warn = run_gate("Fix RISK-0002 before shipping this.")
    assert fail == [], f"citing an OPEN risk as a blocker is legitimate, got {fail}"
    print("PASS: citing a still-OPEN risk as a blocker is not flagged")


def case_fail_fix_phrasing():
    fail, warn = run_gate("mitigation: Fix RISK-0001. Then do the rest.")
    assert len(fail) == 1 and fail[0][0] == "risk-cross-references-current", fail
    assert "RISK-0001" in fail[0][1] and "CLOSED" in fail[0][1]
    print("PASS: 'Fix RISK-0001' against a CLOSED RISK-0001 fails, naming it")


def case_fail_depends_on_phrasing():
    fail, warn = run_gate("recovery depends on RISK-0001 being fixed first.")
    assert len(fail) == 1 and fail[0][0] == "risk-cross-references-current", fail
    print("PASS: 'depends on RISK-0001 ... being fixed' against a CLOSED risk fails")


def case_clean_narrating_own_resolution():
    fail, warn = run_gate(
        "RISK-0001 closed 2026-08-21 when a real transaction completed. "
        "This entry no longer needs RISK-0001 fixed anywhere else."
    )
    # "fixed" alone with no "being fixed"/"depends on"/"Fix RISK-000x" shape
    # must not trip the gate; only the specific live-blocker phrasings do.
    assert fail == [], f"narrating a past resolution should not fail, got {fail}"
    print("PASS: narrating RISK-0001's own resolution does not false-positive")


if __name__ == "__main__":
    case_clean_no_citation()
    case_clean_open_risk_cited()
    case_fail_fix_phrasing()
    case_fail_depends_on_phrasing()
    case_clean_narrating_own_resolution()
    print("\n5 of 5 cases pass")
