#!/usr/bin/env python3
"""
Prove a failing order-delivery pipeline FAILS preflight rather than warning.

WHY THIS EXISTS
---------------
On 2026-10-02 `.github/workflows/fulfil-orders.yml` failed on every run for six
hours (issue #37). That workflow is the only route between a customer's money
and the thing they bought: it emails the buyer the file they paid for and
forwards service bookings to the owner.

gate_workflows_healthy saw it and WARNED, which is correct for most of the
eleven workflows and wrong for this one. The failure appeared as one line among
thirty warnings and nothing acted on it until a human read the Actions tab.
CLAUDE.md 0.2's most expensive lesson in this repository is a payment path left
broken while being correctly reported every single day, and this is the same
shape.

So gate_money_critical_workflows holds a short list of pipelines whose failure
is a P0, and fails on them. The cases below pin the three behaviours that
matter: it fails on a failed run, it says UNCHECKED rather than nothing when it
cannot query, and it fails if a workflow on the list has stopped existing (a
rename that silently empties the list would be the quiet way to lose this).

Run:  python ops/tests/test_gate_money_critical_workflows.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _run(api_result, token="t", listed=None):
    """Run the gate with the API stubbed. Returns (fails, warns)."""
    import dashboard
    old_api = preflight._workflow_run_via_api
    old_cli = preflight._workflow_run_via_cli
    old_tok = dashboard.gh_token
    old_list = preflight.MONEY_CRITICAL_WORKFLOWS
    preflight._workflow_run_via_api = lambda t, n: api_result
    preflight._workflow_run_via_cli = lambda n: api_result
    dashboard.gh_token = lambda: token
    if listed is not None:
        preflight.MONEY_CRITICAL_WORKFLOWS = listed
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_money_critical_workflows()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight._workflow_run_via_api = old_api
        preflight._workflow_run_via_cli = old_cli
        dashboard.gh_token = old_tok
        preflight.MONEY_CRITICAL_WORKFLOWS = old_list


def main():
    fails = []

    # 1. The list must not be empty, or this gate is decoration.
    if not preflight.MONEY_CRITICAL_WORKFLOWS:
        fails.append("MONEY_CRITICAL_WORKFLOWS is empty, so this gate checks "
                     "nothing at all")

    # 2. fulfil-orders.yml must be on it. It is the whole reason the gate
    #    exists, and dropping it would make every case below pass vacuously.
    if "fulfil-orders.yml" not in preflight.MONEY_CRITICAL_WORKFLOWS:
        fails.append("fulfil-orders.yml is not on the money-critical list")

    # 3. A failed run FAILS. This is the 2026-10-02 incident exactly.
    f, w = _run(("failure", "2026-10-02T09:12:00Z", "abc1234", None))
    if not f:
        fails.append("a failed delivery run did not fail the gate: %r" % (w,))
    elif "may receive nothing" not in f[0][1]:
        fails.append("the failure message does not say what is at stake: %r"
                     % (f[0][1][:90],))

    # 4. A successful run is clean, so the gate can tell the two apart.
    f, w = _run(("success", "2026-10-02T16:00:00Z", "abc1234", None))
    if f or w:
        fails.append("a passing delivery run was flagged: %r %r" % (f, w))

    # 5. COULD NOT LOOK IS NOT HEALTHY. An unqueryable workflow warns loudly
    #    rather than passing in silence, which is the defect class this
    #    repository names as its most expensive.
    f, w = _run((None, None, None, "unknown"))
    if f:
        fails.append("an unqueryable workflow was treated as a failure: %r" % f)
    if not w or "UNCHECKED" not in w[0][1]:
        fails.append("an unqueryable workflow did not say UNCHECKED: %r" % (w,))

    # 6. A name on the list that no longer exists on disk is a failure, not a
    #    silent skip. Renaming the workflow and forgetting the list is the
    #    quiet way to end up with a gate that watches nothing.
    f, w = _run(("success", "x", "y", None),
                listed={"no-such-workflow.yml": "a pipeline that is gone"})
    if not f or "does not exist" not in f[0][1]:
        fails.append("a listed workflow missing from disk did not fail: %r"
                     % (f,))

    # 7. The real workflow file is really there right now.
    real = os.path.join(ROOT, ".github", "workflows", "fulfil-orders.yml")
    if not os.path.exists(real):
        fails.append("the real fulfil-orders.yml is missing from this tree")

    if fails:
        print("FAIL")
        for x in fails:
            print(" -", x)
        return 1
    print("OK: gate_money_critical_workflows, 7/7 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
