#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_goals_keyword_cluster_citation_current()
catches a real regression found live 2026-10-02: GOALS.md's O1 section
cited the "small space" and "cheap/budget/DIY" query-cluster coverage as
1/26/10/37 and 0/82/17/99, both stale the same day BACKLOG-2026-09-07.md's
A13 and A14 shipped the pages that moved them (to 20/16/1/37 and 29/66/4/99).
A concurrent PM check-in read the stale sentence instead of re-deriving
from ops/keyword-demand.json directly and drafted a handoff for an
already-closed gap, the exact LRN-0032 shape recurring against prose.

Run:  python ops/tests/test_gate_goals_keyword_cluster_citation_current.py
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402
import keyword_demand as K                                      # noqa: E402

STALE = ('Two other clusters: "small space" is **1 covered / 26 partial / '
         '10 gap of 37**, and "cheap/budget/DIY" is **0 covered / 82 '
         'partial / 17 gap of 99**.\n')

FRESH = ('Two other clusters: "small space" is **20 covered / 16 partial / '
         '1 gap of 37**, and "cheap/budget/DIY" is **29 covered / 66 '
         'partial / 4 gap of 99**.\n')

NO_CITATION = "Nothing about either cluster is said here at all.\n"


def _rows_for(live_counts):
    """Build the minimal keyword-demand.json rows that reproduce the given
    cluster_counts()-shaped dicts exactly, for both named clusters."""
    rows = []
    for status in ("covered", "partial", "gap"):
        for _ in range(live_counts["small space"][status]):
            rows.append({"query": "small space idea", "status": status})
        for _ in range(live_counts["cheap/budget/DIY"][status]):
            rows.append({"query": "diy project", "status": status})
    return rows


FRESH_LIVE = {
    "small space": {"covered": 20, "partial": 16, "gap": 1, "total": 37},
    "cheap/budget/DIY": {"covered": 29, "partial": 66, "gap": 4, "total": 99},
}


def _write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def main() -> int:
    fails = []

    # 1. The pure comparison function, in isolation: stale citation vs the
    #    live counts it should have been re-derived from.
    problems = K.goals_cluster_citation_problems(STALE, FRESH_LIVE)
    if len(problems) != 2:
        fails.append("goals_cluster_citation_problems() on the exact stale "
                      "defect shape must name both clusters, got: %r"
                      % problems)
    problems = K.goals_cluster_citation_problems(FRESH, FRESH_LIVE)
    if problems:
        fails.append("goals_cluster_citation_problems() on a citation "
                      "matching the live counts must find nothing, got: %r"
                      % problems)
    problems = K.goals_cluster_citation_problems(NO_CITATION, FRESH_LIVE)
    if problems:
        fails.append("a file citing neither cluster in this phrasing must "
                      "not be flagged (not this function's business): %r"
                      % problems)

    with tempfile.TemporaryDirectory() as d:
        demand_fp = os.path.join(d, "keyword-demand.json")
        with open(demand_fp, "w", encoding="utf-8") as f:
            json.dump({"rows": _rows_for(FRESH_LIVE)}, f)

        # 2. The real defect shape end to end: must warn, naming both
        #    clusters.
        goals_fp = _write(os.path.join(d, "stale.md"), STALE)
        preflight.WARN.clear()
        preflight.gate_goals_keyword_cluster_citation_current(
            goals_fp, demand_fp)
        if len(preflight.WARN) != 2:
            fails.append("the stale GOALS.md shape must warn twice (once "
                          "per drifted cluster): %r" % preflight.WARN)

        # 3. The fix: a citation matching the live file exactly, must warn
        #    nothing.
        goals_fp = _write(os.path.join(d, "fresh.md"), FRESH)
        preflight.WARN.clear()
        preflight.gate_goals_keyword_cluster_citation_current(
            goals_fp, demand_fp)
        if preflight.WARN:
            fails.append("a citation matching the live counts must not "
                          "warn: %r" % preflight.WARN)

        # 4. A file naming neither cluster in this phrasing: nothing to
        #    catch, must not warn (a legitimate rewording is not this
        #    gate's business).
        goals_fp = _write(os.path.join(d, "none.md"), NO_CITATION)
        preflight.WARN.clear()
        preflight.gate_goals_keyword_cluster_citation_current(
            goals_fp, demand_fp)
        if preflight.WARN:
            fails.append("a file citing neither cluster must not warn: %r"
                          % preflight.WARN)

        # 5. A keyword-demand.json that does not parse: must warn it could
        #    not check, never crash and never claim freshness.
        bad_demand_fp = os.path.join(d, "bad.json")
        with open(bad_demand_fp, "w", encoding="utf-8") as f:
            f.write("not json")
        goals_fp = _write(os.path.join(d, "stale2.md"), STALE)
        preflight.WARN.clear()
        preflight.gate_goals_keyword_cluster_citation_current(
            goals_fp, bad_demand_fp)
        if not preflight.WARN:
            fails.append("an unparseable keyword-demand.json must warn "
                          "that the citation could not be checked")

        # 6. Either file missing entirely: unmeasurable, must not warn.
        preflight.WARN.clear()
        preflight.gate_goals_keyword_cluster_citation_current(
            os.path.join(d, "does-not-exist.md"), demand_fp)
        if preflight.WARN:
            fails.append("a missing GOALS.md must not warn: %r"
                          % preflight.WARN)

    # 7. The real, committed GOALS.md and keyword-demand.json, after this
    #    cycle's own fix, must warn nothing.
    preflight.WARN.clear()
    preflight.FAIL.clear()
    preflight.gate_goals_keyword_cluster_citation_current()
    if preflight.WARN:
        fails.append("the real committed files must be clean after this "
                      "cycle's own fix: %r" % preflight.WARN)
    if preflight.FAIL:
        fails.append("this is a warn-only gate; it must never FAIL: %r"
                      % preflight.FAIL)

    if fails:
        print("FAIL:")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: 7/7 cases (fail-then-pass proved against the real defect "
          "shape)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
