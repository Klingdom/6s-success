"""Prove gate_workflows_healthy can actually see a real defect.

Before this fix the gate always warned "unchecked": this sandbox has no gh
binary, and real CI's runner has gh installed but no GH_TOKEN/GITHUB_TOKEN
exported to the step's environment, so `gh run list` failed unauthenticated
in both places this gate has ever run. A gate that has never once been able
to look is not a check, it is a comment shaped like one.

Two things have to both be true:

    a healthy set of workflows must read as healthy, not "unchecked";
    a real failing/never-run/unqueryable workflow must still be named.

Everything here forces `_workflow_run_via_api`'s return value directly, so
none of it depends on network access, a real token, or today's actual
GitHub state.
"""
import importlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OPS = os.path.join(ROOT, "ops")
sys.path.insert(0, OPS)

import preflight                                               # noqa: E402


def _run_with(fake_names, fake_lookup, token):
    old_names_glob = preflight.glob.glob
    old_api = preflight._workflow_run_via_api
    old_cli = preflight._workflow_run_via_cli
    old_which = preflight.shutil.which
    old_gh_token = None
    import dashboard
    old_gh_token = dashboard.gh_token
    preflight.FAIL.clear()
    preflight.WARN.clear()
    try:
        preflight.glob.glob = lambda *a, **k: [
            os.path.join(ROOT, ".github", "workflows", n) for n in fake_names]
        preflight._workflow_run_via_api = lambda tok, n: fake_lookup(n)
        preflight._workflow_run_via_cli = lambda n: fake_lookup(n)
        preflight.shutil.which = lambda x: "/usr/bin/gh" if x == "gh" else None
        dashboard.gh_token = lambda: token
        preflight.gate_workflows_healthy()
        return list(preflight.WARN)
    finally:
        preflight.glob.glob = old_names_glob
        preflight._workflow_run_via_api = old_api
        preflight._workflow_run_via_cli = old_cli
        preflight.shutil.which = old_which
        dashboard.gh_token = old_gh_token


def test_all_healthy_produces_no_warning():
    warnings = _run_with(
        ["checks.yml", "publish-image.yml"],
        lambda n: ("success", "2026-09-03T00:00:00Z", None),
        token="fake-token")
    assert warnings == [], warnings


def test_a_real_failure_is_named():
    warnings = _run_with(
        ["checks.yml", "publish-image.yml"],
        lambda n: ("failure", "2026-09-03T00:00:00Z", None)
                  if n == "publish-image.yml"
                  else ("success", "2026-09-03T00:00:00Z", None),
        token="fake-token")
    assert len(warnings) == 1, warnings
    assert "publish-image.yml" in warnings[0][1], warnings
    assert "failing" in warnings[0][1], warnings


def test_a_never_run_workflow_is_named_not_hidden_as_healthy():
    warnings = _run_with(
        ["checks.yml", "new-workflow.yml"],
        lambda n: (None, None, "never-run") if n == "new-workflow.yml"
                  else ("success", "2026-09-03T00:00:00Z", None),
        token="fake-token")
    assert len(warnings) == 1, warnings
    assert "new-workflow.yml (never run)" in warnings[0][1], warnings


def test_total_query_failure_reads_as_unchecked_not_healthy():
    warnings = _run_with(
        ["checks.yml", "publish-image.yml"],
        lambda n: (None, None, "unknown"),
        token="fake-token")
    assert len(warnings) == 1, warnings
    assert "Unchecked, not healthy" in warnings[0][1], warnings


if __name__ == "__main__":
    importlib.reload(preflight)
    test_all_healthy_produces_no_warning()
    test_a_real_failure_is_named()
    test_a_never_run_workflow_is_named_not_hidden_as_healthy()
    test_total_query_failure_reads_as_unchecked_not_healthy()
    print("ok  gate_workflows_healthy tells healthy, failing, never-run and "
          "unqueryable apart")
