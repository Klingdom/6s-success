#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_kitchen_deck_current() catches
ops/cardtext/kitchen-deck.json going stale against
ops/cardtext/build_kitchen_deck.py, and leaves a clean checkout alone.

Found 2026-09-13 widening gate_every_generator_has_a_protection_plan's own
glob: it had never seen this generator, one directory deeper than its old
ops/build_*.py-only reach, so nothing regenerated and diffed this file
before this gate. gate_diagnosis_authoring only cross-checks kitchen-deck.json
against content.json's Kitchen diagnosis text, which proves the two agree
with each other, not that kitchen-deck.json is what the generator itself
would produce.

Uses a detached git worktree sharing the real repository's object database,
the same approach test_generator_ownership.py uses: the generator needs the
real content/manual/source/content.json to run at all, so a small fixture
in a bare temp directory cannot stand in for it the way the KDP cover test's
tiny fixture script can.

Run:  python ops/tests/test_gate_kitchen_deck_current.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def git(*args, cwd=ROOT, check=True):
    r = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True,
                       text=True, timeout=300)
    if check and r.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), r.stderr[:300]))
    return r.stdout


def _run_gate(wt):
    old_root = preflight.ROOT
    preflight.ROOT = wt
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_kitchen_deck_current()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


def main() -> int:
    if os.environ.get("SIXS_UNDER_PREFLIGHT"):
        print("  skipped: preflight is the caller, exercising this gate here "
              "would regenerate kitchen-deck.json mid-run. Run this test "
              "directly to exercise the gate.")
        return 0

    if not shutil.which("git"):
        print("  no git here, cannot exercise the gate. NOT VERIFIED.")
        return 0

    tmp = tempfile.mkdtemp(prefix="6s-kdeck-")
    wt = os.path.join(tmp, "wt")
    fails = []
    try:
        try:
            git("worktree", "add", "--detach", wt, "HEAD")
        except RuntimeError as e:
            print("  could not create a worktree (%s). NOT VERIFIED." % e)
            return 0

        kdeck_path = os.path.join(wt, "ops", "cardtext", "kitchen-deck.json")
        if not os.path.exists(kdeck_path):
            print("  ops/cardtext/kitchen-deck.json not in this checkout. "
                 "NOT VERIFIED.")
            return 0

        # 1. The real, current shape: the committed file really was produced
        #    by the real generator from the real content.json. Clean.
        r, w = _run_gate(wt)
        if r:
            fails.append("a genuinely current kitchen-deck.json was wrongly "
                         "failed: %r" % (r,))
        status = git("status", "--porcelain", cwd=wt)
        if status.strip():
            fails.append("the gate left the worktree dirty on a clean run: %r"
                         % (status,))

        # 2. The real regression shape: a hand edit to kitchen-deck.json that
        #    the generator itself would never produce.
        original = open(kdeck_path, encoding="utf-8").read()
        needle = '"count": 72'
        if needle not in original:
            print("  fixture assumption (%r in kitchen-deck.json) no longer "
                 "holds. NOT VERIFIED." % needle)
            return 0
        mutated = original.replace(needle, '"count": 73', 1)
        with open(kdeck_path, "w", encoding="utf-8") as fh:
            fh.write(mutated)

        r, w = _run_gate(wt)
        if not r or "kitchen-deck.json" not in r[0][1]:
            fails.append("a real hand edit to kitchen-deck.json was not "
                         "caught by name: %r" % (r,))

        # 3. The gate must restore the file either way, win or lose, so a
        #    failed run does not leave the working tree looking like the
        #    fix already happened.
        after = open(kdeck_path, encoding="utf-8").read()
        if after != mutated:
            fails.append("the gate did not restore the file it diffed "
                         "against back to the mutated on-disk state")

        # 4. Put the real file back and confirm clean again.
        with open(kdeck_path, "w", encoding="utf-8") as fh:
            fh.write(original)
        r, w = _run_gate(wt)
        if r:
            fails.append("gate not clean after restoring the real file: %r"
                         % (r,))
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", wt],
                       cwd=ROOT, capture_output=True, text=True)
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_kitchen_deck_current, 4/4 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
