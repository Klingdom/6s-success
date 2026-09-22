#!/usr/bin/env python3
"""
Prove `ops/ship.py --help` (and `-h`) only prints usage and never touches git.

Found live, 2026-09-22, this operator: every flag ops/ship.py recognizes is
read positively (its presence is checked, never its absence from a known
set), so an unrecognized flag falls straight through to the default
commit/push/deploy path. Running `python ops/ship.py --help`, expecting
usage text, instead silently committed the dirty tree, pushed it to
origin/main and attempted a production deploy (which happened to fail here
only because this sandbox has no deploy key at /root/.ssh/6s_deploy; in an
environment that does, `--help` would have deployed).

Reproduced directly in an isolated sandbox repo (a real bare origin and a
clone, driving the actual shipped ops/ship.py) before the fix: `--help` on a
dirty tree left origin/main with a new commit and the working tree clean.

Run:  python ops/tests/test_ship_help_flag.py
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHIP = os.path.join(ROOT, "ops", "ship.py")
SYNC = os.path.join(ROOT, "ops", "sync_push.py")


def git(cwd, *a, check=True):
    p = subprocess.run(["git"] + list(a), cwd=cwd, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise RuntimeError("git %s (in %s) failed: %s" % (" ".join(a), cwd, p.stderr))
    return p


def no_gc(repo: str) -> None:
    git(repo, "config", "gc.auto", "0")


def make_repo(base: str):
    repo = os.path.join(base, "repo")
    origin = os.path.join(base, "origin.git")
    os.makedirs(os.path.join(repo, "ops"))
    shutil.copy(SHIP, os.path.join(repo, "ops", "ship.py"))
    shutil.copy(SYNC, os.path.join(repo, "ops", "sync_push.py"))
    with open(os.path.join(repo, "EXECUTIVE-DASHBOARD-LIVE.md"), "w") as f:
        f.write("dashboard\n")
    with open(os.path.join(repo, "README.md"), "w") as f:
        f.write("base\n")
    # Without this, running ops/ship.py here leaves an untracked
    # ops/__pycache__/ behind that the real repo's own .gitignore already
    # excludes, which would wrongly trip the "real change, needs -m" refusal
    # below instead of reproducing the actual only-generated-files shape.
    with open(os.path.join(repo, ".gitignore"), "w") as f:
        f.write("__pycache__/\n")
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "test")
    no_gc(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")

    git(base, "init", "-q", "--bare", origin)
    no_gc(origin)
    git(repo, "remote", "add", "origin", origin)
    git(repo, "push", "-q", "origin", "main")
    return repo, origin


def origin_head(origin: str) -> str:
    p = subprocess.run(["git", "--git-dir", origin, "rev-parse", "main"],
                       capture_output=True, text=True)
    return p.stdout.strip()


def case_help_does_not_ship() -> str:
    """The exact shape found live: only a GENERATED file (the dashboard
    ops/preflight.py itself just rewrote) is dirty, so ship.py's default
    path needs no -m and would silently commit with a stock message."""
    with tempfile.TemporaryDirectory() as base:
        repo, origin = make_repo(base)
        before = origin_head(origin)
        with open(os.path.join(repo, "EXECUTIVE-DASHBOARD-LIVE.md"), "w") as f:
            f.write("dashboard, regenerated\n")

        r = subprocess.run([sys.executable, "ops/ship.py", "--help"],
                           cwd=repo, capture_output=True, text=True, timeout=60)

        after = origin_head(origin)
        dirty_now = git(repo, "status", "--porcelain").stdout.strip()

        if after != before:
            return ("--help pushed a commit to origin/main: %s -> %s" % (before, after))
        if not dirty_now:
            return "--help committed the working tree's own real change locally"
        if r.returncode != 0:
            return "--help should exit 0; exit=%d stderr=%r" % (r.returncode, r.stderr)
        if "One command from working tree to verified production" not in r.stdout:
            return "--help printed no recognizable usage text: %r" % r.stdout
        return ""


def case_h_shorthand_does_not_ship() -> str:
    with tempfile.TemporaryDirectory() as base:
        repo, origin = make_repo(base)
        before = origin_head(origin)
        with open(os.path.join(repo, "EXECUTIVE-DASHBOARD-LIVE.md"), "w") as f:
            f.write("dashboard, regenerated again\n")

        r = subprocess.run([sys.executable, "ops/ship.py", "-h"],
                           cwd=repo, capture_output=True, text=True, timeout=60)
        after = origin_head(origin)

        if after != before:
            return "-h pushed a commit to origin/main: %s -> %s" % (before, after)
        if r.returncode != 0:
            return "-h should exit 0; exit=%d stderr=%r" % (r.returncode, r.stderr)
        return ""


def main() -> int:
    cases = [
        ("--help prints usage and never ships", case_help_does_not_ship),
        ("-h prints usage and never ships", case_h_shorthand_does_not_ship),
    ]
    fails = []
    for name, fn in cases:
        msg = fn()
        if msg:
            fails.append("%s: %s" % (name, msg))

    if fails:
        print("FAIL: %d of %d cases" % (len(fails), len(cases)))
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: %d of %d cases" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
