#!/usr/bin/env python3
"""Fast, Chromium-free check that GOALS.md's keyword-cluster citation is
current against the real committed ops/keyword-demand.json.

Found 2026-11-25: `checks.yml` FAILED on two consecutive pushes to main
(runs 45693681410 and 45694625287) because GOALS.md's own "small space" /
"cheap/budget/DIY" cluster citation had drifted from ordinary autocomplete
churn (no content regressed). `gate_goals_keyword_cluster_citation_current`
in `ops/preflight.py` already catches this, correctly, as a WARN (the gate's
own docstring: failing preflight on a strategy document's prose citation
would be disproportionate). But `test_gate_goals_keyword_cluster_citation_
current.py`'s own case 7 asserts the real committed files produce zero
warnings, which turns that same WARN into a hard test-suite FAIL, and that
test lives inside `gate_tests`, which this sandbox's own documented
Chromium hang forces every local `preflight.py` run to skip with
`--skip-tests`. The same shape `check_risks_evidence_fast.py` and
`check_also_called_digital_collision_fast.py` already document: a control
that lives only inside the slow suite is not reachable before a push, so
every intervening cycle reports clean and the drift only surfaces in CI,
after it has already landed on main. This is at least the seventh time
this exact sentence has broken CI this way.

This script calls the gate directly and treats any WARN from it as
push-blocking (stricter than the gate's own full-preflight severity,
deliberately: blocking a push costs seconds, a red `main` costs a cycle),
skipping `gate_tests` and everything it blocks so it finishes in under a
second regardless of what else in this sandbox is unavailable.

Run directly: ``python3 ops/check_goals_keyword_cluster_citation_fast.py``
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight  # noqa: E402


def main() -> int:
    preflight.FAIL.clear()
    preflight.WARN.clear()
    try:
        preflight.gate_goals_keyword_cluster_citation_current()
    except Exception as exc:  # pragma: no cover - defensive, see run_gate
        preflight.fail("goals-keyword-cluster-citation-current",
                        "gate raised %r" % (exc,))

    problems = list(preflight.FAIL) + list(preflight.WARN)
    if problems:
        print("check_goals_keyword_cluster_citation_fast: FAIL",
              file=sys.stderr)
        for name, msg in problems:
            print(f"  {name}: {msg}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Re-derive the live counts from ops/keyword-demand.json and "
              "edit GOALS.md's first \"<cluster> is **...**\" sentence in "
              "place (re.search only checks the first occurrence, not a "
              "later \"is now\" correction), then push.", file=sys.stderr)
        return 1

    print("check_goals_keyword_cluster_citation_fast: GOALS.md's "
          "keyword-cluster citation is current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
