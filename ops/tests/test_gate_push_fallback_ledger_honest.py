#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_push_fallback_ledger_honest() (and its pure
check_push_fallback_ledger_honest()) catches a scheduled-workflow push
fallback that uses its own `status=success` run count as evidence a real
send already happened today.

Found 2026-09-30, this operator, verifying bluesky-drafts.yml's first live
run. A stood-down push (before the cron's own target time, or because a
real send already happened) exits 0 and is therefore itself a "successful"
run, so on a repository that pushes dozens of times a day, the first push
checked after the target time already counts every earlier stood-down push
as a false "already sent" and the fallback can never fire for real.
linkedin-drafts.yml and social-drafts.yml shared the identical shape.

Run:  python ops/tests/test_gate_push_fallback_ledger_honest.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

BROKEN = """name: Example drafts
on:
  schedule:
    - cron: '5 14 * * *'
  push:
    branches: [main]
jobs:
  drafts:
    steps:
      - name: Decide whether this run should send
        run: |
          today=$(date -u +%Y-%m-%d)
          runs="repos/$GITHUB_REPOSITORY/actions/workflows/example-drafts.yml/runs"
          n=$(gh api "$runs?status=success&created=%3E%3D$today" \\
                --jq '.workflow_runs | length' 2>/dev/null || echo unknown)
          if [ "$n" -gt 0 ]; then
            echo 'send=no' >> "$GITHUB_OUTPUT"
          fi
"""

FIXED = """name: Example drafts
on:
  schedule:
    - cron: '5 14 * * *'
  push:
    branches: [main]
jobs:
  drafts:
    steps:
      - name: Decide whether this run should send
        run: |
          today_start=$(date -u +%Y-%m-%dT00:00:00Z)
          n=$(gh api "repos/$GITHUB_REPOSITORY/commits?since=$today_start&path=ops/corpus-rotation.json&per_page=100" \\
                --jq '[.[] | select(.commit.message | startswith("Example drafts: advance rotation"))] | length' \\
                2>/dev/null || echo unknown)
          if [ "$n" -gt 0 ]; then
            echo 'send=no' >> "$GITHUB_OUTPUT"
          fi
"""

NO_PUSH_TRIGGER = """name: Scheduled only, no fallback needed
on:
  schedule:
    - cron: '0 12 * * *'
jobs:
  x:
    steps:
      - run: |
          n=$(gh api "repos/x/actions/workflows/x.yml/runs?status=success" --jq '.workflow_runs | length')
"""


def _write(tmp_dir, name, text):
    io.open(os.path.join(tmp_dir, name), "w", encoding="utf-8").write(text)


def test_pure_check_catches_the_broken_shape():
    tmp = tempfile.mkdtemp()
    try:
        _write(tmp, "example-drafts.yml", BROKEN)
        problems = preflight.check_push_fallback_ledger_honest(tmp)
        assert any("example-drafts.yml" in p for p in problems), problems
        print("ok  the status=success run-count shape is caught")
    finally:
        shutil.rmtree(tmp)


def test_pure_check_passes_on_the_fixed_shape():
    tmp = tempfile.mkdtemp()
    try:
        _write(tmp, "example-drafts.yml", FIXED)
        assert preflight.check_push_fallback_ledger_honest(tmp) == []
        print("ok  the commit-ledger fixed shape passes clean")
    finally:
        shutil.rmtree(tmp)


def test_pure_check_ignores_a_workflow_with_no_push_trigger():
    """A schedule-only workflow has no fallback to be dishonest about, even
    if it happens to call the Actions API for some other reason.
    """
    tmp = tempfile.mkdtemp()
    try:
        _write(tmp, "scheduled-only.yml", NO_PUSH_TRIGGER)
        assert preflight.check_push_fallback_ledger_honest(tmp) == []
        print("ok  a workflow with no push trigger is not checked")
    finally:
        shutil.rmtree(tmp)


def test_gate_fails_by_name_on_the_broken_shape():
    tmp = tempfile.mkdtemp()
    try:
        _write(tmp, "example-drafts.yml", BROKEN)
        real_root = preflight.ROOT
        preflight.ROOT = tmp
        os.makedirs(os.path.join(tmp, ".github", "workflows"), exist_ok=True)
        shutil.move(os.path.join(tmp, "example-drafts.yml"),
                    os.path.join(tmp, ".github", "workflows", "example-drafts.yml"))
        before = len(preflight.FAIL)
        try:
            preflight.gate_push_fallback_ledger_honest()
            fails = preflight.FAIL[before:]
        finally:
            preflight.ROOT = real_root
        assert len(fails) == 1, fails
        gate, msg = fails[0]
        assert gate == "push-fallback-ledger-honest", fails
        assert "example-drafts.yml" in msg, msg
        print("ok  gate fails naming push-fallback-ledger-honest and the file")
    finally:
        shutil.rmtree(tmp)


def test_missing_workflows_dir_does_not_crash():
    tmp = tempfile.mkdtemp()
    try:
        real_root = preflight.ROOT
        preflight.ROOT = tmp
        before = len(preflight.FAIL)
        try:
            preflight.gate_push_fallback_ledger_honest()
        finally:
            preflight.ROOT = real_root
        assert preflight.FAIL[before:] == []
        print("ok  a missing .github/workflows directory does not crash the gate")
    finally:
        shutil.rmtree(tmp)


def test_real_repository_workflows_pass_right_now():
    """Not a synthetic fixture: the actual committed
    .github/workflows/*.yml files, run through the real gate exactly as
    preflight.py's main() calls it, proving the repository's own fix to
    bluesky-drafts.yml, linkedin-drafts.yml and social-drafts.yml, not just
    the logic.
    """
    before = len(preflight.FAIL)
    preflight.gate_push_fallback_ledger_honest()
    new_fails = preflight.FAIL[before:]
    assert not new_fails, (
        "a real workflow still uses the broken status=success ledger: %s"
        % new_fails)
    print("ok  the real committed workflows pass right now")


if __name__ == "__main__":
    test_pure_check_catches_the_broken_shape()
    test_pure_check_passes_on_the_fixed_shape()
    test_pure_check_ignores_a_workflow_with_no_push_trigger()
    test_gate_fails_by_name_on_the_broken_shape()
    test_missing_workflows_dir_does_not_crash()
    test_real_repository_workflows_pass_right_now()
    print("\nall gate_push_fallback_ledger_honest tests passed")
