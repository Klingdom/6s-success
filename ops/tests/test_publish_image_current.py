"""Prove gate_publish_image_current can actually see the real defect it
was written for: a failed publish-image.yml run leaving real site/ changes
unpublished, silently, because a later fix commit never touched site/ and so
never re-triggered the path-filtered workflow.

Found 2026-09-07: the Sustain rewrite, the Quest scroll fix and a generator-
regeneration pass all landed, but publish-image.yml failed on two unrelated
control-doc/gate bugs. Both were fixed in commits that touched no file under
site/, so the workflow never ran again and gate_workflows_healthy's plain
"failing: publish-image.yml" warning did not say the one thing that mattered:
HEAD's site/ had never once been in a build that actually shipped.

Everything here uses a throwaway local git repo and forces
_publish_image_runs' return value directly, so none of it depends on network
access, a real token, or today's actual GitHub run history.
"""
import os
import subprocess
import sys
import tempfile
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OPS = os.path.join(ROOT, "ops")
sys.path.insert(0, OPS)

import preflight                                               # noqa: E402
import dashboard                                                # noqa: E402


def _git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True,
                   capture_output=True, text=True)


def _make_repo(differs):
    """A one- or two-commit repo. Returns (repo_dir, good_sha)."""
    tmp = tempfile.mkdtemp(prefix="6s-publish-image-")
    _git(tmp, "init", "-q")
    _git(tmp, "config", "user.email", "t@example.com")
    _git(tmp, "config", "user.name", "t")
    os.makedirs(os.path.join(tmp, "site"), exist_ok=True)
    os.makedirs(os.path.join(tmp, ".github", "workflows"), exist_ok=True)
    with open(os.path.join(tmp, ".github", "workflows", "publish-image.yml"), "w") as f:
        f.write("on: push\n")
    with open(os.path.join(tmp, "site", "x.txt"), "w") as f:
        f.write("old\n")
    _git(tmp, "add", ".")
    _git(tmp, "commit", "-q", "-m", "good build")
    good_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp,
        capture_output=True, text=True, check=True).stdout.strip()
    if differs:
        with open(os.path.join(tmp, "site", "x.txt"), "w") as f:
            f.write("new, unpublished\n")
        _git(tmp, "add", ".")
        _git(tmp, "commit", "-q", "-m", "real fix, never published")
    return tmp, good_sha


def _run_with(repo, latest, goods, token="fake-token"):
    old_root = preflight.ROOT
    old_runs = preflight._publish_image_runs
    old_gh_token = dashboard.gh_token
    preflight.FAIL.clear()
    preflight.WARN.clear()
    try:
        preflight.ROOT = repo
        preflight._publish_image_runs = (
            lambda tok, name, extra_qs="": goods if "status=success" in extra_qs
            else latest)
        dashboard.gh_token = lambda: token
        preflight.gate_publish_image_current()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root
        preflight._publish_image_runs = old_runs
        dashboard.gh_token = old_gh_token


def test_failed_run_with_real_unpublished_diff_fails():
    repo, good_sha = _make_repo(differs=True)
    try:
        fails, warns = _run_with(
            repo,
            latest=[{"status": "completed", "conclusion": "failure",
                    "head_sha": "deadbeef"}],
            goods=[{"status": "completed", "conclusion": "success",
                   "head_sha": good_sha}])
        assert len(fails) == 1, (fails, warns)
        assert "publish-image-current" == fails[0][0]
        assert good_sha[:8] in fails[0][1]
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def test_failed_run_with_no_real_diff_does_not_fail():
    # The failed attempt carried nothing under site/ that the last good
    # build did not already have (e.g. it failed on an unrelated doc-only
    # change): nothing is actually undelivered, so this must stay quiet.
    repo, good_sha = _make_repo(differs=False)
    try:
        fails, warns = _run_with(
            repo,
            latest=[{"status": "completed", "conclusion": "failure",
                    "head_sha": "deadbeef"}],
            goods=[{"status": "completed", "conclusion": "success",
                   "head_sha": good_sha}])
        assert fails == [], (fails, warns)
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def test_latest_success_stays_quiet_even_with_uncalled_goods_query():
    repo, good_sha = _make_repo(differs=True)
    try:
        fails, warns = _run_with(
            repo,
            latest=[{"status": "completed", "conclusion": "success",
                    "head_sha": "whatever"}],
            goods=[])
        assert fails == [] and warns == [], (fails, warns)
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def test_in_progress_latest_run_stays_quiet():
    repo, good_sha = _make_repo(differs=True)
    try:
        fails, warns = _run_with(
            repo,
            latest=[{"status": "in_progress", "conclusion": None,
                    "head_sha": "whatever"}],
            goods=[{"status": "completed", "conclusion": "success",
                   "head_sha": good_sha}])
        assert fails == [] and warns == [], (fails, warns)
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def test_never_succeeded_fails_outright():
    repo, good_sha = _make_repo(differs=True)
    try:
        fails, warns = _run_with(
            repo,
            latest=[{"status": "completed", "conclusion": "failure",
                    "head_sha": "deadbeef"}],
            goods=[])
        assert len(fails) == 1, (fails, warns)
        assert "never once succeeded" in fails[0][1]
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def test_no_token_warns_unchecked_not_healthy():
    repo, good_sha = _make_repo(differs=True)
    try:
        fails, warns = _run_with(repo, latest=[], goods=[], token=None)
        assert fails == [], (fails, warns)
        assert len(warns) == 1, warns
        assert "Unchecked, not current" in warns[0][1]
    finally:
        shutil.rmtree(repo, ignore_errors=True)


if __name__ == "__main__":
    test_failed_run_with_real_unpublished_diff_fails()
    test_failed_run_with_no_real_diff_does_not_fail()
    test_latest_success_stays_quiet_even_with_uncalled_goods_query()
    test_in_progress_latest_run_stays_quiet()
    test_never_succeeded_fails_outright()
    test_no_token_warns_unchecked_not_healthy()
    print("ok  gate_publish_image_current tells undelivered fixes apart from "
          "a routine failure with nothing real behind it")
