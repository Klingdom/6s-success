#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_growth_playbook_linkedin_current() catches
GROWTH-PLAYBOOK.md describing LinkedIn as a blocked, one-time batch of
drafts once it is a live, running channel.

Found 2026-09-12: the channel table's LinkedIn row still said "posting
blocked on Phil... Ten posts written and waiting in Phil's inbox for him
to publish," describing the 2026-08-24 launch day, not the channel since.
It has run daily since, GOALS.md O1 already credits it with 17 real
sessions, and it is not blocked: Phil reads three fresh drafts every
morning and sends the one that fits. Fixed by hand; this gate stops the
correction silently regressing back to either retired phrase.

Run:  python ops/tests/test_gate_growth_playbook_linkedin_current.py
"""
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

FIXED = (
    "# Growth Playbook\n\n"
    "| Channel | State | Notes |\n"
    "|---|---|---|\n"
    "| LinkedIn (Phil's) | Live and working | Corrected 2026-09-12: "
    "three fresh drafts every morning, 17 real sessions so far. |\n"
)

STALE_TEN_POSTS = (
    "# Growth Playbook\n\n"
    "| LinkedIn (Phil's) | Drafted, posting blocked on Phil elsewhere | "
    "Daily drafts already automated at 8am Denver. Ten posts written and "
    "waiting in Phil's inbox for him to publish. |\n"
)

STALE_BLOCKED = (
    "# Growth Playbook\n\n"
    "| LinkedIn (Phil's) | posting blocked on Phil | some other wording "
    "entirely, no batch-of-ten claim here. |\n"
)


def _run(body):
    tmp = tempfile.mkdtemp()
    io.open(os.path.join(tmp, "GROWTH-PLAYBOOK.md"), "w",
            encoding="utf-8").write(body)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    old_fail, old_warn = list(preflight.FAIL), list(preflight.WARN)
    preflight.FAIL.clear()
    preflight.WARN.clear()
    try:
        preflight.gate_growth_playbook_linkedin_current()
        failed = bool(preflight.FAIL)
        msg = preflight.FAIL[0][1] if preflight.FAIL else ""
    finally:
        preflight.ROOT = old_root
        preflight.FAIL[:] = old_fail
        preflight.WARN[:] = old_warn
    return failed, msg


def main():
    cases = [
        ("fixed file passes clean", FIXED, False, None),
        ("stale ten-posts claim fails", STALE_TEN_POSTS, True, "ten"),
        ("stale blocked claim fails", STALE_BLOCKED, True, "blocked"),
    ]
    failures = []
    for name, body, want_fail, want_substr in cases:
        got_fail, msg = _run(body)
        if got_fail != want_fail:
            failures.append(
                "%s: expected failed=%s, got failed=%s (msg=%r)"
                % (name, want_fail, got_fail, msg))
        elif want_fail and want_substr.lower() not in msg.lower():
            failures.append(
                "%s: failure message %r did not name %r"
                % (name, msg, want_substr))

    no_file = tempfile.mkdtemp()
    old_root = preflight.ROOT
    preflight.ROOT = no_file
    old_fail = list(preflight.FAIL)
    preflight.FAIL.clear()
    try:
        preflight.gate_growth_playbook_linkedin_current()
        no_file_failed = bool(preflight.FAIL)
        no_file_msg = preflight.FAIL[0][1] if preflight.FAIL else ""
    finally:
        preflight.ROOT = old_root
        preflight.FAIL[:] = old_fail
    if not no_file_failed or "does not exist" not in no_file_msg:
        failures.append("missing GROWTH-PLAYBOOK.md should fail naming the "
                         "missing file, got: %r" % (no_file_msg,))

    real_root = ROOT
    old_root = preflight.ROOT
    preflight.ROOT = real_root
    old_fail = list(preflight.FAIL)
    preflight.FAIL.clear()
    try:
        preflight.gate_growth_playbook_linkedin_current()
        real_failed = bool(preflight.FAIL)
        real_msg = preflight.FAIL[0][1] if preflight.FAIL else ""
    finally:
        preflight.ROOT = old_root
        preflight.FAIL[:] = old_fail
    if real_failed:
        failures.append("real, fixed GROWTH-PLAYBOOK.md wrongly failed: %r"
                         % (real_msg,))

    total = len(cases) + 2
    if failures:
        print("FAIL: %d of %d cases" % (len(failures), total))
        for f in failures:
            print("  -", f)
        return 1
    print("PASS: %d of %d cases" % (total, total))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
