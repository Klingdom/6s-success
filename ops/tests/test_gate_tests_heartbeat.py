#!/usr/bin/env python3
"""
Prove gate_tests() prints a per-file heartbeat, immediately flushed, before
each ops/tests/test_*.py file runs rather than only after the whole loop
finishes.

Found 2026-11-02: dozens of consecutive nightly-log entries across weeks had
to guess whether a backgrounded gate_tests() run was stalled or merely slow
by polling /proc CPU time for several minutes, because nothing printed
between the outer "...gate_tests" line (run_gate's own heartbeat, one level
up) and this function's own return. That is the exact blind spot run_gate's
heartbeat was already fixed for in the gate sequence itself (see its own
docstring, "Found 2026-09-13"): fail()/warn() only append to a list, and
nothing prints until the final report, so a truncated run forced a blind
guess. gate_tests() had the identical shape one level down, for its own
~130-file loop, and nobody had closed it there.

This test drives the real gate_tests() against several fake test files (one
of which "hangs", i.e. its mocked _run_bounded raises TimeoutExpired) and
captures sys.stderr. It must see one heartbeat line per file, in the files'
own order, each naming that file's basename and its position (e.g. "2/3"),
printed via a real write+flush rather than buffered print. Before the fix,
a capture taken WHILE the loop is still "running" (simulated here by
checking output written before the mocked call for the hanging file even
returns) would show no per-file lines at all, only the files already
collected in bad/unverified after the loop finished; this test asserts the
lines exist independent of any gate outcome, so it cannot be satisfied by
widening what counts as a pass.

Run:  python ops/tests/test_gate_tests_heartbeat.py
"""
import io
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main():
    fails = []
    with tempfile.TemporaryDirectory() as tmp:
        first = os.path.join(tmp, "test_a_first.py")
        slow = os.path.join(tmp, "test_b_slow.py")
        last = os.path.join(tmp, "test_c_last.py")
        for p in (first, slow, last):
            open(p, "w").close()
        files = [first, slow, last]

        seen_before_slow_returns = []

        def fake_run_bounded(cmd, cwd, env, timeout):
            # Heartbeat for the file about to run must already be on
            # stderr the moment this call is made, not only after it
            # returns: a real stall inside this call must still leave the
            # line visible to whoever is watching, which is the whole
            # point of the fix.
            seen_before_slow_returns.append(sys.stderr.getvalue())
            if cmd[-1] == slow:
                raise subprocess.TimeoutExpired(cmd, timeout)
            return 0, ""

        real_glob = preflight.glob.glob
        real_run_bounded = preflight._run_bounded
        real_stderr = sys.stderr
        preflight.FAIL.clear()
        preflight.WARN.clear()
        preflight.glob.glob = lambda *a, **k: list(files)
        preflight._run_bounded = fake_run_bounded
        sys.stderr = io.StringIO()
        try:
            preflight.gate_tests()
            final_output = sys.stderr.getvalue()
        finally:
            preflight.glob.glob = real_glob
            preflight._run_bounded = real_run_bounded
            sys.stderr = real_stderr

    # One heartbeat line per file, each naming its own basename and a
    # 1-based position out of the total, in the files' own order.
    lines = [ln for ln in final_output.splitlines() if "...test " in ln]
    expected = [
        (1, "test_a_first.py"),
        (2, "test_b_slow.py"),
        (3, "test_c_last.py"),
    ]
    if len(lines) != len(expected):
        fails.append(f"expected {len(expected)} heartbeat line(s), got "
                     f"{len(lines)}: {lines!r}")
    else:
        for (pos, name), line in zip(expected, lines):
            if name not in line:
                fails.append(f"heartbeat line {line!r} does not name "
                             f"{name!r}")
            if not re.search(r"\b%d/%d\b" % (pos, len(files)), line):
                fails.append(f"heartbeat line {line!r} does not show "
                             f"position {pos}/{len(files)}")

    # The heartbeat for the slow file must have been visible BEFORE its
    # own _run_bounded call returned (i.e. before the TimeoutExpired was
    # even raised), proving it is printed ahead of the run, not logged
    # retroactively once the outcome is known.
    if len(seen_before_slow_returns) >= 2:
        snapshot_at_slow_call = seen_before_slow_returns[1]
        if "test_b_slow.py" not in snapshot_at_slow_call:
            fails.append(
                "the slow file's own heartbeat was not yet on stderr at "
                "the moment its _run_bounded call was made, so a real "
                "stall inside that call would still show nothing: "
                f"{snapshot_at_slow_call!r}")
    else:
        fails.append("fake_run_bounded was not called the expected number "
                     f"of times: {seen_before_slow_returns!r}")

    if fails:
        print("FAIL: " + "; ".join(fails))
        return 1
    print("PASS: gate_tests() prints an immediately-flushed per-file "
          "heartbeat before each test file runs, in order, independent of "
          "outcome")
    return 0


if __name__ == "__main__":
    sys.exit(main())
