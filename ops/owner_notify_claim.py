#!/usr/bin/env python3
"""Claim-before-notify guard for the owner-push channel, so two concurrent
autonomous sessions stop independently deciding the 48-hour repeat floor has
cleared and both pushing the same notification to Phil within minutes of
each other.

Found live 2026-11-20 (GitHub issue #42, last comment): two scheduled
cycles, 07:46:00Z and 07:50:33Z the same morning, each read
ops/last-owner-notification.json, each independently computed that its own
~48h floor had passed, and each called the push tool before either had
written its own new sent_at back to the file. Writing the result afterward,
as every prior cycle has done, cannot prevent this: the human-facing side
effect (a phone notification) already happened by the time git could
serialise the two writes.

This flips the order: CLAIM first (write the new sent_at, commit, push),
and only notify if the claim's push actually lands. git has no atomic
"claim" primitive across independent clones (the same caveat ops/b9_claims.py
already states), so this is not a lock either; it narrows the race from
"two full decision-and-notify cycles" to "two git pushes", and a rejected
push is a hard, visible signal rather than a silent duplicate.

Usage:
    python ops/owner_notify_claim.py --check
    python ops/owner_notify_claim.py --claim --topic "..." --note "..." [--floor-hours 48]

--check is read-only: it reports whether the floor has elapsed against the
committed file, nothing else, and never writes.

--claim performs, in order: git fetch, fast-forward onto origin/main, a
fresh read of the state file, the floor test, and only if the floor has
elapsed: write the new entry, commit, and git push. Exit codes:
    0  floor elapsed and this call's claim was pushed; go ahead and notify
    1  floor has not elaped; do not notify
    2  floor had elapsed on read but the push lost the race to a concurrent
       claim of the same topic; do not notify, someone else just did
    3  push failed for an unrelated reason (merge conflict, no remote, a
       stale local branch); do not notify, the caller should investigate
"""
import argparse
import datetime as dt
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(ROOT, "ops", "last-owner-notification.json")
DEFAULT_FLOOR_HOURS = 48
RACE_WINDOW_MINUTES = 30


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(s: str) -> dt.datetime:
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def load_state() -> dict:
    if not os.path.exists(STATE_PATH):
        return {}
    with io.open(STATE_PATH, encoding="utf-8") as f:
        return json.loads(f.read())


def save_state(state: dict) -> None:
    with io.open(STATE_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(state, indent=1, sort_keys=False))
        f.write("\n")


def floor_elapsed(state: dict, now: dt.datetime, floor_hours: int = DEFAULT_FLOOR_HOURS) -> bool:
    """True if there is no recorded sent_at, or it is older than floor_hours."""
    sent_at = state.get("sent_at")
    if not sent_at:
        return True
    try:
        last = parse_iso(sent_at)
    except (ValueError, TypeError):
        return True
    return (now - last) >= dt.timedelta(hours=floor_hours)


def is_concurrent_race(prior_sent_at: str, new_state: dict, topic: str,
                        window_minutes: int = RACE_WINDOW_MINUTES) -> bool:
    """True if `new_state` (what landed on origin after our push lost) looks
    like the exact race this guard exists for: the same topic, sent within
    `window_minutes` of the moment we tried to claim it, by someone else.
    Distinguishes "another session just notified about the same thing" from
    an unrelated commit that happened to touch main around the same time.
    """
    remote_sent_at = new_state.get("sent_at")
    if not remote_sent_at or remote_sent_at == prior_sent_at:
        return False
    if new_state.get("topic") != topic:
        return False
    try:
        remote_time = parse_iso(remote_sent_at)
        mine_time = dt.datetime.now(dt.timezone.utc)
    except (ValueError, TypeError):
        return False
    return abs((mine_time - remote_time).total_seconds()) <= window_minutes * 60


def run_git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def cmd_check(floor_hours: int) -> int:
    state = load_state()
    now = dt.datetime.now(dt.timezone.utc)
    elapsed = floor_elapsed(state, now, floor_hours)
    sent_at = state.get("sent_at", "(never)")
    print(f"sent_at={sent_at} floor_hours={floor_hours} elapsed={elapsed}")
    return 0


def cmd_claim(topic: str, note: str, floor_hours: int) -> int:
    run_git("fetch", "origin", "main")
    ff = run_git("merge", "--ff-only", "origin/main")
    if ff.returncode != 0:
        print(f"CANNOT_SYNC: {ff.stderr.strip()}", file=sys.stderr)
        return 3

    state = load_state()
    prior_sent_at = state.get("sent_at")
    now = dt.datetime.now(dt.timezone.utc)
    if not floor_elapsed(state, now, floor_hours):
        print(f"NOT_DUE: last sent_at={prior_sent_at}, floor_hours={floor_hours} not elapsed")
        return 1

    new_state = {
        "sent_at": now_iso(),
        "channel": "push",
        "topic": topic,
        "note": note,
    }
    save_state(new_state)
    # Commit scoped to this one file via pathspec, not a bare `git commit`:
    # the caller may be mid-cycle with other real work already `git add`-ed
    # (e.g. a fix this same session is about to ship separately), and a
    # bare commit would sweep that in too, mislabelled under this claim's
    # own message.
    commit = run_git("commit", "-m", f"Claim owner notification: {topic}",
                      "--", "ops/last-owner-notification.json")
    if commit.returncode != 0:
        print(f"COMMIT_FAILED: {commit.stderr.strip()}", file=sys.stderr)
        return 3

    push = run_git("push", "origin", "HEAD:main")
    if push.returncode == 0:
        print(f"CLAIMED: {topic} at {new_state['sent_at']}")
        return 0

    # Lost the push race. Recover WITHOUT `git reset --hard`: this sandbox
    # may hold other real, unrelated uncommitted work in the same working
    # tree (another in-progress fix this same cycle has not shipped yet),
    # and a hard reset to origin/main would silently destroy all of it
    # (CLAUDE.md section 34 / Git Safety Protocol: never discard
    # uncommitted work as a shortcut). `reset --mixed` only rewinds HEAD
    # and the index past our own losing commit, touching no working-tree
    # file; `checkout --` then restores just the one file this script
    # owns from that now-rewound index, so only our own losing claim is
    # undone and nothing else in the tree is touched.
    run_git("fetch", "origin", "main")
    run_git("reset", "--mixed", "HEAD~1")
    run_git("checkout", "--", "ops/last-owner-notification.json")
    resync = run_git("merge", "--ff-only", "origin/main")
    if resync.returncode != 0:
        print(f"CANNOT_RESYNC_AFTER_LOST_RACE: {resync.stderr.strip()}", file=sys.stderr)
        return 3
    landed = load_state()
    if is_concurrent_race(prior_sent_at, landed, topic):
        print(f"LOST_RACE: {landed.get('topic')} already claimed at {landed.get('sent_at')}")
        return 2
    print(f"PUSH_FAILED: {push.stderr.strip()}", file=sys.stderr)
    return 3


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true")
    p.add_argument("--claim", action="store_true")
    p.add_argument("--topic", default="")
    p.add_argument("--note", default="")
    p.add_argument("--floor-hours", type=int, default=DEFAULT_FLOOR_HOURS)
    args = p.parse_args()

    if args.claim:
        if not args.topic:
            print("--claim requires --topic", file=sys.stderr)
            return 2
        return cmd_claim(args.topic, args.note, args.floor_hours)
    return cmd_check(args.floor_hours)


if __name__ == "__main__":
    sys.exit(main())
