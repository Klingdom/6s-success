#!/usr/bin/env python3
"""Lightweight room-claim ledger for B9 (the ongoing "build a room deck for
every room" work), so two concurrent autonomous sessions stop independently
building the same room and colliding at push time.

Found live 2026-09-29, three times inside one day (Pantry, then Hall Closet,
then a second Hall Closet/Dining Room collision inside one push): sessions
each fetch origin, see the same set of undiagnosed rooms, and pick the same
"tied smallest" one, because nothing records that a room is already being
worked. Every collision so far has been resolved correctly (the losing
session takes the winner's superset version rather than force-pushing), but
each reconciliation costs a full preflight re-run and, several times, a real
regression fix on top of it. The repository's own retrospective named this
"process, not a missing check, and outside a single preflight function's
reach" (`ops/NIGHTLY-LOG.md`, 2026-09-29 retrospective entry).

This is not a lock: git has no atomic "claim" primitive across independent
clones, and two sessions can still race to claim the same room in the same
few seconds. What it gives up front is nothing (today, a session commits
30-90 minutes of full room-deck work before anything reveals the collision);
what it gives instead is a fast, cheap signal: claim BEFORE building, in a
small standalone commit, so the ordinary case (a session fetches, sees an
active claim, picks a different room) is decided in seconds instead of after
a full build.

Usage:
    python ops/b9_claims.py --status
    python ops/b9_claims.py --next
    python ops/b9_claims.py --claim "Guest Bedroom" --note "scheduled operator cycle"
    python ops/b9_claims.py --release "Guest Bedroom"

--claim and --release only rewrite ops/b9-claims.json; the caller is
responsible for committing and pushing it (ideally as its own small commit,
before starting the actual build, so the claim reaches origin fast).
"""
import argparse
import datetime as dt
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAIMS_PATH = os.path.join(ROOT, "ops", "b9-claims.json")
CONTENT_PATH = os.path.join(ROOT, "content", "manual", "source", "content.json")

STALE_HOURS = 3


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_claims() -> dict:
    if not os.path.exists(CLAIMS_PATH):
        return {"claims": []}
    with io.open(CLAIMS_PATH, encoding="utf-8") as f:
        return json.loads(f.read())


def save_claims(data: dict) -> None:
    with io.open(CLAIMS_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, indent=2, sort_keys=False))
        f.write("\n")


def room_diagnosis_status() -> dict:
    """{room name: True if every zone in it already carries a diagnosis}."""
    with io.open(CONTENT_PATH, encoding="utf-8") as f:
        data = json.loads(f.read())
    out = {}
    for r in data.get("rooms", []):
        zones = r.get("zones", [])
        diagnosed = sum(1 for z in zones if isinstance(z, dict) and z.get("diagnosis"))
        out[r.get("room")] = (diagnosed == len(zones) and len(zones) > 0, len(zones))
    return out


def is_stale(claimed_at: str, now: str, hours: int = STALE_HOURS) -> bool:
    try:
        t = dt.datetime.strptime(claimed_at, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=dt.timezone.utc)
        n = dt.datetime.strptime(now, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=dt.timezone.utc)
    except (ValueError, TypeError):
        return False
    return (n - t) >= dt.timedelta(hours=hours)


def active_claims(claims: list, now: str) -> dict:
    """{room: claim} for every claim that is in_progress and not stale."""
    out = {}
    for c in claims:
        if c.get("status") != "in_progress":
            continue
        if is_stale(c.get("claimed_at", ""), now):
            continue
        out[c.get("room")] = c
    return out


def next_room(claims: list, diagnosis: dict, now: str) -> str:
    """The next undiagnosed, unclaimed room, smallest zone count first."""
    active = active_claims(claims, now)
    candidates = [
        (n, count) for n, (done, count) in diagnosis.items()
        if not done and n not in active
    ]
    candidates.sort(key=lambda t: (t[1], t[0]))
    return candidates[0][0] if candidates else ""


def cmd_status(args) -> int:
    data = load_claims()
    diagnosis = room_diagnosis_status()
    now = now_iso()
    active = active_claims(data["claims"], now)
    print("Undiagnosed rooms, smallest first:")
    remaining = sorted(
        ((n, c) for n, (done, c) in diagnosis.items() if not done),
        key=lambda t: (t[1], t[0]))
    for name, count in remaining:
        tag = ""
        if name in active:
            tag = "  CLAIMED (%s, %s)" % (
                active[name].get("claimed_at", "?"), active[name].get("note", ""))
        print("  %-20s %d zones%s" % (name, count, tag))
    return 0


def cmd_next(args) -> int:
    data = load_claims()
    diagnosis = room_diagnosis_status()
    room = next_room(data["claims"], diagnosis, now_iso())
    if room:
        print(room)
        return 0
    print("no unclaimed, undiagnosed room remains", file=sys.stderr)
    return 1


def cmd_claim(args) -> int:
    data = load_claims()
    diagnosis = room_diagnosis_status()
    if args.claim not in diagnosis:
        print("not a real room name (check content.json): %r" % args.claim,
              file=sys.stderr)
        return 1
    now = now_iso()
    active = active_claims(data["claims"], now)
    if args.claim in active and active[args.claim].get("note") != args.note:
        print("already actively claimed: %r" % active[args.claim], file=sys.stderr)
        return 1
    data["claims"].append({
        "room": args.claim,
        "status": "in_progress",
        "claimed_at": now,
        "note": args.note or "",
    })
    save_claims(data)
    print("claimed %r at %s" % (args.claim, now))
    return 0


def cmd_release(args) -> int:
    data = load_claims()
    changed = False
    for c in data["claims"]:
        if c.get("room") == args.release and c.get("status") == "in_progress":
            c["status"] = "done"
            c["released_at"] = now_iso()
            changed = True
    if changed:
        save_claims(data)
        print("released %r" % args.release)
        return 0
    print("no active claim found for %r" % args.release, file=sys.stderr)
    return 1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--status", action="store_true")
    p.add_argument("--next", action="store_true")
    p.add_argument("--claim")
    p.add_argument("--note", default="")
    p.add_argument("--release")
    args = p.parse_args()

    if args.claim:
        return cmd_claim(args)
    if args.release:
        return cmd_release(args)
    if args.next:
        return cmd_next(args)
    return cmd_status(args)


if __name__ == "__main__":
    sys.exit(main())
