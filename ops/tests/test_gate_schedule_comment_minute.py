#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_schedule_past_comments() catches a workflow's
own prose disagreeing with its own cron minute.

Found 2026-09-12, cold-reading status-email.yml: its cron minute moved from
:10 to :23 on 2026-08-31 (f879787d), to dodge a congested minute, the same
fix hourly-brief.yml and fulfil-orders.yml got that day. The inline trailing
comment on the cron line was updated to "23 past"; the block comment three
lines above still read "Ten past" and nobody had ever compared the two.
Fixed by hand; this test proves the pure check both catches that exact
regression and stays quiet on every real workflow file today.

Run:  python ops/tests/test_gate_schedule_comment_minute.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

REAL_BUG = """
on:
  schedule:
    # Ten past every fourth hour UTC.
    - cron: '23 1,5,9,13,17,21 * * *'      # six times a day at 23 past
"""

FIXED = """
on:
  schedule:
    # 23 past every fourth hour UTC.
    - cron: '23 1,5,9,13,17,21 * * *'      # six times a day at 23 past
"""

MULTI_MINUTE_OK = """
on:
  schedule:
    # fires at 7 and 37 past, off the contended :00 and :30
    - cron: '7,37 * * * *'
"""

NO_PAST_PHRASE = """
on:
  schedule:
    - cron: '41 14 * * *'
    - cron: '41 18 * * *'
"""

HOURLY_WILDCARD_MINUTE = """
on:
  schedule:
    # fires every minute of every hour, nothing to claim
    - cron: '* * * * *'
"""


def test_real_regression_caught():
    problems = preflight.check_schedule_past_comments({"status-email.yml": REAL_BUG})
    assert len(problems) == 1, problems
    assert "status-email.yml" in problems[0], problems[0]
    assert "Ten" in problems[0] and "23" in problems[0], problems[0]


def test_fixed_text_clean():
    problems = preflight.check_schedule_past_comments({"status-email.yml": FIXED})
    assert problems == [], problems


def test_multi_minute_cron_ok():
    problems = preflight.check_schedule_past_comments(
        {"fulfil-orders.yml": MULTI_MINUTE_OK})
    assert problems == [], problems


def test_no_past_phrase_is_silent():
    problems = preflight.check_schedule_past_comments(
        {"roadmap-report.yml": NO_PAST_PHRASE})
    assert problems == [], problems


def test_wildcard_minute_field_is_not_digits_no_false_positive():
    problems = preflight.check_schedule_past_comments(
        {"weird.yml": HOURLY_WILDCARD_MINUTE})
    assert problems == [], problems


def test_real_committed_files_are_clean():
    wf_dir = os.path.join(ROOT, ".github", "workflows")
    texts = {}
    for fn in sorted(os.listdir(wf_dir)):
        if fn.endswith((".yml", ".yaml")):
            with open(os.path.join(wf_dir, fn), encoding="utf-8") as f:
                texts[fn] = f.read()
    problems = preflight.check_schedule_past_comments(texts)
    assert problems == [], problems


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print("  ok   " + t.__name__)
        except AssertionError as e:
            failed += 1
            print("  FAIL " + t.__name__ + ": " + str(e))
    print(f"\n{len(tests) - failed} of {len(tests)} cases pass")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
