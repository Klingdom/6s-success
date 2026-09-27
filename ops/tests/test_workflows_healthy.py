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
import datetime as dt
import importlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OPS = os.path.join(ROOT, "ops")
sys.path.insert(0, OPS)

import preflight                                               # noqa: E402

# A fixed calendar date here is a bug that has not failed yet: gate_workflows_
# healthy's own staleness check is relative to "now" (age >= 7 days), so a
# literal "2026-09-03" read as recent the day this was written and read as
# 7-plus-days-stale, and therefore unhealthy, the moment real time caught up
# to it. Found live: this file passed every prior run and then failed on its
# own assertion once the date advanced, with nothing about gate_workflows_
# healthy or the code under test having changed at all. Computed relative to
# import time instead, so "recent" stays recent no matter when this runs.
RECENT = (dt.datetime.now(dt.timezone.utc)
          - dt.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")


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
        lambda n: ("success", RECENT, "deadbeef", None),
        token="fake-token")
    assert warnings == [], warnings


def test_a_real_failure_at_head_is_named_plainly():
    old_commits_behind_head = preflight._commits_behind_head
    try:
        preflight._commits_behind_head = lambda sha: None
        warnings = _run_with(
            ["checks.yml", "publish-image.yml"],
            lambda n: ("failure", RECENT, "current-head-sha", None)
                      if n == "publish-image.yml"
                      else ("success", RECENT, "deadbeef", None),
            token="fake-token")
    finally:
        preflight._commits_behind_head = old_commits_behind_head
    assert len(warnings) == 1, warnings
    assert "publish-image.yml" in warnings[0][1], warnings
    assert "failing" in warnings[0][1], warnings
    assert "behind HEAD" not in warnings[0][1], warnings


def test_a_failure_already_superseded_by_head_says_so():
    old_commits_behind_head = preflight._commits_behind_head
    try:
        preflight._commits_behind_head = lambda sha: 2 if sha == "stale-sha" else None
        warnings = _run_with(
            ["checks.yml", "publish-image.yml"],
            lambda n: ("failure", RECENT, "stale-sha", None)
                      if n == "checks.yml"
                      else ("success", RECENT, "deadbeef", None),
            token="fake-token")
    finally:
        preflight._commits_behind_head = old_commits_behind_head
    assert len(warnings) == 1, warnings
    assert "checks.yml" in warnings[0][1], warnings
    assert "2 commit(s) behind HEAD" in warnings[0][1], warnings
    assert "not proven broken" in warnings[0][1], warnings


def test_a_never_run_workflow_is_named_not_hidden_as_healthy():
    warnings = _run_with(
        ["checks.yml", "new-workflow.yml"],
        lambda n: (None, None, None, "never-run") if n == "new-workflow.yml"
                  else ("success", RECENT, "deadbeef", None),
        token="fake-token")
    assert len(warnings) == 1, warnings
    assert "new-workflow.yml (never run)" in warnings[0][1], warnings


def test_total_query_failure_reads_as_unchecked_not_healthy():
    warnings = _run_with(
        ["checks.yml", "publish-image.yml"],
        lambda n: (None, None, None, "unknown"),
        token="fake-token")
    assert len(warnings) == 1, warnings
    assert "Unchecked, not healthy" in warnings[0][1], warnings


OLD = (dt.datetime.now(dt.timezone.utc)
       - dt.timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_with_staleness_helpers(fake_names, fake_lookup, token,
                                 trigger_paths, touched):
    """Like `_run_with`, but also forces `_workflow_trigger_paths` and
    `_commits_touching_paths_since`, the two helpers the path-scoped-idle
    fix below depends on, so this stays independent of both real git
    history and the real workflow files on disk.
    """
    old_paths = preflight._workflow_trigger_paths
    old_touching = preflight._commits_touching_paths_since
    try:
        preflight._workflow_trigger_paths = lambda n: trigger_paths
        preflight._commits_touching_paths_since = lambda sha, paths: touched
        return _run_with(fake_names, fake_lookup, token)
    finally:
        preflight._workflow_trigger_paths = old_paths
        preflight._commits_touching_paths_since = old_touching


def test_path_scoped_workflow_idle_since_last_run_is_not_stale():
    """Found live 2026-09-27: `mobile-checks.yml` (paths: mobile/quest-app/
    lib/**, package.json) had a `success` run 10 days old and was flagged
    "not running", even though nothing had touched its own trigger paths
    since. Correctly idle by design is not the same as stopped running."""
    warnings = _run_with_staleness_helpers(
        ["checks.yml", "mobile-checks.yml"],
        lambda n: ("success", OLD, "deadbeef", None)
                  if n == "mobile-checks.yml"
                  else ("success", RECENT, "deadbeef", None),
        token="fake-token",
        trigger_paths=["mobile/quest-app/lib/**"],
        touched=0)
    assert warnings == [], warnings


def test_path_scoped_workflow_idle_despite_a_matching_commit_is_still_stale():
    """The fix above must not swallow a real regression: if a commit DID
    touch the workflow's own trigger paths since its last recorded run and
    it still has not re-run, that is a real "stopped running", not idle."""
    warnings = _run_with_staleness_helpers(
        ["checks.yml", "mobile-checks.yml"],
        lambda n: ("success", OLD, "deadbeef", None)
                  if n == "mobile-checks.yml"
                  else ("success", RECENT, "deadbeef", None),
        token="fake-token",
        trigger_paths=["mobile/quest-app/lib/**"],
        touched=2)
    assert len(warnings) == 1, warnings
    assert "mobile-checks.yml (10 days)" in warnings[0][1], warnings


def test_unscoped_workflow_going_stale_is_unaffected_by_the_fix():
    """A workflow with no `paths:` filter at all has nothing to be idle
    about; the old age >= 7 behaviour must be unchanged for it."""
    warnings = _run_with_staleness_helpers(
        ["checks.yml", "hourly-brief.yml"],
        lambda n: ("success", OLD, "deadbeef", None)
                  if n == "hourly-brief.yml"
                  else ("success", RECENT, "deadbeef", None),
        token="fake-token",
        trigger_paths=None,
        touched=None)
    assert len(warnings) == 1, warnings
    assert "hourly-brief.yml (10 days)" in warnings[0][1], warnings


if __name__ == "__main__":
    importlib.reload(preflight)
    test_all_healthy_produces_no_warning()
    test_a_real_failure_at_head_is_named_plainly()
    test_a_failure_already_superseded_by_head_says_so()
    test_a_never_run_workflow_is_named_not_hidden_as_healthy()
    test_total_query_failure_reads_as_unchecked_not_healthy()
    test_path_scoped_workflow_idle_since_last_run_is_not_stale()
    test_path_scoped_workflow_idle_despite_a_matching_commit_is_still_stale()
    test_unscoped_workflow_going_stale_is_unaffected_by_the_fix()
    print("ok  gate_workflows_healthy tells healthy, failing, already-"
          "superseded, never-run, unqueryable and correctly-idle apart")
