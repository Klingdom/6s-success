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


def _posix_shell():
    """A bash that has proved itself, or None.

    Added 2026-10-01 after this test reported FAIL for a reason that had
    nothing to do with ops/run_preflight.sh. From Python on this machine,
    subprocess resolving the bare name "bash" finds Windows' own
    System32/bash.exe, the WSL launcher, which answers every invocation
    with "Windows Subsystem for Linux must be updated" in UTF-16 and exits
    nonzero. The shell script never ran at all.

    That mattered far more than the one red line it produced. Cases 1 and 3
    below assert exit code 1, and WSL's own refusal exits 1, so BOTH OF THEM
    WERE PASSING FOR THE WRONG REASON: they would have passed against a
    run_preflight.sh deleted from disk, which is the precise shape of
    not-a-check this file was written to prevent. Only case 2, which asserts
    0, was honest enough to go red.

    So the interpreter is no longer assumed. Each candidate must round-trip
    a known string on stdout before it is used, and if none can, the test
    reports NOT VERIFIED and exits 0, which gate_tests() counts as unchecked
    rather than passing.
    """
    candidates = [
        os.environ.get("POSIX_SHELL"),
        "C:/Program Files/Git/bin/bash.exe",
        "C:/Program Files (x86)/Git/bin/bash.exe",
        "sh",
        "bash",
    ]
    for cand in candidates:
        if not cand:
            continue
        try:
            r = subprocess.run([cand, "-c", "echo posix-shell-probe-ok"],
                               capture_output=True, text=True, timeout=20)
        except Exception:                             # noqa: BLE001
            continue
        if r.returncode == 0 and "posix-shell-probe-ok" in (r.stdout or ""):
            return cand
    return None


def _missing_tool(shell):
    """The name of a tool ops/run_preflight.sh needs and this shell lacks.

    Second half of the same 2026-10-01 finding. Once a real bash was found,
    the script ran and died on `setsid: command not found`: Git Bash for
    Windows ships nohup but not setsid, and the wrapper launches with both.
    Case 2 went red again, and again for a reason that says nothing about
    whether the wrapper derives its exit code correctly.

    Checked up front rather than by reading the failure text afterwards, which
    is the distinction that keeps this honest: a missing tool is established
    BEFORE any case runs, so it can never be used to explain away a case that
    failed for a real reason.
    """
    for tool in ("setsid", "nohup"):
        try:
            r = subprocess.run([shell, "-c", "command -v " + tool],
                               capture_output=True, text=True, timeout=20)
        except Exception:                             # noqa: BLE001
            return tool
        if r.returncode != 0 or not (r.stdout or "").strip():
            return tool
    return None


def _run(shell: str, variant: str) -> "tuple[int, str]":
    r = subprocess.run([shell, variant], cwd=ROOT, capture_output=True,
                        text=True, timeout=30)
    return r.returncode, r.stdout + r.stderr


def main() -> int:
    fails = []
    shell = _posix_shell()
    if shell is None:
        print("NOT VERIFIED: no POSIX shell on this machine could round-trip "
              "a probe string, so ops/run_preflight.sh was never executed and "
              "cases 1 to 3 below prove nothing. Set POSIX_SHELL to a working "
              "bash to exercise them.")
        return 0
    lacks = _missing_tool(shell)
    if lacks is not None:
        print("NOT VERIFIED: %s has no %r, which ops/run_preflight.sh needs to "
              "launch at all, so cases 1 to 3 below prove nothing about its "
              "exit-code derivation. Case 4, a static read of the committed "
              "script, is the only one that still means anything here."
              % (shell, lacks))
        real_src = open(SCRIPT, encoding="utf-8").read()
        if re.search(r'wait' + chr(92) + 's+"' + chr(92) + '$PID"'
                     + chr(92) + 's*' + chr(92) + 'n' + chr(92) + 's*CODE='
                     + chr(92) + '$' + chr(92) + '?', real_src):
            print("FAIL")
            print(" - ops/run_preflight.sh reverted to deriving CODE directly "
                  "from the `wait` return value, the exact shape that silently "
                  "reports 0 on a real failure once the job is disowned")
            return 1
        return 0
    with tempfile.TemporaryDirectory() as tmp:
        # 1. The real regression shape: preflight.py's own real FAIL summary
        #    shape must produce exit code 1, not 0.
        fail_cmd = ('python3 -c "print(chr(32)*2+'
                    '\'FAIL  stray-probe-files      1 leftover thing\'); '
                    'print(); print(chr(32)*2+\'1 gate(s) failed, 2 '
                    'warning(s). Nothing should ship on this.\')"')
        variant = _make_variant(tmp, fail_cmd)
        code, out = _run(shell, variant)
        if code != 1:
            fails.append("a real gate-FAIL summary shape produced exit "
                         "code %d, not 1 (this is the exact 2026-09-30 "
                         "regression: the wrapper reporting success on a "
                         "real failure): output=%r" % (code, out))

        # 2. The real pass shape must still produce exit code 0.
        pass_cmd = ('python3 -c "print(chr(32)*2+\'every gate passed, 3 '
                    'warning(s) worth a read\')"')
        variant = _make_variant(tmp, pass_cmd)
        code, out = _run(shell, variant)
        if code != 0:
            fails.append("a real gate-pass summary shape produced exit "
                         "code %d, not 0: output=%r" % (code, out))

        # 3. A crash before either summary line (no recognisable shape at
        #    all) must be treated as failure, never a silent false pass.
        crash_cmd = 'python3 -c "import sys; sys.exit(1)"'
        variant = _make_variant(tmp, crash_cmd)
        code, out = _run(shell, variant)
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
