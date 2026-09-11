#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_hooks_enabled() actually catches a hook that
git will silently skip.

Found 2026-09-11, this operator: the gate already checked .githooks/pre-commit
for its executable bit, but a fresh .githooks/pre-push (added the same day, to
refuse pushing an unresolved merge conflict after one reached main) was
committed as mode 100644 next to pre-commit's correct 100755. Git does not
error on a non-executable hooksPath hook; it prints one warning the first time
and then silently never runs it, which is exactly the "looks clean, verified
nothing" shape this gate exists to catch, now on its own sibling file. A fresh
clone of this repository (this one, before the fix) had the identical
push-time protection the file's own commit message called "the control", and
it was inert.

This test proves the widened gate fires on: hooksPath unset, pre-commit not
executable, pre-push not executable, and both not executable; and stays quiet
once every present hook is executable and hooksPath is set.

Run:  python ops/tests/test_gate_hooks_enabled.py
"""
import io
import os
import shutil
import stat
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _git(*args, cwd):
    subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True,
                    text=True, timeout=60)


def _write_hook(path, executable):
    io.open(path, "w", encoding="utf-8").write("#!/bin/sh\nexit 0\n")
    mode = 0o755 if executable else 0o644
    os.chmod(path, mode)


def _run_gate(hooks, hooks_path_set=True):
    """hooks: {"pre-commit": True/False/None, "pre-push": True/False/None}.

    True/False = present with that executable bit; None = file absent.
    """
    tmp_dir = tempfile.mkdtemp()
    try:
        _git("init", "-q", cwd=tmp_dir)
        if hooks_path_set:
            _git("config", "core.hooksPath", ".githooks", cwd=tmp_dir)
        hooks_dir = os.path.join(tmp_dir, ".githooks")
        os.makedirs(hooks_dir)
        for name, state in hooks.items():
            if state is None:
                continue
            _write_hook(os.path.join(hooks_dir, name), executable=state)

        real_root = preflight.ROOT
        preflight.ROOT = tmp_dir
        before_fail, before_warn = len(preflight.FAIL), len(preflight.WARN)
        try:
            preflight.gate_hooks_enabled()
        finally:
            preflight.ROOT = real_root
        return preflight.FAIL[before_fail:], preflight.WARN[before_warn:]
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_both_executable_and_path_set_is_clean():
    fails, warns = _run_gate({"pre-commit": True, "pre-push": True})
    assert not fails, fails
    assert not warns, warns
    print("ok  both hooks executable, hooksPath set: clean")


def test_hooks_path_unset_warns():
    fails, warns = _run_gate({"pre-commit": True, "pre-push": True},
                              hooks_path_set=False)
    assert not fails, fails
    assert any(name == "hooks-enabled" for name, _ in warns), warns
    print("ok  core.hooksPath unset: warns")


def test_pre_commit_not_executable_warns_by_name():
    fails, warns = _run_gate({"pre-commit": False, "pre-push": True})
    assert not fails, fails
    msgs = [msg for name, msg in warns if name == "hooks-enabled"]
    assert msgs, warns
    assert "pre-commit" in msgs[0], msgs
    assert "pre-push" not in msgs[0], msgs
    print("ok  pre-commit alone not executable: warns naming pre-commit only")


def test_pre_push_not_executable_warns_by_name():
    """The exact regression this test exists for: pre-push shipped mode
    100644 while pre-commit was already correct at 100755."""
    fails, warns = _run_gate({"pre-commit": True, "pre-push": False})
    assert not fails, fails
    msgs = [msg for name, msg in warns if name == "hooks-enabled"]
    assert msgs, warns
    assert "pre-push" in msgs[0], msgs
    assert "pre-commit" not in msgs[0], msgs
    print("ok  pre-push alone not executable: warns naming pre-push only "
          "(this is the real 2026-09-11 defect)")


def test_both_not_executable_warns_naming_both():
    fails, warns = _run_gate({"pre-commit": False, "pre-push": False})
    assert not fails, fails
    msgs = [msg for name, msg in warns if name == "hooks-enabled"]
    assert msgs, warns
    assert "pre-commit" in msgs[0] and "pre-push" in msgs[0], msgs
    print("ok  both hooks not executable: warns naming both")


def test_only_pre_commit_present_and_executable_is_clean():
    """Old shape (before pre-push existed) must keep working."""
    fails, warns = _run_gate({"pre-commit": True, "pre-push": None})
    assert not fails, fails
    assert not warns, warns
    print("ok  only pre-commit present and executable: clean, as before "
          "pre-push existed")


def test_no_hooks_directory_is_a_noop():
    tmp_dir = tempfile.mkdtemp()
    try:
        _git("init", "-q", cwd=tmp_dir)
        real_root = preflight.ROOT
        preflight.ROOT = tmp_dir
        before_fail, before_warn = len(preflight.FAIL), len(preflight.WARN)
        try:
            preflight.gate_hooks_enabled()
        finally:
            preflight.ROOT = real_root
        assert not preflight.FAIL[before_fail:]
        assert not preflight.WARN[before_warn:]
        print("ok  no .githooks directory at all: silent no-op")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


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
