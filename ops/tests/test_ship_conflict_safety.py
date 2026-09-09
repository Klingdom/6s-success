#!/usr/bin/env python3
"""
Prove ops/ship.py cannot push a real conflict marker to origin/main, the exact
incident ops/sync_push.py's own docstring describes ("put unresolved conflict
markers into ops/state.json and ops/dashboard.html on 2026-09-01 and failed
CI") reintroduced through the tool this repository is now told to ship
through instead of a plain commit.

Found live, 2026-09-09: ship.py's own GENERATED list, unlike sync_push.py's,
also named CHECKIN-LOG.md and ops/state-checkin.json as "safe to regenerate on
conflict". Neither is that kind of file. ops/checkin.py only ever APPENDS to
CHECKIN-LOG.md, so a fresh run cannot clear a conflict already sitting in the
file body, and it carries forward state from the previous run in
state-checkin.json, so a blind rerun during a conflict can silently erase a
still-standing measurement. ship.py's conflict handler called only
ops/dashboard.py (which never touches either file) and then `git add`ed
everything in GENERATED regardless: git marks a path resolved the moment it is
added, whatever its content, so this staged and committed the literal
"<<<<<<<"/"======="/">>>>>>>" markers left by the failed rebase and pushed
them, while printing "push ok".

Reproduced directly in an isolated sandbox repo (a real bare "origin" and two
clones, so this drives the actual shipped ops/ship.py and ops/sync_push.py,
not a re-description of them) before the fix: the pushed CHECKIN-LOG.md and
ops/state-checkin.json on origin/main both contained live conflict markers.
Fixed by narrowing GENERATED to sync_push.py's own list (the three true
dashboard.py outputs only) and adding a sync_push.markered() scan as defense
in depth before any push. This test drives the real, current ops/ship.py and
ops/sync_push.py end to end against that same scenario, plus the legitimate
case (a conflict only in the true dashboard outputs) to prove the fix did not
also break the thing ship.py exists for.

Run:  python ops/tests/test_ship_conflict_safety.py
"""
from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHIP = os.path.join(ROOT, "ops", "ship.py")
SYNC = os.path.join(ROOT, "ops", "sync_push.py")

MARKERS = ("<<<<<<<", "=======", ">>>>>>>")


def git(cwd, *a, check=True):
    p = subprocess.run(["git"] + list(a), cwd=cwd, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise RuntimeError("git %s (in %s) failed: %s" % (" ".join(a), cwd, p.stderr))
    return p


def write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", newline="").write(content)


def base_files(repo: str) -> None:
    """A minimal sandbox: the real ship.py and sync_push.py, a stub
    dashboard.py that only ever writes the three true dashboard outputs
    (real enough to prove whether ship.py's conflict handler calls it,
    without needing this repository's own heavy build), and starting
    content for every file this test touches."""
    shutil.copy(SHIP, os.path.join(repo, "ops", "ship.py"))
    shutil.copy(SYNC, os.path.join(repo, "ops", "sync_push.py"))
    write(os.path.join(repo, "ops", "dashboard.py"),
          "import io\n"
          "io.open('EXECUTIVE-DASHBOARD-LIVE.md', 'w').write('dashboard\\n')\n"
          "io.open('ops/dashboard.html', 'w').write('<html></html>\\n')\n"
          "io.open('ops/state.json', 'w').write('{}\\n')\n")
    write(os.path.join(repo, "EXECUTIVE-DASHBOARD-LIVE.md"), "dashboard\n")
    write(os.path.join(repo, "ops", "dashboard.html"), "<html></html>\n")
    write(os.path.join(repo, "ops", "state.json"), "{}\n")
    write(os.path.join(repo, "CHECKIN-LOG.md"), "# log\n\n## entry\nSENTINEL-BASE\n")
    write(os.path.join(repo, "ops", "state-checkin.json"),
          json.dumps({"marker": "BASE"}) + "\n")


def init_repo(repo: str) -> None:
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "test")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")


