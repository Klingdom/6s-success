#!/usr/bin/env python3
"""
Prove ops/build_seo.py's _committed_date() and ops/check_cron_cadence.py's
last_changed() never report a shallow-clone boundary commit's own date as a
real commit date for an unrelated path.

Found 2026-11-18, PM check-in: ops/cold_read_ledger.py's last_touched() and
_batch_last_touched() had this exact bug (307 false "stale" entries, every
one carrying the boundary commit's own date) and were fixed the same cycle.
The same `git log -1 --format=... -- path` call, with no guard against the
boundary commit, was still live in two sibling tools: _committed_date()
feeds the deployed sitemap.xml's <lastmod> directly, and last_changed()
feeds gate_cron_cadence_workflows_registry_current's "did the schedule
change recently" check. Fixed both the same way: capture the commit hash
alongside the date/timestamp and refuse to report one that lands on
`.git/shallow`'s own boundary commit.

This cannot be reproduced by actually shrinking this checkout mid-test, so
it fakes the boundary by monkeypatching each module's own
_shallow_boundary_commits() to report a real commit this repository's
history already has, the same technique
ops/tests/test_cold_read_ledger_stale.py's equivalent case uses.

Run:  python ops/tests/test_date_guard_shallow_boundary.py
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import build_seo                                               # noqa: E402
import check_cron_cadence                                       # noqa: E402


def _real_commit_for(path: str) -> tuple:
    out = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", path],
        cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return out or None


def main() -> int:
    fails = []

    # 1. build_seo._committed_date(): a faked boundary commit must yield
    #    None, never that commit's own date.
    target = os.path.join(ROOT, "ops", "build_seo.py")
    real_hash = _real_commit_for("ops/build_seo.py")
    if not real_hash:
        fails.append("could not get a real commit for ops/build_seo.py "
                      "to fake a shallow boundary")
    else:
        orig = build_seo._shallow_boundary_commits
        build_seo._shallow_boundary_commits = lambda: {real_hash}
        try:
            result = build_seo._committed_date(target)
            if result is not None:
                fails.append(
                    "_committed_date() returned %r for a path whose only "
                    "answer (git log -1) is the faked shallow boundary "
                    "commit, instead of None" % (result,))
        finally:
            build_seo._shallow_boundary_commits = orig

    # 2. _committed_date() must still work normally once the real boundary
    #    (empty set on this fully-fetched checkout, or the real one if
    #    still shallow) is restored: real committed files return a 10-char
    #    ISO date, not None.
    normal = build_seo._committed_date(target)
    if normal is not None and len(normal) != 10:
        fails.append("_committed_date() returned a non-ISO-date value on "
                      "the real, unfaked boundary: %r" % (normal,))

    # 3. check_cron_cadence.last_changed(): same guard, same fake technique,
    #    against a real workflow file.
    wf_rel = "checks.yml"
    wf_path = os.path.join(".github", "workflows", wf_rel)
    if not os.path.isfile(os.path.join(ROOT, wf_path)):
        fails.append("%s does not exist; pick a real workflow file for "
                      "this test" % (wf_path,))
    else:
        real_wf_hash = _real_commit_for(wf_path)
        if not real_wf_hash:
            fails.append("could not get a real commit for %s to fake a "
                          "shallow boundary" % (wf_path,))
        else:
            orig_cc = check_cron_cadence._shallow_boundary_commits
            check_cron_cadence._shallow_boundary_commits = lambda: {real_wf_hash}
            try:
                result = check_cron_cadence.last_changed(wf_rel)
                if result is not None:
                    fails.append(
                        "last_changed() returned %r for a workflow whose "
                        "only answer (git log -1) is the faked shallow "
                        "boundary commit, instead of None" % (result,))
            finally:
                check_cron_cadence._shallow_boundary_commits = orig_cc

        # 4. Normal case: a real workflow file's last_changed() is either
        #    None (git unavailable) or a parseable ISO timestamp, never a
        #    bare non-ISO string.
        normal_wf = check_cron_cadence.last_changed(wf_rel)
        if normal_wf is not None and "T" not in normal_wf:
            fails.append("last_changed() returned a non-ISO-timestamp "
                          "value on the real, unfaked boundary: %r"
                          % (normal_wf,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS (4 cases)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
