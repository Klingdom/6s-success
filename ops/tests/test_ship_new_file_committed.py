#!/usr/bin/env python3
"""
Prove ops/ship.py actually ships a commit whose ONLY change is a brand-new,
untracked file (no tracked file modified alongside it).

Found live, 2026-09-21, cold-reading ops/ship.py in the standing low-mention
fallback. dirty() excluded every "??" (untracked) line from git status before
deciding whether there was anything to commit:

    return [l for l in git("status", "--porcelain").stdout.split("\n")
            if l.strip() and not l.startswith("??")]

That exclusion was copied from ops/sync_push.py, where it is correct: that
tool only ever decides whether to REFUSE a rebase, so a stray untracked
scratch file (audit_visual.py's own probe pages and similar) should not block
it. ops/ship.py reuses the same helper for a different decision: whether
there is anything to STAGE and commit. The scratch files the exclusion was
meant to shrug off are gitignored (site/**/_*.html, see .gitignore), so they
never appear in git status at all; the exclusion protected against nothing
there, while quietly breaking the case where a commit's only content is one
or more new files. When `changes` came back empty (because every real change
was a "??" line), main() took the "nothing to commit" branch, never reached
`git add -A`, and proceeded straight to push/verify/deploy, all of which
report "ok" against an unchanged HEAD, exactly the "green check, nothing
actually shipped" shape ops/verify_deploy.py's own CRITICAL_PAGES fix (same
day, this backlog) closed for a different surface.

Reproduced directly in an isolated sandbox repo (a real bare origin and a
clone, driving the actual shipped ops/ship.py, not a re-description of it)
before the fix: a brand-new file committed nowhere, reported "commit: ok
(nothing to commit)" and "push: ok", while origin/main never gained the file.

Run:  python ops/tests/test_ship_new_file_committed.py
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
    """See test_ship_conflict_safety.py's own no_gc: stops a detached
    `git gc --auto` child from racing this test's tempdir cleanup."""
    git(repo, "config", "gc.auto", "0")


def make_repo(base: str):
    repo = os.path.join(base, "repo")
    origin = os.path.join(base, "origin.git")
    os.makedirs(os.path.join(repo, "ops"))
    shutil.copy(SHIP, os.path.join(repo, "ops", "ship.py"))
    shutil.copy(SYNC, os.path.join(repo, "ops", "sync_push.py"))
    # A minimal stand-in for the three real dashboard.py outputs, so
    # build_id.py's own subprocess call inside ship.py has nothing to trip
    # over; not exercised by this scenario (no rebase conflict), but present
    # so the sandbox matches the real repo's file shape.
    with open(os.path.join(repo, "EXECUTIVE-DASHBOARD-LIVE.md"), "w") as f:
        f.write("dashboard\n")
    with open(os.path.join(repo, "README.md"), "w") as f:
        f.write("base\n")
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


def origin_files(origin: str) -> list:
    p = subprocess.run(["git", "--git-dir", origin, "ls-tree", "-r",
                        "--name-only", "main"], capture_output=True, text=True)
    return [l for l in p.stdout.split("\n") if l.strip()]


def run_ship(repo: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "ops/ship.py", "-m", "add a new file",
                           "--no-deploy"],
                          cwd=repo, capture_output=True, text=True, timeout=120)


def case_new_file_only_still_ships() -> str:
    """The bug as found: a working tree whose only change is one brand-new,
    untracked file must still be staged, committed and pushed."""
    with tempfile.TemporaryDirectory() as base:
        repo, origin = make_repo(base)
        with open(os.path.join(repo, "brand_new_page.md"), "w") as f:
            f.write("this file did not exist before this commit\n")

        r = run_ship(repo)
        files = origin_files(origin)

        if r.returncode != 0:
            return ("ship.py should ship a new-file-only change; exit=%d "
                    "stdout=%r stderr=%r" % (r.returncode, r.stdout, r.stderr))
        if "brand_new_page.md" not in files:
            return ("the new file never reached origin/main even though "
                    "ship.py reported success; origin has: %r; stdout=%r"
                    % (files, r.stdout))
        if "nothing to commit" in r.stdout:
            return ("ship.py claimed nothing to commit while a real new "
                    "file sat in the working tree; stdout=%r" % r.stdout)
        return ""


def case_new_file_alongside_modification_still_ships() -> str:
    """Sanity check the ordinary path (a modified tracked file plus a new
    file together) was never broken; only the new-file-alone case was."""
    with tempfile.TemporaryDirectory() as base:
        repo, origin = make_repo(base)
        with open(os.path.join(repo, "README.md"), "w") as f:
            f.write("changed\n")
        with open(os.path.join(repo, "brand_new_page.md"), "w") as f:
            f.write("new alongside a real edit\n")

        r = run_ship(repo)
        files = origin_files(origin)
        if r.returncode != 0:
            return "the ordinary mixed case should ship; stdout=%r" % r.stdout
        if "brand_new_page.md" not in files:
            return "the new file was dropped even in the mixed case: %r" % files
        return ""


def main() -> int:
    cases = [
        ("new file alone still ships", case_new_file_only_still_ships),
        ("new file plus a real edit still ships",
         case_new_file_alongside_modification_still_ships),
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
