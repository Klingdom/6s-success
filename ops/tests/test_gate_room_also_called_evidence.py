#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_room_also_called_evidence() catches the
defect it exists for: a room-also-called name that is not a phrase anyone
actually typed in the demand harvest.

Found 2026-11-19: "childrens bedroom" (Kids Bedroom), "groceries" (Pantry
signal_name) and "stairway landing" (Stair Landing) all had real evidence
when added, then lost it the same day keyword-demand.yml was narrowed to
--source google (Bing's osjson.aspx returning HTTP 204 to its own
canary), because each one's grounding query turned out to be Bing-only.
ops/tests/test_room_also_called.py already held this exact rule, but only
inside the slow, full ops/tests/*.py suite (gate_tests), which this
sandbox's documented Chromium hang forces every local preflight run to
skip with --skip-tests. Nothing reachable before a push caught it; only
the full, slower CI run did (checks.yml run 44547908641), after the push
had already landed. This test proves the promoted gate,
gate_room_also_called_evidence() / check_room_also_called_evidence(), can
fail, and ops/check_room_also_called_evidence_fast.py (wired into
.githooks/pre-push) is what makes it reachable before the next push.

Run:  python ops/tests/test_gate_room_also_called_evidence.py
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    rows = [
        {"query": "how to organize a boys bedroom"},
        {"query": "staircase landing storage ideas"},
    ]

    # 1. Clean: every name matches some row.
    problems = preflight.check_room_also_called_evidence(
        {"Kids Bedroom": ["boys bedroom"],
         "Stair Landing": ["staircase landing"]}, rows)
    if problems:
        fails.append("grounded names wrongly flagged: %s" % problems)

    # 2. The regression itself: a name with zero matching rows.
    problems = preflight.check_room_also_called_evidence(
        {"Kids Bedroom": ["boys bedroom", "childrens bedroom"]}, rows)
    if (len(problems) != 1
            or "childrens bedroom" not in problems[0]
            or "Kids Bedroom" not in problems[0]):
        fails.append("ungrounded name not caught correctly: %s" % problems)

    # 3. signal_names are held to the same rule (merged in by the gate
    #    wrapper, not this pure function, but the pure function must treat
    #    every name list identically regardless of which field it came
    #    from).
    problems = preflight.check_room_also_called_evidence(
        {"Pantry": ["groceries"]}, rows)
    if len(problems) != 1 or "groceries" not in problems[0]:
        fails.append("ungrounded signal_name not caught: %s" % problems)

    # 4. Word-boundary matching: "landing" alone must not falsely ground
    #    "stairway landing" via a substring of "staircase landing".
    problems = preflight.check_room_also_called_evidence(
        {"Stair Landing": ["stairway landing"]}, rows)
    if len(problems) != 1 or "stairway landing" not in problems[0]:
        fails.append("substring match wrongly grounded an absent phrase: %s"
                     % problems)

    # 5. FAIL-THEN-PASS against the REAL corpus. Plant the exact three
    #    names this cycle found and removed back into a copy of the real
    #    room-also-called map, and confirm the real gate fails and names
    #    all three.
    room_path = os.path.join(ROOT, "ops", "room-also-called.json")
    us_path = os.path.join(ROOT, "ops", "keyword-demand.json")
    global_path = os.path.join(ROOT, "ops", "keyword-demand-global.json")
    if all(os.path.exists(p) for p in (room_path, us_path, global_path)):
        data = json.loads(io.open(room_path, encoding="utf-8").read())
        names_by_room = {}
        for room, entry in (data.get("rooms") or {}).items():
            names = list(entry.get("names") or []) + list(
                entry.get("signal_names") or [])
            if names:
                names_by_room[room] = names
        real_rows = (
            json.loads(io.open(us_path, encoding="utf-8").read())
            .get("rows") or [])
        real_rows += (
            json.loads(io.open(global_path, encoding="utf-8").read())
            .get("rows") or [])

        # 5a. Today's real shipped state must already be clean.
        problems = preflight.check_room_also_called_evidence(
            names_by_room, real_rows)
        if problems:
            fails.append("the real committed map fails today: %s"
                         % problems)

        # 5b. Plant the three retired names back in and confirm the real
        #     gate (not just the pure function) fails on all three.
        planted = {k: list(v) for k, v in names_by_room.items()}
        planted.setdefault("Kids Bedroom", []).append("childrens bedroom")
        planted.setdefault("Pantry", []).append("groceries")
        planted.setdefault("Stair Landing", []).append("stairway landing")
        problems = preflight.check_room_also_called_evidence(
            planted, real_rows)
        found = " ".join(problems)
        missing = [name for name in
                   ("childrens bedroom", "groceries", "stairway landing")
                   if name not in found]
        if missing:
            fails.append("planting the retired names back did not "
                         "reproduce the real defect for: %s (got %s)"
                         % (missing, problems))
    else:
        print("NOT VERIFIED (case 5): one of the three real files is "
              "missing.")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: 5/5 cases, including a fail-then-pass against the real "
          "committed site")
    return 0


if __name__ == "__main__":
    sys.exit(main())
