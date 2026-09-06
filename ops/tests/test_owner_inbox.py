#!/usr/bin/env python3
"""
Prove owner_inbox.main() checks third-party mail even when the owner-specific
check has no credential, found 2026-09-06 cold-reading the money/safety
domain.

unread_from_owner() needs five things (IMAP_HOST/PORT/USER/PASS and
OWNER_EMAIL); unread_needing_action() needs only the first four. main() used
to return immediately when unread_from_owner() reported no credential
(returning None), which meant a missing OWNER_EMAIL alone -- with a fully
working IMAP connection otherwise -- silently skipped the third-party
affiliate/dispute/chargeback scan and printed "no mail credential here, so
the inbox was NOT checked" even though the mailbox was reachable. This is
the exact "unchecked read as nothing to do" shape the file's own docstring
names as an eight-day incident (an Impact decline sitting unread while
OWNER-ACTIONS.md said the application was pending our own click), just one
level higher: this time the checker itself, not a human, would have been
the one to miss it.

Run:  python ops/tests/test_owner_inbox.py
"""
import contextlib
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import owner_inbox as oi                                      # noqa: E402


def with_stubs(owner_result, third_result, fn):
    real_owner, real_third = oi.unread_from_owner, oi.unread_needing_action
    oi.unread_from_owner = lambda: owner_result
    oi.unread_needing_action = lambda: third_result
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = fn()
    finally:
        oi.unread_from_owner, oi.unread_needing_action = real_owner, real_third
    return rc, buf.getvalue()


def main() -> int:
    fails = []

    # The regression itself: OWNER_EMAIL missing (owner-check returns None)
    # but the mailbox is otherwise reachable and finds a real actionable
    # third-party message. It must be printed and must not be swallowed.
    rc, out = with_stubs(None, ["2026-08-29 | Impact <noreply@impact.com> | Application Update"],
                          oi.main)
    if "Application Update" not in out:
        fails.append("third-party finding was silently skipped when only "
                     "the owner-check credential was missing: " + repr(out))
    if rc != 1:
        fails.append(f"main() should return 1 with an actionable third-party "
                     f"message pending, got {rc}")

    # Both unavailable: both "not checked" messages must appear, and the
    # return code must be 0 (nothing known to be waiting, not nothing to do).
    rc, out = with_stubs(None, None, oi.main)
    if out.count("NOT checked") < 1 or "inbox was NOT checked" not in out:
        fails.append("owner-check unchecked message missing: " + repr(out))
    if "third-party mail NOT checked" not in out:
        fails.append("third-party unchecked message missing when both are "
                     "unavailable: " + repr(out))
    if rc != 0:
        fails.append(f"main() with nothing knowable should return 0, got {rc}")

    # Owner has a real unread message: still reported, and third-party still
    # runs alongside it rather than being replaced by it.
    rc, out = with_stubs(["2026-09-01 | fix stripe issues immediately"], [], oi.main)
    if "fix stripe issues immediately" not in out:
        fails.append("a real owner message was not printed: " + repr(out))
    if "nothing unread from a third party" not in out:
        fails.append("third-party check did not run alongside a real owner "
                     "finding: " + repr(out))
    if rc != 1:
        fails.append(f"main() with an owner message pending should return 1, got {rc}")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("owner_inbox.main() independent-checks: 3 case(s) passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
