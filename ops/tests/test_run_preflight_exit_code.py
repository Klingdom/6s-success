#!/usr/bin/env python3
"""
Prove ops/run_preflight.sh reports the real exit code of the preflight.py run
it launches, rather than always reporting 0.

Found live 2026-09-30: a real preflight.py run had one genuine gate FAIL
("stray-probe-files"), confirmed by reading the log body directly, yet
ops/run_preflight.sh reported exit code 0 to both its own $LOG.exitcode
marker file and its caller. Root cause: `disown "$PID"` (kept so a killed
wrapper's own job-control SIGHUP bookkeeping cannot take a fresh launch down
with it) makes bash's own `wait "$PID"` on that pid always return 0
regardless of the process's real exit status once it has been disowned.
Every "preflight passed" claim in this repository's history that trusted
this wrapper's own exit code rather than reading the log body directly
could have been exactly this wrong, silently.

Fixed by deriving the reported exit code from preflight.py's own final
summary line in the log ("every gate passed" vs "N gate(s) failed,"),
never from `wait`'s return value, and treating anything else (a crash
before either line) as failure rather than a silent false pass.

This test drives the REAL ops/run_preflight.sh (a copy with only the
`setsid nohup python ops/preflight.py "$@"` line replaced by a fake command
that prints one of preflight.py's own two real summary shapes, and the
hardcoded /tmp state path replaced with a per-test path so this cannot
collide with, or be confused for, a real concurrent preflight run in this
shared environment) rather than a reimplementation of its logic, so a
regression in the real file is what this test would actually catch.

Run:  python ops/tests/test_run_preflight_exit_code.py
"""
import os
import re
import stat
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, "ops", "run_preflight.sh")

REAL_LAUNCH_LINE = 'setsid nohup python ops/preflight.py "$@" >"$LOG" 2>&1 < /dev/null &'
REAL_STATE_LINE = 'STATE="/tmp/.run_preflight_state"'


def _make_variant(tmp: str, fake_cmd: str) -> str:
    src = open(SCRIPT, encoding="utf-8").read()
    if src.count(REAL_LAUNCH_LINE) != 1:
        raise RuntimeError("ops/run_preflight.sh's launch line has changed "
                            "shape; this test's substitution point no "
                            "longer matches exactly once")
    if src.count(REAL_STATE_LINE) != 1:
        raise RuntimeError("ops/run_preflight.sh's STATE line has changed "
                            "shape; this test's substitution point no "
                            "longer matches exactly once")
    state_path = os.path.join(tmp, "state")
    new = src.replace(
        REAL_LAUNCH_LINE,
        'setsid nohup %s >"$LOG" 2>&1 < /dev/null &' % fake_cmd
    ).replace(REAL_STATE_LINE, 'STATE="%s"' % state_path)
    path = os.path.join(tmp, "run_preflight_variant.sh")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(new)
    os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
    return path


def _run(variant: str) -> "tuple[int, str]":
    r = subprocess.run(["bash", variant], cwd=ROOT, capture_output=True,
                        text=True, timeout=30)
    return r.returncode, r.stdout + r.stderr


def main() -> int:
    fails = []
    with tempfile.TemporaryDirectory() as tmp:
        # 1. The real regression shape: preflight.py's own real FAIL summary
        #    shape must produce exit code 1, not 0.
        fail_cmd = ('python3 -c "print(chr(32)*2+'
                    '\'FAIL  stray-probe-files      1 leftover thing\'); '
                    'print(); print(chr(32)*2+\'1 gate(s) failed, 2 '
                    'warning(s). Nothing should ship on this.\')"')
        variant = _make_variant(tmp, fail_cmd)
        code, out = _run(variant)
        if code != 1:
            fails.append("a real gate-FAIL summary shape produced exit "
                         "code %d, not 1 (this is the exact 2026-09-30 "
                         "regression: the wrapper reporting success on a "
                         "real failure): output=%r" % (code, out))

        # 2. The real pass shape must still produce exit code 0.
        pass_cmd = ('python3 -c "print(chr(32)*2+\'every gate passed, 3 '
                    'warning(s) worth a read\')"')
        variant = _make_variant(tmp, pass_cmd)
        code, out = _run(variant)
        if code != 0:
            fails.append("a real gate-pass summary shape produced exit "
                         "code %d, not 0: output=%r" % (code, out))

        # 3. A crash before either summary line (no recognisable shape at
        #    all) must be treated as failure, never a silent false pass.
        crash_cmd = 'python3 -c "import sys; sys.exit(1)"'
        variant = _make_variant(tmp, crash_cmd)
        code, out = _run(variant)
        if code != 1:
            fails.append("an unrecognisable log (simulating a crash before "
                         "either summary line) produced exit code %d, not "
                         "1: output=%r" % (code, out))

        # 4. The real committed script still contains the fix, not just
        #    this test's own substituted copy: the exit code must be
        #    derived from the log, and `disown` must still be present
        #    (removing it, rather than fixing the exit-code derivation,
        #    would be a different and also-valid fix, but this proves
        #    whichever shape ships still gets the two cases above right,
        #    which the copy already checked; this only guards against a
        #    naive revert straight back to `wait "$PID"; CODE=$?`).
        real_src = open(SCRIPT, encoding="utf-8").read()
        if re.search(r'wait\s+"\$PID"\s*\n\s*CODE=\$\?', real_src):
            fails.append("ops/run_preflight.sh reverted to deriving CODE "
                         "directly from `wait \"$PID\"`, the exact shape "
                         "that silently reports 0 on a real failure once "
                         "the job has been disowned")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: ops/run_preflight.sh reports the real preflight.py exit "
          "code (pass/fail/crash), 4/4 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
