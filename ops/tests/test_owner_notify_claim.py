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
import sys

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


def main():
    test_floor_elapsed()
    test_is_concurrent_race()
    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURE(S): {FAILURES}")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
