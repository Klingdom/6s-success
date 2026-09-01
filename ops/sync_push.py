"""Push to main safely, against sessions that push constantly.

Cloud routines push to this repository every few minutes, so a plain push loses
the race often. The obvious fix, a retry loop that resolves conflicts with
`git checkout --theirs` and `git add -A`, is what put unresolved conflict
markers into ops/state.json and ops/dashboard.html on 2026-09-01 and failed CI.
`--theirs` on a file git has already written markers into stages the markers.

So this does three things a naive loop does not:

1. Generated files are REGENERATED on conflict, never picked from a side. They
   are outputs, so both sides are equally wrong and the truth is a fresh run.
2. Any other conflict stops the push and says so. A conflict in real source is
   a decision, not something to automate.
3. It refuses to push anything containing a conflict marker, checked on the
   actual staged content rather than trusted from the resolution step.

    python ops/sync_push.py            rebase, verify, push
    python ops/sync_push.py --check    report only, push nothing
"""
from __future__ import annotations

import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Outputs of ops/dashboard.py. Regenerate; never merge.
GENERATED = ["EXECUTIVE-DASHBOARD-LIVE.md", "ops/dashboard.html", "ops/state.json"]

MARKER = re.compile(r"^(<{7} |={7}$|>{7} )", re.M)


def git(*a, check=False):
    p = subprocess.run(["git"] + list(a), cwd=ROOT, capture_output=True,
                       text=True)
    if check and p.returncode != 0:
        raise SystemExit("git %s failed: %s" % (" ".join(a), p.stderr[-300:]))
    return p


def markered() -> list:
    """Tracked files that currently contain a conflict marker."""
    out = []
    for f in git("ls-files").stdout.split("\n"):
        f = f.strip()
        if not f:
            continue
        p = os.path.join(ROOT, f)
        if not os.path.isfile(p) or os.path.getsize(p) > 4_000_000:
            continue
        try:
            s = io.open(p, encoding="utf-8", errors="strict").read()
        except Exception:                                       # noqa: BLE001
            continue
        if MARKER.search(s):
            out.append(f)
    return out


def regenerate():
    subprocess.run([sys.executable, os.path.join(ROOT, "ops", "dashboard.py")],
                   cwd=ROOT, capture_output=True, text=True, timeout=900)


def attempt() -> str:
    """One rebase-and-push cycle. Returns 'pushed', 'retry' or an error string."""
    git("fetch", "-q", "origin")
    # A dirty tree stops a rebase before it starts. Committing or stashing
    # is the caller's decision, so say so rather than guessing.
    dirty = [l for l in git("status", "--porcelain").stdout.split(chr(10))
             if l.strip() and not l.startswith("??")]
    if dirty:
        return ("STOP: %d uncommitted change(s), so a rebase cannot start. "
                "Commit or stash first: %s"
                % (len(dirty), [d[3:] for d in dirty[:4]]))

    r = git("rebase", "origin/main")
    if r.returncode != 0:
        # A non-zero rebase is not necessarily a conflict. Only treat it as
        # one when git actually left a rebase in progress, or the recovery
        # path runs "rebase --continue" with nothing to continue and reports
        # a confusing failure for a push that was otherwise fine.
        in_progress = (
            os.path.isdir(os.path.join(ROOT, ".git", "rebase-merge"))
            or os.path.isdir(os.path.join(ROOT, ".git", "rebase-apply")))
        if not in_progress:
            return "STOP: rebase failed without conflicts: %s" % (
                (r.stderr or r.stdout)[-200:].strip())
        conflicted = [l[3:] for l in git("status", "--porcelain").stdout.split("\n")
                      if l[:2] in ("UU", "AA", "DU", "UD")]
        unknown = [c for c in conflicted if c not in GENERATED]
        if unknown:
            git("rebase", "--abort")
            return ("STOP: conflict in files that are not generated: %s. "
                    "That is a decision, not something to automate." % unknown[:4])
        # Only generated files. Regenerate rather than choose a side.
        regenerate()
        for f in GENERATED:
            git("add", f)
        c = git("-c", "core.editor=true", "rebase", "--continue")
        if c.returncode != 0:
            git("rebase", "--abort")
            return "STOP: rebase could not continue: %s" % c.stderr[-200:]

    bad = markered()
    if bad:
        return "STOP: conflict markers present after rebase: %s" % bad[:4]

    p = git("push", "origin", "main")
    return "pushed" if p.returncode == 0 else "retry"


def main() -> int:
    if "--check" in sys.argv:
        bad = markered()
        print("  conflict markers in tracked files: %d %s" % (len(bad), bad[:4]))
        git("fetch", "-q", "origin")
        ahead = git("rev-list", "--count", "origin/main..HEAD").stdout.strip()
        behind = git("rev-list", "--count", "HEAD..origin/main").stdout.strip()
        print("  ahead of origin/main by %s, behind by %s" % (ahead, behind))
        return 1 if bad else 0

    head_before = git("rev-parse", "HEAD").stdout.strip()
    for i in (1, 2, 3, 4, 5):
        r = attempt()
        if r == "pushed":
            git("fetch", "-q", "origin")
            here = git("rev-parse", "HEAD").stdout.strip()
            anc = git("merge-base", "--is-ancestor", here, "origin/main")
            # Verify against the remote rather than trusting the push's exit
            # code, which is the whole lesson of this repository.
            print("  pushed on attempt %d, and %s is on origin/main: %s"
                  % (i, here[:9], anc.returncode == 0))
            return 0 if anc.returncode == 0 else 1
        if r.startswith("STOP"):
            print("  " + r)
            return 1
        print("  attempt %d: remote moved, retrying" % i)
    print("  gave up after 5 attempts; the remote is moving faster than this "
          "can rebase. HEAD is still %s" % head_before[:9])
    return 1


if __name__ == "__main__":
    sys.exit(main())
