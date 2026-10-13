#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_schedule_fallback_race() (and its pure
check_schedule_fallback_race()) catches a workflow whose `schedule` branch
sends unconditionally while its own `push` fallback keeps a once-a-day
ledger.

Found 2026-10-13, this operator. linkedin-drafts.yml, bluesky-drafts.yml
and social-drafts.yml each gated with `if [ "$EVENT_NAME" != 'push' ]` and
sent unconditionally for anything else, on the theory that cron fires at
most once a day. It does not fire ON TIME once a day; GitHub queues
scheduled runs under load, so a delayed schedule run can execute AFTER the
push fallback has already stood in for it, and both send. Confirmed
directly from git history: 8 of the last 13 to 28 tracked days for each of
the three workflows carried 2 or 3 real "advance rotation" commits in one
day. Fixed by making `schedule` fall through to the same once-a-day ledger
check as `push`, leaving only `workflow_dispatch` sending unconditionally.

Run:  python ops/tests/test_gate_schedule_fallback_race.py
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
          if [ "$EVENT_NAME" != 'push' ]; then
            echo 'send=yes' >> "$GITHUB_OUTPUT"
            exit 0
          fi
          n=$(gh api "repos/$GITHUB_REPOSITORY/commits?since=$today_start" \\
                --jq '[.[] | select(.commit.message | startswith("Example: advance"))] | length' \\
                2>/dev/null || echo unknown)
          if [ "$n" -gt 0 ]; then
            echo 'send=no' >> "$GITHUB_OUTPUT"
            echo "already sent today ($n rotation-advance commit(s))."
            exit 0
          fi
          echo 'send=yes' >> "$GITHUB_OUTPUT"
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
          if [ "$EVENT_NAME" = 'workflow_dispatch' ]; then
            echo 'send=yes' >> "$GITHUB_OUTPUT"
            exit 0
          fi
          if [ "$EVENT_NAME" = 'push' ]; then
            now=$(date -u +%s)
            if [ "$now" -lt "$target" ]; then
              echo 'send=no' >> "$GITHUB_OUTPUT"
              exit 0
            fi
          fi
          n=$(gh api "repos/$GITHUB_REPOSITORY/commits?since=$today_start" \\
                --jq '[.[] | select(.commit.message | startswith("Example: advance"))] | length' \\
                2>/dev/null || echo unknown)
          if [ "$n" -gt 0 ]; then
            echo 'send=no' >> "$GITHUB_OUTPUT"
            echo "already sent today ($n rotation-advance commit(s))."
            exit 0
          fi
          echo 'send=yes' >> "$GITHUB_OUTPUT"
"""

NO_PUSH_TRIGGER = """name: Scheduled only, no fallback to race
on:
  schedule:
    - cron: '0 12 * * *'
jobs:
  x:
    steps:
      - run: |
          if [ "$EVENT_NAME" != 'push' ]; then
            echo 'send=yes' >> "$GITHUB_OUTPUT"
          fi
"""

NO_LEDGER = """name: Push trigger but no real ledger to race
on:
  schedule:
    - cron: '0 12 * * *'
  push:
    branches: [main]
jobs:
  x:
    steps:
      - run: |
          if [ "$EVENT_NAME" != 'push' ]; then
            echo 'send=yes' >> "$GITHUB_OUTPUT"
          fi
"""


def _write(tmp_dir, name, text):
    io.open(os.path.join(tmp_dir, name), "w", encoding="utf-8").write(text)


def test_pure_check_catches_the_broken_shape():
    tmp = tempfile.mkdtemp()
    try:
        _write(tmp, "example-drafts.yml", BROKEN)
        problems = preflight.check_schedule_fallback_race(tmp)
        assert any("example-drafts.yml" in p for p in problems), problems
        print("ok  the unconditional-schedule-send shape is caught")
    finally:
        shutil.rmtree(tmp)


def test_pure_check_passes_on_the_fixed_shape():
    tmp = tempfile.mkdtemp()
    try:
        _write(tmp, "example-drafts.yml", FIXED)
        assert preflight.check_schedule_fallback_race(tmp) == []
        print("ok  the workflow_dispatch-only-unconditional fixed shape passes clean")
    finally:
        shutil.rmtree(tmp)


def test_pure_check_ignores_a_workflow_with_no_push_trigger():
    tmp = tempfile.mkdtemp()
    try:
        _write(tmp, "scheduled-only.yml", NO_PUSH_TRIGGER)
        assert preflight.check_schedule_fallback_race(tmp) == []
        print("ok  a workflow with no push trigger is not checked")
    finally:
        shutil.rmtree(tmp)


def test_pure_check_ignores_a_workflow_with_no_real_ledger():
    """A push trigger that is not a once-a-day send fallback (no "already
    sent today" ledger check) has nothing for the schedule branch to race
    against.
    """
    tmp = tempfile.mkdtemp()
    try:
        _write(tmp, "unrelated-push.yml", NO_LEDGER)
        assert preflight.check_schedule_fallback_race(tmp) == []
        print("ok  a push trigger with no once-a-day ledger is not checked")
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
            preflight.gate_schedule_fallback_race()
            fails = preflight.FAIL[before:]
        finally:
            preflight.ROOT = real_root
        assert len(fails) == 1, fails
        gate, msg = fails[0]
        assert gate == "schedule-fallback-race", fails
        assert "example-drafts.yml" in msg, msg
        print("ok  gate fails naming schedule-fallback-race and the file")
    finally:
        shutil.rmtree(tmp)


def test_missing_workflows_dir_does_not_crash():
    tmp = tempfile.mkdtemp()
    try:
        real_root = preflight.ROOT
        preflight.ROOT = tmp
        before = len(preflight.FAIL)
        try:
            preflight.gate_schedule_fallback_race()
        finally:
            preflight.ROOT = real_root
        assert preflight.FAIL[before:] == []
        print("ok  a missing .github/workflows directory does not crash the gate")
    finally:
        shutil.rmtree(tmp)


def test_real_repository_workflows_pass_right_now():
    """Not a synthetic fixture: the actual committed .github/workflows/*.yml
    files, run through the real gate exactly as preflight.py's main() calls
    it, proving the repository's own fix to bluesky-drafts.yml,
    linkedin-drafts.yml and social-drafts.yml, not just the logic.
    """
    before = len(preflight.FAIL)
    preflight.gate_schedule_fallback_race()
    new_fails = preflight.FAIL[before:]
    assert not new_fails, (
        "a real workflow still lets its schedule branch send unconditionally "
        "while a push fallback keeps a once-a-day ledger: %s" % new_fails)
    print("ok  the real committed workflows pass right now")


if __name__ == "__main__":
    test_pure_check_catches_the_broken_shape()
    test_pure_check_passes_on_the_fixed_shape()
    test_pure_check_ignores_a_workflow_with_no_push_trigger()
    test_pure_check_ignores_a_workflow_with_no_real_ledger()
    test_gate_fails_by_name_on_the_broken_shape()
    test_missing_workflows_dir_does_not_crash()
    test_real_repository_workflows_pass_right_now()
    print("\nall gate_schedule_fallback_race tests passed")
