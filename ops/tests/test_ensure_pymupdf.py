#!/usr/bin/env python3
"""
Prove ops/preflight.py's ensure_pymupdf() actually retries a transient
install failure and reports its real result, rather than firing one install
and moving on regardless of outcome.

Found 2026-09-10: this session's own first preflight run hit exactly this.
pip's fetch of pymupdf timed out once (ReadTimeoutError from
files.pythonhosted.org, ordinary cold-tunnel slowness, not a policy denial)
and the old bootstrap_fresh_sandbox() fired a single pip install and moved
on regardless of its exit code. Every PDF gate_affiliate() reads
(delivered_documents()) then reads as unreadable and fails closed, correctly
by that check's own design, and test_affiliate.py fails alongside it, both
looking like a real content defect until a second, unrelated preflight run
happens to pass because a later network attempt succeeded. Rerunning
preflight.py itself is not a controlled reproduction of that timing, so this
test drives ensure_pymupdf() directly with fake importable()/install()
callables instead, proving: a first-attempt failure that succeeds on retry
returns True and the caller can tell it took more than one attempt; a
failure that never succeeds returns False rather than silently claiming
success; and a package already importable makes no install call at all.

Run:  python ops/tests/test_ensure_pymupdf.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    # 1. Already importable: no install call at all.
    calls = []
    ok = preflight.ensure_pymupdf(
        importable=lambda: True,
        install=lambda: calls.append(1),
        attempts=3,
    )
    if not ok or calls:
        fails.append("already-importable case installed anyway: "
                      "ok=%r calls=%r" % (ok, calls))

    # 2. Fails once (the real 2026-09-10 shape), succeeds on retry.
    state = {"tries": 0}

    def flaky_importable():
        # False before any install call, False on the first post-install
        # check (the timed-out attempt), True from the second onward.
        return state["tries"] >= 2

    def flaky_install():
        state["tries"] += 1

    ok = preflight.ensure_pymupdf(
        importable=flaky_importable, install=flaky_install, attempts=3)
    if not ok:
        fails.append("a transient failure that recovers on retry still "
                     "reported False")
    if state["tries"] != 2:
        fails.append("expected exactly 2 install attempts before success, "
                     "got %d" % state["tries"])

    # 3. Never succeeds: must report False, not swallow the failure.
    ok = preflight.ensure_pymupdf(
        importable=lambda: False,
        install=lambda: None,
        attempts=3,
    )
    if ok:
        fails.append("a genuinely unavailable package was reported "
                     "importable")

    # 4. attempts is honoured exactly, not off by one.
    count = {"n": 0}
    preflight.ensure_pymupdf(
        importable=lambda: False,
        install=lambda: count.__setitem__("n", count["n"] + 1),
        attempts=2,
    )
    if count["n"] != 2:
        fails.append("attempts=2 should install exactly twice, got %d"
                     % count["n"])

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: ensure_pymupdf, 4/4 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
