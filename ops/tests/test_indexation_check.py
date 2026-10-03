#!/usr/bin/env python3
"""
Prove ops/indexation_check.py classifies URLs correctly and refuses to let
a blocked engine look like a reading of real indexation.

Run:  python ops/tests/test_indexation_check.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import indexation_check as I                                     # noqa: E402


def main() -> int:
    fails = []

    # 1. classify() by path, including the home-page special case.
    cases = {
        "https://6s-success.com/": "home",
        "https://6s-success.com/index.html": "home",
        "https://6s-success.com/rooms/kitchen": "room",
        "https://6s-success.com/zones/kitchen-the-cooking-zone": "zone",
        "https://6s-success.com/articles/why-is-my-house-always-messy": "article",
        "https://6s-success.com/about.html": "other",
    }
    for url, want in cases.items():
        got = I.classify(url)
        if got != want:
            fails.append("classify(%r) = %r, want %r" % (url, got, want))

    # 2. A clean run with a real canary present merges every URL, including
    #    one from an engine queried after another engine already grew the
    #    in-run confirmed set. This is the exact regression this file's own
    #    merge() had: an engine's canary check must be judged against the
    #    ledger as it stood BEFORE this run, not against entries a sibling
    #    engine already added during the same run.
    ledger = {"checked_at": None, "confirmed": {}, "runs": []}
    results = {
        "duckduckgo": ("ok", ["https://6s-success.com/"]),
        "bing_rss": ("ok", ["https://6s-success.com/about.html",
                            "https://6s-success.com/zones/kitchen-the-cooking-zone"]),
    }
    merged = I.merge(ledger, results, "2026-10-03T00:00:00Z")
    if "https://6s-success.com/zones/kitchen-the-cooking-zone" not in merged["confirmed"]:
        fails.append(
            "a clean second engine's zone URL was dropped merely because it "
            "shares a run with a first engine; canary must be judged "
            "against the pre-run ledger, not a mid-run moving target")
    if merged["confirmed"].get(
            "https://6s-success.com/zones/kitchen-the-cooking-zone", {}
    ).get("section") != "zone":
        fails.append("merged zone URL was not tagged section=zone")

    # 3. A blocked engine (its own URLs do not reproduce anything already
    #    trusted) must be voided and must NOT merge its URLs, even if the
    #    status claims "ok" and even if a sibling engine is clean.
    ledger2 = {"checked_at": None, "confirmed": {}, "runs": []}
    results2 = {
        "duckduckgo": ("ok", ["https://6s-success.com/"]),
        "bing_rss": ("ok", ["https://6s-success.com/zones/some-made-up-zone"]),
    }
    merged2 = I.merge(ledger2, results2, "2026-10-03T00:00:00Z")
    if "https://6s-success.com/zones/some-made-up-zone" in merged2["confirmed"]:
        fails.append(
            "an engine whose result never reproduced a trusted URL was "
            "merged anyway; the canary check did not void it")
    if merged2["runs"][-1]["engines"]["bing_rss"]["voided"] is not True:
        fails.append("the blocked-looking engine was not recorded as voided")
    if merged2["runs"][-1]["engines"]["duckduckgo"]["voided"] is not False:
        fails.append("the clean engine was wrongly voided by a sibling's failure")

    # 4. An engine reporting a non-"ok" status must void regardless of what
    #    URLs (if any) it claims, even if one happens to match a trusted URL.
    ledger3 = {"checked_at": None,
               "confirmed": {"https://6s-success.com/": {"section": "home"}},
               "runs": []}
    results3 = {"duckduckgo": ("http 202", ["https://6s-success.com/"])}
    merged3 = I.merge(ledger3, results3, "2026-10-03T00:00:00Z")
    if merged3["runs"][-1]["engines"]["duckduckgo"]["voided"] is not True:
        fails.append("a non-ok status was not voided even though its URL matched")

    # 5. Nothing already in the ledger is ever removed by a run that fails
    #    to repeat it (the whole point of an additive ledger).
    ledger4 = {"checked_at": "2026-10-01T00:00:00Z",
               "confirmed": {"https://6s-success.com/zones/old-zone":
                              {"section": "zone", "first_seen": "2026-10-01T00:00:00Z",
                               "last_seen": "2026-10-01T00:00:00Z"}},
               "runs": []}
    results4 = {"duckduckgo": ("ok", ["https://6s-success.com/"]),
                "bing_rss": ("empty", [])}
    merged4 = I.merge(ledger4, results4, "2026-10-03T00:00:00Z")
    if "https://6s-success.com/zones/old-zone" not in merged4["confirmed"]:
        fails.append("a previously confirmed URL disappeared after a run "
                     "that simply did not repeat it")

    if fails:
        print("FAIL (%d):" % len(fails))
        for f in fails:
            print("  - %s" % f)
        return 1
    print("test_indexation_check: all cases pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
