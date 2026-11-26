#!/usr/bin/env python3
"""
Prove ops/owner_notify_claim.py's pure decision logic (floor_elapsed,
is_concurrent_race) actually distinguishes the race it exists to catch from
the cases that must NOT be blocked, by making each one fail before the fix
and pass after.

Found live 2026-11-20 (GitHub issue #42, last comment): two scheduled
cycles read ops/last-owner-notification.json within four minutes of each
other, each independently decided the 48h floor had cleared, and both
called the push tool before either had committed its own new sent_at. The
guard this tests flips the order (claim via commit+push, then notify only
if the push lands); these two functions are the parts of that guard with
no git or network dependency, so they are tested directly.

Run:  python ops/tests/test_owner_notify_claim.py
"""
import datetime as dt
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import owner_notify_claim as onc                                # noqa: E402

FAILURES = []


def check(label, condition):
    if not condition:
        FAILURES.append(label)
    print(("ok  " if condition else "FAIL") + "  " + label)


def test_floor_elapsed():
    now = dt.datetime(2026, 11, 25, 12, 0, 0, tzinfo=dt.timezone.utc)

    # No prior entry at all: nothing to be inside a floor of.
    check("no sent_at => elapsed", onc.floor_elapsed({}, now, 48))

    # Sent 1 hour ago, 48h floor: must NOT be treated as elapsed.
    recent = {"sent_at": "2026-11-25T11:00:00Z"}
    check("1h-old sent_at, 48h floor => not elapsed",
          onc.floor_elapsed(recent, now, 48) is False)

    # Sent exactly 48h ago: elapsed.
    exact = {"sent_at": "2026-11-23T12:00:00Z"}
    check("exactly-48h-old sent_at => elapsed", onc.floor_elapsed(exact, now, 48))

    # Sent 49h ago: elapsed.
    old = {"sent_at": "2026-11-23T11:00:00Z"}
    check("49h-old sent_at => elapsed", onc.floor_elapsed(old, now, 48))

    # Corrupt/unparseable timestamp: must not crash, and must not block
    # forever (treat as elapsed so a broken file cannot wedge the channel).
    corrupt = {"sent_at": "not-a-timestamp"}
    check("corrupt sent_at => elapsed (fails open)", onc.floor_elapsed(corrupt, now, 48))


def test_is_concurrent_race():
    topic = "backlog-exhausted-30-decisions-cheapest-unlocks"
    prior_sent_at = "2026-11-24T09:52:00Z"

    # The exact shape issue #42 named: someone else claimed the SAME topic
    # within the race window, strictly after our prior read. Must be caught.
    raced = {"sent_at": onc.now_iso(), "topic": topic}
    check("same topic, just landed => real race",
          onc.is_concurrent_race(prior_sent_at, raced, topic))

    # A DIFFERENT topic landed around the same time (e.g. a genuinely new,
    # unrelated finding someone else pushed). Must NOT be blocked as a race.
    different_topic = {"sent_at": onc.now_iso(), "topic": "something-else-entirely"}
    check("different topic => not a race",
          onc.is_concurrent_race(prior_sent_at, different_topic, topic) is False)

    # The file on origin is unchanged from what we started with (our own
    # push failed for an unrelated git reason, nobody else claimed). Must
    # NOT be read as a race, since nothing new actually landed.
    unchanged = {"sent_at": prior_sent_at, "topic": topic}
    check("unchanged remote state => not a race",
          onc.is_concurrent_race(prior_sent_at, unchanged, topic) is False)

    # Same topic, but landed long before the race window (a stale read,
    # not a live race). Must NOT be treated as a race.
    long_ago = {"sent_at": "2026-11-20T07:52:49Z", "topic": topic}
    check("same topic but old timestamp, outside window => not a race",
          onc.is_concurrent_race(prior_sent_at, long_ago, topic, window_minutes=30) is False)


def _git(cwd, *args):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError(f"git {args} failed in {cwd}: {r.stderr}")
    return r