def make_scenario(base: str):
    """repo (local clone with an uncommitted LOCAL-side change) and origin
    (a bare repo already carrying a REMOTE-side commit that touched the same
    lines), both derived from one shared base commit so rebasing genuinely
    conflicts rather than fast-forwarding."""
    repo = os.path.join(base, "repo")
    origin = os.path.join(base, "origin.git")
    os.makedirs(os.path.join(repo, "ops"))
    base_files(repo)
    init_repo(repo)

    git(base, "init", "-q", "--bare", origin)
    git(repo, "remote", "add", "origin", origin)
    git(repo, "push", "-q", "origin", "main", check=False)  # noisy local warning, still lands

    remote_clone = os.path.join(base, "remote_clone")
    git(base, "clone", "-q", origin, remote_clone)
    git(remote_clone, "checkout", "-q", "-b", "main", "origin/main", check=False)
    git(remote_clone, "config", "user.email", "test@example.com")
    git(remote_clone, "config", "user.name", "test")
    write(os.path.join(remote_clone, "CHECKIN-LOG.md"),
          "# log\n\n## entry\nSENTINEL-REMOTE\n")
    write(os.path.join(remote_clone, "ops", "state-checkin.json"),
          json.dumps({"marker": "REMOTE"}) + "\n")
    git(remote_clone, "add", "-A")
    git(remote_clone, "commit", "-q", "-m", "remote change")
    git(remote_clone, "push", "-q", "origin", "main")

    write(os.path.join(repo, "CHECKIN-LOG.md"), "# log\n\n## entry\nSENTINEL-LOCAL\n")
    write(os.path.join(repo, "ops", "state-checkin.json"),
          json.dumps({"marker": "LOCAL"}) + "\n")
    return repo, origin


def run_ship(repo: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "ops/ship.py", "-m", "local change",
                           "--no-deploy"],
                          cwd=repo, capture_output=True, text=True, timeout=120)


def origin_main_text(origin: str, path: str) -> str:
    p = subprocess.run(["git", "--git-dir", origin, "show", "main:%s" % path],
                       capture_output=True, text=True)
    return p.stdout


def case_real_source_conflict_never_pushes() -> str:
    """The bug as found: a conflict in CHECKIN-LOG.md/state-checkin.json must
    never be pushed, marked resolved or not."""
    with tempfile.TemporaryDirectory() as base:
        repo, origin = make_scenario(base)
        before = origin_main_text(origin, "CHECKIN-LOG.md")
        r = run_ship(repo)
        after = origin_main_text(origin, "CHECKIN-LOG.md")
        after_json = origin_main_text(origin, "ops/state-checkin.json")

        if any(m in after for m in MARKERS) or any(m in after_json for m in MARKERS):
            return ("ship.py pushed a live conflict marker to origin/main: "
                    "CHECKIN-LOG.md=%r state-checkin.json=%r"
                    % (after, after_json))
        if after != before:
            return ("origin/main's CHECKIN-LOG.md changed even though ship.py "
                    "should have refused to push at all: before=%r after=%r"
                    % (before, after))
        if r.returncode == 0:
            return ("ship.py exited 0 on an unresolved real-source conflict; "
                    "stdout=%r" % r.stdout)
        if "CHECKIN-LOG.md" not in r.stdout and "state-checkin.json" not in r.stdout:
            return ("ship.py refused correctly but did not name the "
                    "conflicting file(s); stdout=%r" % r.stdout)
        return ""


def case_dashboard_only_conflict_still_ships() -> str:
    """The legitimate case this tool exists for: a conflict confined to the
    three true dashboard.py outputs must still auto-resolve and push."""
    with tempfile.TemporaryDirectory() as base:
        repo = os.path.join(base, "repo")
        origin = os.path.join(base, "origin.git")
        os.makedirs(os.path.join(repo, "ops"))
        base_files(repo)
        init_repo(repo)
        git(base, "init", "-q", "--bare", origin)
        git(repo, "remote", "add", "origin", origin)
        git(repo, "push", "-q", "origin", "main", check=False)

        remote_clone = os.path.join(base, "remote_clone")
        git(base, "clone", "-q", origin, remote_clone)
        git(remote_clone, "checkout", "-q", "-b", "main", "origin/main", check=False)
        git(remote_clone, "config", "user.email", "test@example.com")
        git(remote_clone, "config", "user.name", "test")
        write(os.path.join(remote_clone, "ops", "state.json"), '{"remote": true}\n')
        git(remote_clone, "add", "-A")
        git(remote_clone, "commit", "-q", "-m", "remote dashboard run")
        git(remote_clone, "push", "-q", "origin", "main")

        # A real, non-generated source change, so there is something to ship.
        write(os.path.join(repo, "README.md"), "local edit\n")
        write(os.path.join(repo, "ops", "state.json"), '{"local": true}\n')

        r = run_ship(repo)
        readme = origin_main_text(origin, "README.md")
        if r.returncode != 0:
            return ("a conflict confined to dashboard.py's own outputs should "
                    "still ship; stdout=%r stderr=%r" % (r.stdout, r.stderr))
        if readme.strip() != "local edit":
            return "the real source change never reached origin/main: %r" % readme
        state = origin_main_text(origin, "ops/state.json")
        if any(m in state for m in MARKERS):
            return "a marker survived even the legitimate auto-resolve path: %r" % state
        return ""


def main() -> int:
    cases = [
        ("real-source conflict must never push", case_real_source_conflict_never_pushes),
        ("dashboard-only conflict still ships", case_dashboard_only_conflict_still_ships),
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
