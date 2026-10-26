#!/usr/bin/env python3
"""
Prove a red checks.yml FAILS preflight near the top of the run, where a local
sandbox's gate_tests hang cannot hide it.

WHY THIS EXISTS
---------------
Found 2026-10-19: three straight pushes (759c43f8, a7498109, 7c630782) each
failed checks.yml's own Preflight step on the same root cause (a stale
sitemap lastmod), and every cycle in between kept shipping on "preflight.py:
0 FAIL through every gate reached before the gate_tests sandbox hang" without
ever separately checking whether its own push's CI run had actually passed.
gate_workflows_healthy already watches checks.yml, but only warns, and sits
after gate_tests in main()'s own call order, so neither the gate nor a human
reading "0 FAIL" ever saw it. The same shape cost a cycle once already on
2026-10-15 and was never turned into a gate then, so it recurred.

gate_ci_conclusion_current is called before gate_tests and is a hard FAIL,
the same escalation gate_money_critical_workflows already makes for a broken
delivery pipeline. The cases below pin: it fails on a failed run, it says
UNCHECKED rather than nothing when it cannot query, and a passing run is
clean.

Run:  python ops/tests/test_gate_ci_conclusion_current.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _run(api_result, token="t", has_gh=True, github_workflow=None):
    """Run the gate with the API/CLI stubbed. Returns (fails, warns).

    github_workflow is always set explicitly, never inherited from the
    ambient environment: when this test module runs for real inside
    publish-image.yml's own "Publish site image" job, GITHUB_WORKFLOW
    genuinely equals that string for the whole process, so a caller that
    never touches it would silently exercise the wrong branch (see
    test_publish_image_current.py, 2026-09-17, same shape).
    """
    import dashboard
    old_api = preflight._workflow_run_via_api
    old_cli = preflight._workflow_run_via_cli
    old_tok = dashboard.gh_token
    old_which = preflight.shutil.which
    had_env = "GITHUB_WORKFLOW" in os.environ
    old_env = os.environ.get("GITHUB_WORKFLOW")
    preflight._workflow_run_via_api = lambda t, n: api_result
    preflight._workflow_run_via_cli = lambda n: api_result
    dashboard.gh_token = lambda: token
    preflight.shutil.which = (lambda name: "/usr/bin/gh" if has_gh else None)
    if github_workflow is None:
        os.environ.pop("GITHUB_WORKFLOW", None)
    else:
        os.environ["GITHUB_WORKFLOW"] = github_workflow
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_ci_conclusion_current()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight._workflow_run_via_api = old_api
        preflight._workflow_run_via_cli = old_cli
        dashboard.gh_token = old_tok
        preflight.shutil.which = old_which
        if had_env:
            os.environ["GITHUB_WORKFLOW"] = old_env
        else:
            os.environ.pop("GITHUB_WORKFLOW", None)


def main():
    fails = []

    # 1. A failed run on checks.yml FAILS preflight, by name, and says what
    #    the consequence is (every gate after gate_tests being unverified).
    f, w = _run(("failure", "2026-10-19T19:57:25Z", "7c630782ef6b", None))
    if not f:
        fails.append("a failed checks.yml run did not fail the gate: %r" % (w,))
    elif "gate_tests" not in f[0][1]:
        fails.append("the failure message does not explain the gate_tests "
                      "hang this exists to route around: %r" % (f[0][1][:90],))

    # 2. A passing run is clean, so the gate can tell the two apart and does
    #    not cry wolf on green main.
    f, w = _run(("success", "2026-10-15T11:21:45Z", "3d84199d3c3d", None))
    if f or w:
        fails.append("a passing checks.yml run was flagged: %r %r" % (f, w))

    # 3. COULD NOT LOOK IS NOT GREEN. An unqueryable workflow warns loudly
    #    rather than passing in silence (CLAUDE.md 0.4).
    f, w = _run((None, None, None, "unknown"))
    if f:
        fails.append("an unqueryable workflow was treated as a failure: %r" % f)
    if not w or "Unchecked" not in w[0][1]:
        fails.append("an unqueryable workflow did not say Unchecked: %r" % (w,))

    # 4. No token and no gh binary: warns, does not crash, does not pass
    #    in silence either.
    f, w = _run((None, None, None, "unknown"), token=None, has_gh=False)
    if f:
        fails.append("no-credential case was treated as a failure: %r" % f)
    if not w or "not green" not in w[0][1]:
        fails.append("no-credential case did not say it could not check: %r"
                      % (w,))

    # 5. The gate is actually wired into main() before gate_tests, not just
    #    defined and forgotten (the exact shape of bug this gate exists to
    #    catch one layer up).
    import inspect
    src = inspect.getsource(preflight.main)
    before, _, after = src.partition("run_gate(gate_tests")
    if "gate_ci_conclusion_current" not in before:
        fails.append("gate_ci_conclusion_current is not called before "
                      "gate_tests in main(), so the hang can still hide it")

    # 6. Found 2026-10-26: a failed checks.yml run demoted to WARN, not
    #    FAIL, inside publish-image.yml's own job. That job already runs
    #    this whole preflight against its own HEAD, and hard-failing here
    #    too is what let checks.yml and publish-image.yml deadlock on each
    #    other's prior failure with no way out (gate_publish_image_current
    #    already gets this same demotion for the mirror-image reason).
    f, w = _run(("failure", "2026-10-19T19:57:25Z", "7c630782ef6b", None),
                github_workflow="Publish site image")
    if f:
        fails.append("a failed checks.yml run still hard-FAILed inside "
                      "publish-image.yml's own job, the exact deadlock "
                      "this demotion exists to break: %r" % f)
    if not w or "ci-conclusion-current" not in w[0][0]:
        fails.append("the failure was not even reported as a warning "
                      "inside publish-image.yml's own job: %r" % (w,))

    # 7. The demotion is scoped to publish-image.yml specifically, not a
    #    blanket "anything under GITHUB_WORKFLOW passes": a different (or
    #    absent) workflow name still gets the hard FAIL.
    f, w = _run(("failure", "2026-10-19T19:57:25Z", "7c630782ef6b", None),
                github_workflow="Checks")
    if not f:
        fails.append("the demotion leaked into a differently-named "
                      "workflow, which should still hard-FAIL: %r" % (w,))

    if fails:
        print("FAIL")
        for x in fails:
            print(" -", x)
        return 1
    print("OK: gate_ci_conclusion_current, 7/7 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
