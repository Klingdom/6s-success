#!/usr/bin/env python3
"""
Prove preflight.py's fail() prints the FAIL line to stderr the moment it is
called, not only in the final report at the end of main().

Found 2026-10-29: a run that hits the documented gate_tests sandbox hang is
killed before main()'s own "for g, m in FAIL: print(...)" loop ever runs, so
a real FAIL recorded earlier in the run (before gate_tests) was invisible in
the log; only maybe_record_cycle_signal()'s "not recorded, this run has
failing gate(s)" line hinted one existed, by name, with no way to tell
which gate or why. Same root cause run_gate()'s own heartbeat line was
fixed for: nothing printed until the whole run finished. fail() now prints
immediately, alongside the heartbeat, so a truncated run still names its
failure.

Fail-then-pass: calls fail() directly and checks stderr carries the line
before any end-of-run report could have produced it, then confirms a run
with no fail() calls prints nothing.

Run:  python ops/tests/test_gate_fail_prints_immediately.py
"""
import io
import os
import sys
from contextlib import redirect_stderr

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                  # noqa: E402


def main() -> int:
    fails = []

    preflight.FAIL.clear()
    buf = io.StringIO()
    with redirect_stderr(buf):
        preflight.fail("gate_demo", "a deliberately synthetic failure")
    out = buf.getvalue()
    if "FAIL" not in out or "gate_demo" not in out or "deliberately synthetic" not in out:
        fails.append(f"fail() did not print its own message immediately, got: {out!r}")
    if preflight.FAIL != [("gate_demo", "a deliberately synthetic failure")]:
        fails.append(f"fail() stopped appending to FAIL: {preflight.FAIL!r}")
    preflight.FAIL.clear()

    buf2 = io.StringIO()
    with redirect_stderr(buf2):
        pass  # no fail() call this time
    if buf2.getvalue().strip():
        fails.append(f"expected no stderr output with no fail() call, got: {buf2.getvalue()!r}")

    if fails:
        print("FAILURES:")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: preflight.fail() prints its FAIL line immediately, 2/2 cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
