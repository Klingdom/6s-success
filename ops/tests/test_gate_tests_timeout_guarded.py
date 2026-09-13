#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_tests() and gate_mobile_js_tests() cannot be
crashed by a slow test file.

Found 2026-09-13, run 909: gate_tests() launches each ops/tests/test_*.py file
with subprocess.run(..., timeout=900), but never caught the TimeoutExpired
that call itself can raise. When a real Chrome-heavy test file (already twice
hardened this same day against an uncaught TimeoutExpired *inside* itself) ran
long enough under genuine CI contention, this call raised the identical
exception one frame further out, in gate_tests()'s own caller, and crashed the
whole gate with a raw traceback instead of a controlled FAIL: "1 of 129 test
file(s) failed: [...subprocess.TimeoutExpired...]", every test file after the
slow one silently never run. Same defect class already fixed twice today
inside test_gate_etsy_pdfs_current.py, just one call frame further out and
still live when run 909 hit it.

This test drives the real gate_tests() against two fake test files: one that
would exceed the timeout (subprocess.run mocked to raise TimeoutExpired for
it) and one that exits 1 normally. Before the fix, the mocked TimeoutExpired
propagated out of gate_tests() uncaught; after the fix, it is recorded as a
plain FAIL entry naming the file, and the loop continues to the next file
rather than stopping.

Auditing every subprocess.run(...timeout=...) call inside a `for` loop across
ops/*.py (the specific shape that matters: a gate checking several
independent items where one slow item must not silently cancel the rest)
found one more live instance in this same file: gate_mobile_js_tests() has
the identical unguarded call in its own per-file loop, never hit in practice
only because no mobile lib test file has ever run long enough to matter.
Fixed the same way; covered below.

Run:  python ops/tests/test_gate_tests_timeout_guarded.py
"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _run(files, run_impl):
    preflight.FAIL.clear()
    preflight.WARN.clear()
    real_glob = preflight.glob.glob
    real_run = preflight.subprocess.run
    preflight.glob.glob = lambda *a, **k: list(files)
    preflight.subprocess.run = run_impl
    try:
        preflight.gate_tests()
    finally:
        preflight.glob.glob = real_glob
        preflight.subprocess.run = real_run
    return list(preflight.FAIL), list(preflight.WARN)


def main():
    fails = []
    with tempfile.TemporaryDirectory() as tmp:
        slow = os.path.join(tmp, "test_slow_thing.py")
        ok = os.path.join(tmp, "test_ok_thing.py")
        for p in (slow, ok):
            open(p, "w").close()

        calls = []

        def fake_run(cmd, **kw):
            calls.append(cmd[-1])
            if cmd[-1] == slow:
                raise subprocess.TimeoutExpired(cmd, kw.get("timeout"))
            return subprocess.CompletedProcess(cmd, 0, "", "")

        # 1. A slow file must not crash the gate, and the file after it must
        #    still run (proves `continue`, not an unguarded re-raise).
        FAIL, WARN = _run([slow, ok], fake_run)
        if not any("test_slow_thing.py" in msg and "1200s" in msg
                   for _, msg in FAIL):
            fails.append(f"no controlled FAIL naming the slow file: {FAIL!r}")
        if ok not in calls:
            fails.append("the file after the timeout was never run: "
                         f"{calls!r}")

        # 2. Same shape, but the slow file is not the last one: everything
        #    after it must still be attempted, not abandoned.
        third = os.path.join(tmp, "test_third_thing.py")
        open(third, "w").close()
        calls.clear()
        FAIL, WARN = _run([ok, slow, third], fake_run)
        if third not in calls:
            fails.append("a file after a mid-list timeout was never run: "
                         f"{calls!r}")
        if len(FAIL) != 1:
            fails.append(f"expected exactly 1 FAIL entry, got {FAIL!r}")

        # 3. No timeout at all: clean run, no FAIL, matching today's real
        #    green shape so the fix has not widened what counts as broken.
        calls.clear()
        FAIL, WARN = _run([ok, third], fake_run)
        if FAIL:
            fails.append(f"a clean run should not FAIL: {FAIL!r}")

    # gate_mobile_js_tests(): identical shape, its own loop and glob target.
    with tempfile.TemporaryDirectory() as tmp:
        slow = os.path.join(tmp, "slow.test.js")
        ok = os.path.join(tmp, "ok.test.js")
        for p in (slow, ok):
            open(p, "w").close()
        calls = []

        def fake_run(cmd, **kw):
            calls.append(cmd[-1])
            if cmd[-1] == slow:
                raise subprocess.TimeoutExpired(cmd, kw.get("timeout"))
            return subprocess.CompletedProcess(cmd, 0, "", "")

        preflight.FAIL.clear()
        preflight.WARN.clear()
        real_glob, real_run, real_which = (preflight.glob.glob,
                                           preflight.subprocess.run,
                                           preflight.shutil.which)
        preflight.glob.glob = lambda *a, **k: [slow, ok]
        preflight.subprocess.run = fake_run
        preflight.shutil.which = lambda name: "/usr/bin/node"
        try:
            preflight.gate_mobile_js_tests()
        finally:
            preflight.glob.glob = real_glob
            preflight.subprocess.run = real_run
            preflight.shutil.which = real_which

        if not any("slow.test.js" in msg and "120s" in msg
                   for _, msg in preflight.FAIL):
            fails.append("gate_mobile_js_tests: no controlled FAIL naming "
                         f"the slow file: {preflight.FAIL!r}")
        if ok not in calls:
            fails.append("gate_mobile_js_tests: the file after the timeout "
                         f"was never run: {calls!r}")

    if fails:
        print("FAIL: " + "; ".join(fails))
        return 1
    print("PASS: gate_tests() and gate_mobile_js_tests() both survive a "
          "test file exceeding their own subprocess timeout, report it "
          "plainly, and keep going")
    return 0


if __name__ == "__main__":
    sys.exit(main())
