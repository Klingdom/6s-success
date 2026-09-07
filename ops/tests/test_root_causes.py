#!/usr/bin/env python3
"""
Prove ops/root_causes.py's own self-check and unknown_ids_in() actually catch
the defect they exist for, rather than trusting a clean preflight run once.

Companion to ops/preflight.py's gate_root_cause_vocabulary, added with
PLAN-MICROZONES-DECKS-APP.md item M1. The gate was already proved fail-then-
pass by hand in an isolated worktree before this file existed; this makes
that proof repeatable without a worktree.

Run:  python ops/tests/test_root_causes.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import root_causes as RC                                      # noqa: E402


def main() -> int:
    fails = []

    # 1. The 12 Kitchen-origin ids are present, unchanged, and match the
    #    real cards in ops/cardtext/kitchen-deck.json (not just this file's
    #    own claim that they do).
    import json
    d = json.load(open(os.path.join(ROOT, "ops", "cardtext", "kitchen-deck.json"),
                        encoding="utf-8"))
    real = {c["id"]: c for c in d["cards"] if c.get("type") == "ROOT CAUSE CARD"}
    if set(real) - set(RC.BY_ID):
        fails.append(f"kitchen-deck.json has cause id(s) missing from "
                      f"root_causes.py: {sorted(set(real) - set(RC.BY_ID))}")
    for cid, card in real.items():
        v = RC.BY_ID.get(cid)
        if v and (v["name"] != card["title"] or v["six_s"] != card["six_s"]):
            fails.append(f"{cid}: root_causes.py disagrees with the real "
                          f"card (name/six_s drifted)")

    # 2. A known-good structure reports no unknown ids.
    clean = {"cards": [{"related": {"root_causes": ["KC-001", "RC-013"]}}]}
    found = RC.unknown_ids_in(clean)
    if found:
        fails.append(f"a structure using only real ids was flagged: {found}")

    # 3. A planted bad id, the exact shape a mistyped or retired cause id
    #    would take, must be caught.
    planted = {"cards": [{"branches": [{"answer": "x", "root_cause": "KC-099"}]}]}
    found = RC.unknown_ids_in(planted)
    if found != {"KC-099"}:
        fails.append(f"a planted unknown id KC-099 was not caught, got {found}")

    # 4. A string that merely looks close (KC-01, no leading zero padding)
    #    must not be silently accepted as KC-001.
    near_miss = {"x": "KC-01"}
    found = RC.unknown_ids_in(near_miss)
    if found != {"KC-01"}:
        fails.append("a near-miss id (wrong digit count) was not flagged "
                      f"as unknown, got {found}")

    # 5. Ordinary strings that are not card-id shaped must never be flagged.
    noise = {"title": "The RC car needs KC-800 volts", "code": "AB-001"}
    found = RC.unknown_ids_in(noise)
    if found:
        fails.append(f"non-cause text was incorrectly flagged as a cause id: {found}")

    # 6. Every cause has a unique id, a valid six_s, and non-empty prose.
    #    (root_causes.py runs this at import time; re-run it explicitly so a
    #    future refactor that removes the import-time call still gets it.)
    try:
        RC._self_check()
    except ValueError as e:
        fails.append(f"root_causes.py's own self-check failed: {e}")

    # 7. Every cause with an article names a real file.
    for c in RC.CAUSES:
        if c["article"]:
            path = os.path.join(ROOT, "site", "articles", c["article"] + ".html")
            if not os.path.exists(path):
                fails.append(f"{c['id']} names article {c['article']!r}, "
                              f"no such file at site/articles/")

    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {7 - len(fails)} of 7 cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
