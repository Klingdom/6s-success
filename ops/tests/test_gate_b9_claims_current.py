#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_b9_claims_current() (via its pure logic,
b9_claim_problems()) can actually fail on each of the three real shapes it
exists to catch, and stays clean on an honest ledger.

Found live 2026-09-29: three duplicate-work collisions on B9 room decks
inside one day, each costing a full extra preflight re-run and, twice, a
real regression fix reconciled on top of it. ops/b9_claims.py gives
sessions a claim-before-building signal to reduce that; this gate catches
the ways the claims ledger itself can go stale or wrong, which would
otherwise recreate the same starvation/collision problem one level up
(every room permanently "claimed" by an abandoned entry, or nobody ever
told a finished claim is done).

Run:  python ops/tests/test_gate_b9_claims_current.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

NOW = "2026-09-29T12:00:00Z"

DIAGNOSIS = {
    "Guest Bedroom": (False, 5),
    "Guest Bathroom": (False, 5),
    "Living Room": (False, 6),
    "Hall Closet": (True, 5),
}


def main() -> int:
    fails = []

    # 1. Unknown room name (a typo): must fire, must name the room.
    problems = preflight.b9_claim_problems(
        [{"room": "Guset Bedroom", "status": "in_progress",
          "claimed_at": NOW}],
        DIAGNOSIS, NOW)
    if not any("Guset Bedroom" in p and "not a real room" in p
               for p in problems):
        fails.append("unknown room name did not fire: %r" % problems)

    # 2. Stale abandoned claim: in_progress, claimed 5 hours ago (over the
    #    3-hour default), room still undiagnosed. Must fire, must name the
    #    room and call it stale/abandoned, not just "unknown".
    problems = preflight.b9_claim_problems(
        [{"room": "Living Room", "status": "in_progress",
          "claimed_at": "2026-09-29T07:00:00Z"}],
        DIAGNOSIS, NOW)
    if not any("Living Room" in p and "abandoned" in p for p in problems):
        fails.append("stale abandoned claim did not fire: %r" % problems)

    # 3. Finished-but-uncleared claim: in_progress, but the room is already
    #    fully diagnosed. Must fire, worded distinctly from case 2 (this is
    #    a cleanup nag, not a collision risk).
    problems = preflight.b9_claim_problems(
        [{"room": "Hall Closet", "status": "in_progress",
          "claimed_at": NOW}],
        DIAGNOSIS, NOW)
    if not any("Hall Closet" in p and "fully diagnosed" in p
               for p in problems):
        fails.append("finished-but-uncleared claim did not fire: %r" % problems)

    # 4. A fresh in_progress claim on a genuinely undiagnosed room (the
    #    normal, healthy case): must NOT fire.
    problems = preflight.b9_claim_problems(
        [{"room": "Guest Bedroom", "status": "in_progress",
          "claimed_at": NOW}],
        DIAGNOSIS, NOW)
    if problems:
        fails.append("healthy fresh claim wrongly fired: %r" % problems)

    # 5. A done claim, whatever its age or room state: must NOT fire.
    problems = preflight.b9_claim_problems(
        [{"room": "Hall Closet", "status": "done",
          "claimed_at": "2026-09-29T01:00:00Z"}],
        DIAGNOSIS, NOW)
    if problems:
        fails.append("done claim wrongly fired: %r" % problems)

    # 6. Empty ledger: must NOT fire.
    problems = preflight.b9_claim_problems([], DIAGNOSIS, NOW)
    if problems:
        fails.append("empty ledger wrongly fired: %r" % problems)

    # 7. A claim just under the staleness threshold (2 hours old): must
    #    NOT fire as stale.
    problems = preflight.b9_claim_problems(
        [{"room": "Living Room", "status": "in_progress",
          "claimed_at": "2026-09-29T10:00:00Z"}],
        DIAGNOSIS, NOW)
    if problems:
        fails.append("claim under the staleness threshold wrongly fired: %r"
                     % problems)

    if fails:
        print("FAIL:")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: 7/7 cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
