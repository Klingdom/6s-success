"""One command from working tree to verified production.

Phil's instruction, 2026-09-03: make committing and pushing work every time, and
make VPS deployment work too.

Both already worked, individually, when driven by hand. What did not work was
the path: sync_push.py stops when the tree is dirty, and the tree is almost
always dirty because ops/dashboard.py rewrites three generated files on every
run. So every push became "commit the churn by hand, then push", and a step a
human has to remember is a step that fails.

This is the whole path in one place:

    stage -> commit -> rebase on origin -> push -> verify on origin -> deploy
    -> verify production actually changed

Every stage is checked against the thing itself rather than an exit code. The
push is confirmed by asking GitHub whether the commit is an ancestor of main.
The deploy is confirmed by reading the live catalogue, because "docker compose
returned zero" and "production changed" are different claims.

    python ops/ship.py -m "message"       commit, push, deploy, verify
    python ops/ship.py -m "..." --no-deploy
    python ops/ship.py --check            report what would happen
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))
import sync_push                                                # noqa: E402

# Outputs of ops/dashboard.py, and only those. On a rebase conflict here, a
# fresh run of dashboard.py is the truth, since both sides are equally wrong.
#
# CHECKIN-LOG.md and ops/state-checkin.json were listed here too until this
# was found live: they are NOT that kind of output. CHECKIN-LOG.md only ever
# APPENDS (ops/checkin.py never rewrites the whole file), so "regenerate" does
# not clear a conflict already sitting in the file body, and state-checkin.json
# carries forward state from the previous run, so silently recomputing it on
# conflict can quietly erase a still-standing measurement. Treating them as
# blindly regenerable meant this code path staged whatever the working tree
# held after a failed rebase, markers included, then committed and pushed it:
# proved directly in an isolated sandbox (ops/tests/test_ship_conflict_safety.py),
# the exact incident sync_push.py's own docstring already describes, now
# reachable through the tool this repository is told to ship through instead.
# A conflict in either file is real information now, same as any other
# non-generated file: it stops the push rather than being resolved for you.
GENERATED = sync_push.GENERATED


def git(*a, check=False):
    p = subprocess.run(["git"] + list(a), cwd=ROOT, capture_output=True,
                       text=True)
    if check and p.returncode != 0:
        raise SystemExit("git %s failed: %s" % (" ".join(a), p.stderr[-300:]))
    return p


def dirty() -> list:
    return [l for l in git("status", "--porcelain").stdout.split("\n")
            if l.strip() and not l.startswith("??")]


def only_generated(changes: list) -> bool:
    return all(any(c[3:].strip().startswith(g) for g in GENERATED)
               for c in changes)


def step(name: str, ok: bool, detail: str = "") -> bool:
    print("  %-28s %s%s" % (name, "ok" if ok else "FAILED",
                            ("  " + detail) if detail else ""))
    return ok


def main() -> int:
    msg = None
    if "-m" in sys.argv:
        msg = sys.argv[sys.argv.index("-m") + 1]
    check_only = "--check" in sys.argv

    changes = dirty()
    if check_only:
        print("  uncommitted changes : %d" % len(changes))
        print("  only generated files: %s" % only_generated(changes)
              if changes else "  tree clean")
        git("fetch", "-q", "origin")
        print("  ahead of origin     : %s"
              % git("rev-list", "--count", "origin/main..HEAD").stdout.strip())
        return 0

    # 1. Commit. Generated churn does not need a message from the caller,
    #    because nobody is deciding anything by writing one.
    if changes:
        if msg is None and not only_generated(changes):
            print("  REFUSING: %d change(s) are not generated files and no -m "
                  "was given. A real change deserves a real message: %s"
                  % (len(changes), [c[3:] for c in changes[:4]]))
            return 1
        git("add", "-A")
        # Stamp AFTER staging, not before. build_id.py hashes git's index, so
        # running it first would describe the previous state and hand deploy.py
        # a stamp for a build nobody is shipping. That is the one way this
        # check fails dangerously: it would match an older build and call a
        # newer one live.
        subprocess.run([sys.executable, os.path.join(ROOT, "ops",
                                                     "build_id.py")],
                       cwd=ROOT, capture_output=True, timeout=600)
        git("add", "site/build-id.txt")
        commit_msg = msg or "Regenerate dashboard and check-in records"
        c = git("commit", "-q", "-m", commit_msg)
        if not step("commit", c.returncode == 0, commit_msg[:40]):
            return 1
    else:
        step("commit", True, "nothing to commit")

    # 2. Push, retrying against the sessions that push every few minutes.
    pushed = False
    for attempt in (1, 2, 3, 4, 5):
        git("fetch", "-q", "origin")
        r = git("rebase", "origin/main")
        if r.returncode != 0:
            conflicted = [l[3:] for l in git("status", "--porcelain").stdout.split("\n")
                          if l[:2] in ("UU", "AA", "DU", "UD")]
            unknown = [c for c in conflicted if c not in GENERATED]
            if unknown:
                git("rebase", "--abort")
                step("push", False, "conflict in real source: %s" % unknown[:3])
                return 1
            subprocess.run([sys.executable, os.path.join(ROOT, "ops",
                                                         "dashboard.py")],
                           cwd=ROOT, capture_output=True, timeout=900)
            for f in GENERATED:
                git("add", f)
            staged = git("diff", "--cached", "--quiet")
            git("-c", "core.editor=true", "rebase",
                "--skip" if staged.returncode == 0 else "--continue")
            # Defense in depth: `git add` marks a path resolved regardless of
            # its content, so a conflict this loop misclassified as safe would
            # otherwise commit real "<<<<<<<" markers with nothing to stop it.
            # This is the exact failure GENERATED above was just narrowed to
            # prevent; check it directly rather than trust the narrowing alone.
            bad = sync_push.markered()
            if bad:
                git("rebase", "--abort")
                step("push", False, "conflict markers survived resolution: %s"
                     % bad[:4])
                return 1
        if git("push", "origin", "main").returncode == 0:
            pushed = True
            break
    if not step("push", pushed, "attempt %d" % attempt):
        return 1

    # 3. Verify against GitHub, not against the push's exit code.
    git("fetch", "-q", "origin")
    here = git("rev-parse", "HEAD").stdout.strip()
    on_remote = git("merge-base", "--is-ancestor", here,
                    "origin/main").returncode == 0
    if not step("verified on origin/main", on_remote, here[:9]):
        return 1

    if "--no-deploy" in sys.argv:
        step("deploy", True, "skipped by --no-deploy")
        return 0

    # 4. Deploy, and let deploy.py decide whether production actually moved.
    d = subprocess.run([sys.executable, os.path.join(ROOT, "ops", "deploy.py")],
                       cwd=ROOT, capture_output=True, text=True, timeout=900)
    tail = [l for l in d.stdout.split("\n") if l.strip()][-1:] or [""]
    return 0 if step("deploy", d.returncode == 0, tail[0].strip()[:60]) else 1


if __name__ == "__main__":
    sys.exit(main())