def test_lost_race_preserves_unrelated_uncommitted_work():
    """Integration test, real git repos, no mocking of git itself.

    Found cold-reading this file for the first time, 2026-11-26: the
    original lost-race recovery path ran `git reset --hard origin/main`
    unconditionally. That discards EVERY uncommitted change in the
    working tree, not just this script's own file, which is exactly the
    CLAUDE.md section 34 / Git Safety Protocol shape ("never run
    destructive git commands as a shortcut... stash or commit real work
    first"). A concurrent session losing this race is, by definition, a
    sandbox that was busy doing something else at the same time, so the
    working tree it shares with that call is the one most likely to hold
    real unfinished work. This proves the fixed recovery (reset --mixed +
    checkout of only the one owned file) survives exactly that case.
    """
    tmp = tempfile.mkdtemp(prefix="onc_test_")
    real_root, real_state_path, real_run_git = onc.ROOT, onc.STATE_PATH, onc.run_git
    try:
        origin = os.path.join(tmp, "origin.git")
        repo_a = os.path.join(tmp, "a")
        repo_b = os.path.join(tmp, "b")
        state_rel = os.path.join("ops", "last-owner-notification.json")

        subprocess.run(["git", "init", "--bare", "-b", "main", origin],
                        check=True, capture_output=True)
        subprocess.run(["git", "clone", origin, repo_a], check=True, capture_output=True)
        _git(repo_a, "config", "user.email", "a@test")
        _git(repo_a, "config", "user.name", "a")
        _git(repo_a, "checkout", "-b", "main")
        os.makedirs(os.path.join(repo_a, "ops"), exist_ok=True)
        with open(os.path.join(repo_a, state_rel), "w", encoding="utf-8") as f:
            f.write("{}\n")
        tracked_rel = os.path.join("ops", "real_work.py")
        original_tracked_content = "# committed baseline\n"
        with open(os.path.join(repo_a, tracked_rel), "w", encoding="utf-8") as f:
            f.write(original_tracked_content)
        _git(repo_a, "add", state_rel, tracked_rel)
        _git(repo_a, "commit", "-m", "seed")
        _git(repo_a, "push", "origin", "HEAD:main")

        subprocess.run(["git", "clone", origin, repo_b], check=True, capture_output=True)
        _git(repo_b, "config", "user.email", "b@test")
        _git(repo_b, "config", "user.name", "b")
        _git(repo_b, "checkout", "main")

        # Real, unrelated uncommitted work sitting in repo_a's tree, the
        # kind an in-progress cycle would have mid-fix. Must survive.
        # Two shapes, because they are destroyed differently: `git reset
        # --hard` leaves a brand-new UNTRACKED file alone (it only resets
        # tracked content) but silently discards an uncommitted
        # MODIFICATION to an already-tracked file, which is the real risk
        # this test exists to catch.
        os.makedirs(os.path.join(repo_a, "wip"), exist_ok=True)
        unrelated_path = os.path.join(repo_a, "wip", "unrelated.txt")
        marker = "real uncommitted work, must not be destroyed\n"
        with open(unrelated_path, "w", encoding="utf-8") as f:
            f.write(marker)
        tracked_marker = "# real uncommitted edit, must not be discarded\n"
        with open(os.path.join(repo_a, tracked_rel), "w", encoding="utf-8") as f:
            f.write(original_tracked_content + tracked_marker)

        pushed_b = {"done": False}

        def fake_run_git(*args):
            if args and args[0] == "push" and not pushed_b["done"]:
                # The concurrent session (repo_b) wins the race: it lands
                # its own claim on origin before repo_a's own push call
                # (the one about to happen) actually runs.
                pushed_b["done"] = True
                _git(repo_b, "fetch", "origin", "main")
                _git(repo_b, "merge", "--ff-only", "origin/main")
                with open(os.path.join(repo_b, state_rel), "w", encoding="utf-8") as f:
                    f.write('{"sent_at": "%s", "channel": "push", '
                            '"topic": "topic-x", "note": "from b"}\n' % onc.now_iso())
                _git(repo_b, "commit", "-m", "Claim owner notification: topic-x",
                     "--", state_rel)
                _git(repo_b, "push", "origin", "HEAD:main")
            return real_run_git(*args)

        onc.ROOT = repo_a
        onc.STATE_PATH = os.path.join(repo_a, state_rel)
        onc.run_git = fake_run_git
        try:
            rc = onc.cmd_claim("topic-x", "from a", 48)
        finally:
            onc.run_git = real_run_git

        check("lost race returns exit code 2 (LOST_RACE)", rc == 2)
        check("unrelated uncommitted file still exists",
              os.path.exists(unrelated_path))
        check("unrelated uncommitted file's content is untouched",
              os.path.exists(unrelated_path)
              and open(unrelated_path, encoding="utf-8").read() == marker)
        tracked_abs = os.path.join(repo_a, tracked_rel)
        check("uncommitted MODIFICATION to an already-tracked file survives "
              "(the shape plain `git reset --hard` destroys)",
              os.path.exists(tracked_abs)
              and open(tracked_abs, encoding="utf-8").read()
              == original_tracked_content + tracked_marker)
        status = _git(repo_a, "status", "--porcelain", "--untracked-files=all").stdout
        check("the unrelated file is still reported uncommitted (not swept into a commit)",
              "wip/unrelated.txt" in status)
        check("the tracked file's edit is still reported as a local modification",
              "ops/real_work.py" in status)
        check("the state file itself is clean after recovery (no leftover local diff)",
              "last-owner-notification.json" not in status)
        landed = onc.load_state()
        check("local state matches the winner's (b's) claim after recovery",
              landed.get("topic") == "topic-x" and landed.get("note") == "from b")
    finally:
        onc.ROOT, onc.STATE_PATH, onc.run_git = real_root, real_state_path, real_run_git
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    test_floor_elapsed()
    test_is_concurrent_race()
    test_lost_race_preserves_unrelated_uncommitted_work()
    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURE(S): {FAILURES}")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
