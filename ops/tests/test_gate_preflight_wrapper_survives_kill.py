#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_preflight_wrapper_survives_kill() actually
catches the wrapper being missing, non-executable, or downgraded to a form
that no longer uses setsid (LRN-0021: nohup+disown alone do not survive a
process-group signal aimed at the caller; only setsid does).

Run:  python ops/tests/test_gate_preflight_wrapper_survives_kill.py
"""
import os
import shutil
import stat
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _run_gate(write_file=True, executable=True, body="setsid nohup python ops/preflight.py\n"):
    tmp_dir = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(tmp_dir, "ops"))
        if write_file:
            path = os.path.join(tmp_dir, "ops", "run_preflight.sh")
            with open(path, "w", encoding="utf-8") as f:
                f.write(body)
            mode = 0o755 if executable else 0o644
            os.chmod(path, mode)

        real_root = preflight.ROOT
        preflight.ROOT = tmp_dir
        before_fail = len(preflight.FAIL)
        try:
            preflight.gate_preflight_wrapper_survives_kill()
        finally:
            preflight.ROOT = real_root
        return preflight.FAIL[before_fail:]
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_real_wrapper_is_clean():
    real_path = os.path.join(ROOT, "ops", "run_preflight.sh")
    assert os.path.exists(real_path), "ops/run_preflight.sh must exist"
    before_fail = len(preflight.FAIL)
    preflight.gate_preflight_wrapper_survives_kill()
    fails = preflight.FAIL[before_fail:]
    assert not fails, fails
    print("ok  the real ops/run_preflight.sh passes the gate")


def test_missing_wrapper_fails():
    fails = _run_gate(write_file=False)
    assert any(name == "preflight-wrapper" for name, _ in fails), fails
    assert "missing" in fails[0][1]
    print("ok  missing ops/run_preflight.sh: fails, names the gap")


def test_non_executable_wrapper_fails():
    if os.name == "nt":
        print("SKIPPED (NOT VERIFIED) test_non_executable_wrapper_fails: "
              "os.access(X_OK) cannot be made False on this platform")
        return
    fails = _run_gate(executable=False)
    assert any(name == "preflight-wrapper" for name, _ in fails), fails
    assert "not executable" in fails[0][1]
    print("ok  non-executable wrapper: fails, names the gap")


def test_wrapper_without_setsid_fails():
    """The exact regression this gate exists for: a wrapper that still
    looks like a detaching wrapper (nohup, disown, backgrounding) but has
    lost the one mechanism, setsid, that actually survives a killed
    caller (LRN-0021)."""
    fails = _run_gate(body="nohup python ops/preflight.py & disown\n")
    assert any(name == "preflight-wrapper" for name, _ in fails), fails
    assert "setsid" in fails[0][1]
    print("ok  wrapper downgraded to nohup+disown only: fails, names setsid")


def test_wrapper_with_setsid_is_clean():
    fails = _run_gate(body="setsid nohup python ops/preflight.py \"$@\" &\n")
    assert not fails, fails
    print("ok  wrapper using setsid: clean")


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failed += 1
            print("FAIL %s: %s" % (t.__name__, e))
    if failed:
        print("\n%d of %d test(s) failed" % (failed, len(tests)))
        return 1
    print("\n%d of %d test(s) pass" % (len(tests), len(tests)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
