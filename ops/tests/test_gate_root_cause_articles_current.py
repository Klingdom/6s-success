#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_root_cause_articles_current() catches the real
defect it exists for: root_causes.py's `article` mapping and
build_zone_pages.py's cause_reading() docstring silently disagreeing about
which of the 17 frozen causes have no article yet.

The real incident: root_causes.py said EXCESS had no article from
2026-09-07. "more-storage-wont-fix-clutter" (the container trap) shipped
2026-09-08, a genuine, on-topic match, but nothing told root_causes.py, so
10 real friction branches across the diagnosed pilot zones kept silently
skipping it in cause_reading() for two days. Fixed 2026-09-10 by mapping
EXCESS to that article; this test protects the fix and the two-way
consistency check the gate performs, not the semantic judgement that found
the match in the first place (a human/operator call, not a mechanical one).

Run:  python ops/tests/test_gate_root_cause_articles_current.py
"""
import importlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402


def _run():
    preflight.FAIL.clear()
    preflight.WARN.clear()
    preflight.gate_root_cause_articles_current()
    return list(preflight.FAIL)


def main() -> int:
    fails = []

    import root_causes as RC
    import build_zone_pages as BZP
    importlib.reload(RC)
    importlib.reload(BZP)

    # 1. The real, live files must pass clean today.
    live_fails = _run()
    if live_fails:
        fails.append(f"the real, current files fail the gate: {live_fails}")

    # 2. Sanity: EXCESS really is mapped now, CONFLICTING USERS really is not.
    by_name = {c["name"]: c for c in RC.CAUSES}
    if not by_name["EXCESS"].get("article"):
        fails.append("EXCESS has no article in the real root_causes.py; "
                      "the 2026-09-10 fix is missing")
    if by_name["CONFLICTING USERS"].get("article"):
        fails.append("CONFLICTING USERS unexpectedly has an article; "
                      "update this test's assumptions if that is now true")

    # 3. Plant the exact regression this gate exists to catch: the docstring
    #    still claims a cause is unmapped after root_causes.py maps it.
    doc_path = os.path.join(ROOT, "ops", "build_zone_pages.py")
    src = open(doc_path, encoding="utf-8").read()
    marker = "One of the 17 frozen causes (CONFLICTING"
    if marker not in src:
        fails.append("could not find the live docstring text to plant a "
                      "regression against; has the wording changed?")
    else:
        stale = src.replace(
            "One of the 17 frozen causes (CONFLICTING\n    USERS) has no "
            "article yet",
            "Two of the 17 frozen causes (EXCESS,\n    CONFLICTING USERS) "
            "have no article yet")
        if stale == src:
            fails.append("the replacement did not change the file; the "
                          "exact wording this test plants is stale")
        else:
            open(doc_path, "w", encoding="utf-8").write(stale)
            try:
                planted_fails = _run()
                if not planted_fails:
                    fails.append("a stale docstring claiming EXCESS has no "
                                  "article, when root_causes.py maps it to "
                                  "a real one, was not caught")
                elif "EXCESS" not in planted_fails[0][1]:
                    fails.append(f"caught something, but not by name: "
                                  f"{planted_fails}")
            finally:
                open(doc_path, "w", encoding="utf-8").write(src)

    # 4. The opposite drift: docstring silent about a cause root_causes.py
    #    genuinely leaves unmapped.
    src2 = open(doc_path, encoding="utf-8").read()
    marker2 = ("One of the 17 frozen causes (CONFLICTING\n    USERS) has "
               "no article yet")
    if marker2 not in src2:
        fails.append("could not find the live docstring text for check 4")
    else:
        silent = src2.replace(marker2,
                               "No frozen cause is missing an article")
        open(doc_path, "w", encoding="utf-8").write(silent)
        try:
            silent_fails = _run()
            if not silent_fails:
                fails.append("a docstring claiming nothing is unmapped, "
                              "when CONFLICTING USERS genuinely has no "
                              "article, was not caught")
            elif "CONFLICTING USERS" not in silent_fails[0][1]:
                fails.append(f"caught something, but not by name: "
                              f"{silent_fails}")
        finally:
            open(doc_path, "w", encoding="utf-8").write(src2)

    # 5. Restore and confirm clean again, so this test does not leave the
    #    tree dirty even if an assertion above already failed.
    final = open(doc_path, encoding="utf-8").read()
    if final != src:
        fails.append("build_zone_pages.py was not restored to its original "
                      "content after planting regressions")
    final_fails = _run()
    if final_fails:
        fails.append(f"gate does not pass clean after restoring the real "
                      f"file: {final_fails}")

    # 6. The real 2026-09-11 incident: root_causes.py's `article` field is
    #    populated (so checks 1-4 above see it as mapped) but the slug is
    #    missing from cause_reading()'s own lookup table, so it silently
    #    resolves to nothing on every diagnosed zone page carrying that
    #    cause. gate_root_cause_articles_current() reloads build_zone_pages
    #    fresh from disk on every call, so an in-memory monkeypatch of the
    #    lookup dict would not survive that reload; plant the regression in
    #    the source text instead, the same way cases 3 and 4 do, by cutting
    #    one real _CAUSE_ONLY_READING entry out of the file.
    bzp_src = open(doc_path, encoding="utf-8").read()
    marker3 = (
        '    ("../articles/why-you-have-to-dig-for-what-you-need.html",\n'
        '     "Moving three things to get to the one you need?",\n'
        '     "Too many steps is its own root cause, distinct from no '
        'home or poor reach."),\n')
    if marker3 not in bzp_src:
        fails.append("could not find the live _CAUSE_ONLY_READING entry "
                      "to cut for check 6; has the wording changed?")
    else:
        cut = bzp_src.replace(marker3, "")
        open(doc_path, "w", encoding="utf-8").write(cut)
        try:
            reachability_fails = _run()
            if not reachability_fails:
                fails.append(
                    "EXCESS MOTION mapped to an article missing from "
                    "cause_reading()'s own lookup table was not caught")
            elif "EXCESS MOTION" not in reachability_fails[0][1]:
                fails.append(f"caught something, but not by name: "
                              f"{reachability_fails}")
        finally:
            open(doc_path, "w", encoding="utf-8").write(bzp_src)
    final2 = open(doc_path, encoding="utf-8").read()
    if final2 != bzp_src:
        fails.append("build_zone_pages.py was not restored after check 6")
    importlib.reload(RC)
    importlib.reload(BZP)
    check6_clean = _run()
    if check6_clean:
        fails.append(f"gate does not pass clean after restoring the real "
                      f"file post check 6: {check6_clean}")

    if fails:
        print(f"FAIL: {len(fails)} case(s)")
        for f in fails:
            print(f" - {f}")
        return 1
    print("PASS: 6 of 6 cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
