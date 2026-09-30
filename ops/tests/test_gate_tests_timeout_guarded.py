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

Found live 2026-09-30: even guarded, subprocess.run's own timeout handling
only kills the direct child, never a grandchild that child spawns of its
own (test_audit_catalog.py's own audit_catalog.py subprocess, run while
holding a file lock). gate_tests() now calls preflight._run_bounded(), which
keeps the Popen object and kills the WHOLE process group on a timeout, not
just the pid it started. _check_run_bounded_kills_process_group() below
proves this directly against a real three-generation process tree: a
control reproduces the old bug (the grandchild survives a plain
subprocess.run + .kill()), then the same tree is killed for real by
_run_bounded, which must leave no survivor.

Run:  python ops/tests/test_gate_tests_timeout_guarded.py
"""
import os
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _pid_alive(pid: int) -> bool:
    """True if pid is a live, running process, not merely a still-listed one.

    Found while writing this test: a killed process stays visible to
    os.kill(pid, 0) (no ProcessLookupError) for as long as it remains an
    unreaped zombie, which can be indefinitely in a sandbox with no init
    process to collect orphans. A zombie has already released everything a
    real SIGKILL was meant to free (CPU, open files, any lock it held); it
    is a process-table entry, not a running process, so counting it as
    "alive" would make a working process-group kill look like it failed.
    Reads /proc directly on Linux to tell the difference; falls back to the
    plain kill(pid, 0) check elsewhere (macOS has no /proc), which can only
    make a real leak look clean here, never the reverse.
    """
    if os.name != "posix":
        return False
    try:
        with open("/proc/%d/stat" % pid) as fh:
            state = fh.read().split()[2]
        return state != "Z"
    except (FileNotFoundError, IndexError):
        return False
    except OSError:
        pass
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _check_run_bounded_kills_process_group() -> str:
    """Prove _run_bounded() reaches a grandchild, and that plain
    subprocess.run(...timeout=...) + .kill() (the old gate_tests() shape) does
    not, on the exact same process tree. Both halves matter: proving only the
    fixed half would not show this test can fail on the real defect it was
    written for.

    POSIX only, matching _run_bounded()'s own os.name branch; skipped on
    Windows rather than faked, since a fake would not exercise os.killpg at
    all.
    """
    if os.name != "posix":
        return ""
    with tempfile.TemporaryDirectory() as tmp:
        marker = os.path.join(tmp, "grandchild.pid")
        parent = os.path.join(tmp, "spawn_and_hang.py")
        with open(parent, "w") as fh:
            fh.write(
                "import os, subprocess, sys, time\n"
                "marker = sys.argv[1]\n"
                "child = subprocess.Popen([sys.executable, '-c',\n"
                "    \"import os,sys,time; "
                "open(sys.argv[1],'w').write(str(os.getpid())); "
                "time.sleep(30)\", marker])\n"
                "time.sleep(30)\n"
            )

        def wait_for_marker() -> int:
            for _ in range(100):
                if os.path.exists(marker) and os.path.getsize(marker) > 0:
                    return int(open(marker).read().strip())
                time.sleep(0.1)
            raise RuntimeError("grandchild never wrote its own pid")

        # Control: the OLD shape (subprocess.run + implicit .kill() on
        # TimeoutExpired) reaches only the direct child. The grandchild it
        # spawned must survive this, or the control proves nothing.
        def old_shape():
            if os.path.exists(marker):
                os.remove(marker)
            p = subprocess.Popen([sys.executable, parent, marker])
            try:
                p.communicate(timeout=1)
            except subprocess.TimeoutExpired:
                p.kill()
                p.communicate()
            return wait_for_marker()

        grandchild_pid = old_shape()
        time.sleep(0.3)
        if not _pid_alive(grandchild_pid):
            return ("control failed to reproduce the old bug: the "
                    "grandchild died even under the old subprocess.run + "
                    ".kill() shape, so this test cannot tell fixed from "
                    "broken")
        # Clean up the control's now-orphaned grandchild before it either
        # matters or finishes its own 30s sleep on its own.
        try:
            os.kill(grandchild_pid, 9)
        except ProcessLookupError:
            pass

        # Fixed shape: _run_bounded must kill the WHOLE tree, grandchild
        # included, on the identical timeout. Marker removed first: it still
        # holds the control's own (already-killed) pid, and reading that
        # stale value back here would make a still-broken fix look passing.
        os.remove(marker)
        try:
            preflight._run_bounded([sys.executable, parent, marker], tmp,
                                    os.environ.copy(), 1)
            return "expected TimeoutExpired from _run_bounded, got none"
        except subprocess.TimeoutExpired:
            pass
        grandchild_pid2 = wait_for_marker()
        time.sleep(0.5)
        if _pid_alive(grandchild_pid2):
            try:
                os.kill(grandchild_pid2, 9)
            except ProcessLookupError:
                pass
            return ("_run_bounded left a grandchild process alive after its "
                    "own timeout fired (pid %d): the process-group kill did "
                    "not reach it" % grandchild_pid2)
    return ""


def _run(files, run_impl):
    preflight.FAIL.clear()
    preflight.WARN.clear()
    real_glob = preflight.glob.glob
    real_run_bounded = preflight._run_bounded
    preflight.glob.glob = lambda *a, **k: list(files)
    preflight._run_bounded = run_impl
    try:
        preflight.gate_tests()
    finally:
        preflight.glob.glob = real_glob
        preflight._run_bounded = real_run_bounded
    return list(preflight.FAIL), list(preflight.WARN)


def main():
    fails = []
    with tempfile.TemporaryDirectory() as tmp:
        slow = os.path.join(tmp, "test_slow_thing.py")
        ok = os.path.join(tmp, "test_ok_thing.py")
        for p in (slow, ok):
            open(p, "w").close()

        calls = []

        # gate_tests() now calls preflight._run_bounded(cmd, cwd, env,
        # timeout) instead of subprocess.run(...) directly, so it can hold
        # the Popen object and kill cmd's whole process group on a timeout
        # rather than only the pid it started (see _run_bounded's own
        # docstring). Mocking that one function still drives the real
        # gate_tests() loop end to end: this proves the loop's own
        # behaviour (continue past a timeout, report it, do not crash),
        # not _run_bounded's internal process-group mechanics, which
        # test_run_bounded_kills_process_group below proves separately
        # against a real subprocess.
        def fake_run_bounded(cmd, cwd, env, timeout):
            calls.append(cmd[-1])
            if cmd[-1] == slow:
                raise subprocess.TimeoutExpired(cmd, timeout)
            return 0, ""

        # 1. A slow file must not crash the gate, and the file after it must
        #    still run (proves `continue`, not an unguarded re-raise).
        FAIL, WARN = _run([slow, ok], fake_run_bounded)
        if not any("test_slow_thing.py" in msg and "700s" in msg
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
        FAIL, WARN = _run([ok, slow, third], fake_run_bounded)
        if third not in calls:
            fails.append("a file after a mid-list timeout was never run: "
                         f"{calls!r}")
        if len(FAIL) != 1:
            fails.append(f"expected exactly 1 FAIL entry, got {FAIL!r}")

        # 3. No timeout at all: clean run, no FAIL, matching today's real
        #    green shape so the fix has not widened what counts as broken.
        calls.clear()
        FAIL, WARN = _run([ok, third], fake_run_bounded)
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

    process_group_failure = _check_run_bounded_kills_process_group()
    if process_group_failure:
        fails.append(process_group_failure)

    if fails:
        print("FAIL: " + "; ".join(fails))
        return 1
    print("PASS: gate_tests() and gate_mobile_js_tests() both survive a "
          "test file exceeding their own subprocess timeout, report it "
          "plainly, and keep going")
    return 0


if __name__ == "__main__":
    sys.exit(main())
