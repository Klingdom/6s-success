#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_experiments_blocked_reason_current() can
actually fail, and that it clears once the experiments section stops
claiming the site has no deployment.

Found 2026-09-24, this operator: ops/status_report.py's gather() hardcoded
experiments.blocked_reason to "no deployment, therefore no traffic and no
subjects", true only on 2026-08-19, the day EXPERIMENT-PLAN.md (the source
this sentence was copied from) was written. ops/state.json's own
deploy_verdict had read "current" for weeks, and traffic_line carried a
real number the whole time, while every status PDF Phil received kept
telling him the site was not deployed at all. Fixed by pulling the
derivation into ops.status_report.experiments_blocked_reason(S), read from
real state instead of typed once.

Run:  python ops/tests/test_gate_experiments_blocked_reason_current.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import status_report as SR                                     # noqa: E402


def main() -> int:
    fails = []

    # 1. The real defect shape: deployed, but the reason text still claims
    #    "no deployment". Must fire, and must name both the real verdict and
    #    the stale claim.
    problem = preflight.experiments_blocked_reason_problem(
        "current", "no deployment, therefore no traffic and no subjects")
    if not problem:
        fails.append("deploy_verdict current but reason claims no "
                     "deployment: expected a problem, got none")
    elif "current" not in problem:
        fails.append("problem string did not name the real deploy_verdict: "
                     "%r" % problem)

    # 2. Same stale claim, but deploy_verdict is "stale" (still means the
    #    site is deployed, just behind). Must still fire.
    problem = preflight.experiments_blocked_reason_problem(
        "stale", "no deployment, therefore no traffic and no subjects")
    if not problem:
        fails.append("deploy_verdict stale but reason claims no "
                     "deployment: expected a problem, got none")

    # 3. deploy_verdict unknown (this sandbox could not measure it): must
    #    not fire, since "no deployment" is not disprovable from here.
    problem = preflight.experiments_blocked_reason_problem(
        "unknown", "no deployment, therefore no traffic and no subjects")
    if problem:
        fails.append("deploy_verdict unknown, but still flagged: %r"
                     % problem)

    # 4. deploy_verdict current, reason text honest (the real fix): must not
    #    fire.
    honest = ("the site is deployed and has real traffic (68 visitors "
             "across 160 visits, 30 days), but at this volume no test can "
             "reach a valid read yet; see EXPERIMENT-PLAN.md")
    problem = preflight.experiments_blocked_reason_problem("current", honest)
    if problem:
        fails.append("honest, current reason text, but still flagged: %r"
                     % problem)

    # 5. The real function, called directly, must produce text that clears
    #    its own gate when the site is deployed: proves the fix and the
    #    check agree, not just two hand-typed strings.
    real = SR.experiments_blocked_reason({
        "deploy_verdict": "current",
        "traffic_line_last_measured": "68 visitors across 160 visits, 30 days",
    })
    if "no deployment" in real:
        fails.append("status_report.experiments_blocked_reason() itself "
                     "still says 'no deployment' while deployed: %r" % real)
    problem = preflight.experiments_blocked_reason_problem("current", real)
    if problem:
        fails.append("status_report.experiments_blocked_reason()'s real "
                     "output still fails its own gate: %r" % problem)

    # 6. Real function with unknown deploy state: honest, must not claim
    #    "no deployment" as a certainty either.
    real_unknown = SR.experiments_blocked_reason({})
    if "no deployment" in real_unknown:
        fails.append("experiments_blocked_reason({}) asserts 'no "
                     "deployment' as fact rather than admitting it is "
                     "unknown: %r" % real_unknown)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 6 checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
