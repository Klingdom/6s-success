#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_risks_traffic_citations_current() catches a
RISKS.md evidence block that tracks traffic (mentions both "visitor" and
"visit") but still cites a superseded GOALS.md baseline instead of the
current one.

Found live 2026-09-14 (late): RISK-0013's evidence opened with "68
visitors/161 visits... most recently 2026-09-11" and RISK-0005's evidence
said the visit count was "correctly left unconfirmed", both a full cycle
after GOALS.md had already moved to "75 visitors / 196 visits / 30 days"
(2026-09-14 21:30). gate_no_stale_session_label had already fixed the
identical shape once in these same two entries (2026-09-04, the retired "47
sessions" wording) and gate_risks_evidence_current already catches this
shape for `key=value` state.json citations; neither reaches a prose
"N visitors / N visits" figure, which is what both stale entries actually
used.

Run:  python ops/tests/test_gate_risks_traffic_citations_current.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

GOALS = """
| Stranger to Visitor | **75 visitors / 196 visits / 30 days** | measured 2026-09-14 |
"""


def run_gate(risks_body):
    preflight.FAIL.clear()
    preflight.WARN.clear()
    preflight.check_risks_traffic_citations_current(risks_body, GOALS)
    return list(preflight.FAIL), list(preflight.WARN)


def case_clean_current_figure_cited():
    fail, warn = run_gate("""
```yaml
id: RISK-0013
evidence:
  - 75 visitors/196 visits/30 days, the current baseline.
```
""")
    assert fail == [], f"current figure cited, expected clean, got {fail}"
    print("PASS: block citing the current 75 visitors/196 visits figure is clean")


def case_fail_stale_figure_only():
    fail, warn = run_gate("""
```yaml
id: RISK-0013
evidence:
  - 68 visitors/161 visits/30 days, most recently 2026-09-11.
```
""")
    assert len(fail) == 1 and fail[0][0] == "risks-traffic-citations-current", fail
    assert "RISK-0013" in fail[0][1]
    print("PASS: block citing only a stale 68/161 figure fails, naming RISK-0013")


def case_clean_stale_figure_alongside_current():
    fail, warn = run_gate("""
```yaml
id: RISK-0013
evidence:
  - 75 visitors/196 visits/30 days, up from 68 visitors/161 visits on
    2026-09-11.
```
""")
    assert fail == [], (
        f"current figure present alongside historical trail, expected "
        f"clean, got {fail}")
    print("PASS: current figure alongside a historical 'up from' trail is clean")


def case_clean_block_with_no_traffic_mention():
    fail, warn = run_gate("""
```yaml
id: RISK-0007
evidence:
  - no staging environment exists, and no restore has ever been proven.
```
""")
    assert fail == [], f"no visitor/visit mention, expected clean, got {fail}"
    print("PASS: a block that never mentions visitor/visit traffic is untouched")


def case_fail_two_stale_entries_named_together():
    fail, warn = run_gate("""
```yaml
id: RISK-0005
evidence:
  - visitor and visit counts were pulled 2026-09-11, 68 visitors/161 visits.
```

```yaml
id: RISK-0013
evidence:
  - 68 visitors/161 visits, most recently 2026-09-11.
```
""")
    assert len(fail) == 1 and fail[0][0] == "risks-traffic-citations-current", fail
    assert "RISK-0005" in fail[0][1] and "RISK-0013" in fail[0][1]
    print("PASS: two stale traffic-tracking entries are both named in one failure")


def case_clean_goals_format_unrecognized():
    fail, warn = run_gate("""
```yaml
id: RISK-0013
evidence:
  - 68 visitors/161 visits/30 days.
```
""")
    real = preflight.check_risks_traffic_citations_current
    # A GOALS.md that no longer matches the expected baseline sentence shape
    # must not crash or false-positive; it should simply skip the check.
    preflight.FAIL.clear()
    preflight.WARN.clear()
    real("""
```yaml
id: RISK-0013
evidence:
  - 68 visitors/161 visits/30 days.
```
""", "GOALS.md rewritten with no recognizable baseline sentence at all.")
    assert list(preflight.FAIL) == [], "unrecognized GOALS.md format must not fail"
    print("PASS: an unrecognized GOALS.md baseline format is skipped, not flagged")


if __name__ == "__main__":
    case_clean_current_figure_cited()
    case_fail_stale_figure_only()
    case_clean_stale_figure_alongside_current()
    case_clean_block_with_no_traffic_mention()
    case_fail_two_stale_entries_named_together()
    case_clean_goals_format_unrecognized()
    print("\n6 of 6 cases pass")
