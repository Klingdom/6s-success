#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_room_guide_mining_diminishing_returns() (and its
pure helper, room_guide_mining_diminishing_returns()) correctly tells apart a
room-guide keyword-scorer state with real work left from one that is
genuinely exhausted site-wide.

Found live 2026-11-12: two scheduled cycles a few hours apart reached
opposite verdicts on the same question ("keep mining BACKLOG-2026-09-07.md
section 2's FORMAT_WORDS/also-called/off-topic-context lane, or stop") from
the same underlying data, because the answer was re-derived by hand each
time rather than checked mechanically. This gate makes it mechanical; this
test proves it can actually fail before it ever gets the chance to pass.

Run:  python ops/tests/test_gate_room_guide_mining_diminishing_returns.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _room(name, gap=0, shortfall=0.0):
    return {"room": name, "gap": [{"query": "x"}] * gap, "shortfall": shortfall}


def main() -> int:
    fails = []

    # 1. Empty input: nothing to say.
    problem = preflight.room_guide_mining_diminishing_returns([])
    if problem:
        fails.append("empty results wrongly warned: %r" % problem)

    # 2. A real gap row anywhere: must NOT warn, real work remains.
    results = [_room("Garage", gap=1, shortfall=0.14),
               _room("Kitchen", gap=0, shortfall=0.07)]
    problem = preflight.room_guide_mining_diminishing_returns(results)
    if problem:
        fails.append("a real gap row wrongly warned: %r" % problem)

    # 3. 0 gap everywhere, but one room's shortfall is over the line: must
    #    NOT warn, that room still has a meaningful partial tier.
    results = [_room("Garage", gap=0, shortfall=0.22),
               _room("Kitchen", gap=0, shortfall=0.07)]
    problem = preflight.room_guide_mining_diminishing_returns(results)
    if problem:
        fails.append("a real 22%% shortfall wrongly warned: %r" % problem)

    # 4. 0 gap everywhere, every shortfall at or under the line: must warn,
    #    by name, naming the worst room and its figure.
    results = [_room("Garage", gap=0, shortfall=0.14),
               _room("Kitchen", gap=0, shortfall=0.07)]
    problem = preflight.room_guide_mining_diminishing_returns(results)
    if not problem:
        fails.append("an exhausted state did not warn")
    else:
        if "Garage" not in problem or "14%" not in problem:
            fails.append("warning did not name the worst room/figure: %r" % problem)
        if "gap" not in problem.lower():
            fails.append("warning did not mention gap rows: %r" % problem)

    # 5. Exactly at the 15% default line: still counts as exhausted (<=, not <).
    results = [_room("Garage", gap=0, shortfall=0.15)]
    problem = preflight.room_guide_mining_diminishing_returns(results)
    if not problem:
        fails.append("a shortfall exactly at the line did not warn")

    # 6. The wrapper against a real but synthetic gap result, via the real
    #    keyword-demand files but a monkeypatched score_room, proves the
    #    wiring itself, not just the shared pure function.
    import room_guide_underperformance as rgu
    real_score_room = rgu.score_room
    try:
        rgu.score_room = lambda us, gl, room: _room(room, gap=1, shortfall=0.5)
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_room_guide_mining_diminishing_returns()
        if preflight.WARN:
            fails.append("wrapper warned despite a monkeypatched real gap: %r"
                         % preflight.WARN)
    finally:
        rgu.score_room = real_score_room

    # 7. The real committed keyword-demand files, as they stand today
    #    (every room already independently confirmed 0 gap, worst under
    #    15%): the real wrapper must warn, proving today's actual state is
    #    the exhausted one this gate exists to name.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_room_guide_mining_diminishing_returns()
    if not preflight.WARN:
        fails.append("the real committed files did not warn; either the "
                     "lane has genuinely stopped being exhausted (good "
                     "news, update this test) or the wrapper is broken")

    if fails:
        print("FAIL (%d):" % len(fails))
        for f in fails:
            print("  - %s" % f)
        return 1
    print("test_gate_room_guide_mining_diminishing_returns: all cases pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
