"""Prove ops/check_goals_keyword_cluster_citation_fast.py actually catches a
stale GOALS.md keyword-cluster citation, and stays silent on a current one,
without needing gate_tests or anything after it in preflight.py's own call
order.

Found 2026-11-25 (at least the seventh time): GOALS.md's own "small space" /
"cheap/budget/DIY" cluster citation drifted from the real committed
ops/keyword-demand.json and broke checks.yml on two consecutive pushes to
main. test_gate_goals_keyword_cluster_citation_current.py already catches
this, but it lives inside gate_tests, which this sandbox's documented
Chromium hang forces every local preflight run to skip with --skip-tests, so
a local run never reaches it before push. ops/check_goals_keyword_cluster_
citation_fast.py (mirroring ops/check_risks_evidence_fast.py's own
reasoning) calls the gate directly, skipping gate_tests entirely, so it can
run in the pre-push hook. This test proves the wrapper's exit code and
output, not the gate's own logic, which
ops/tests/test_gate_goals_keyword_cluster_citation_current.py already
covers.

Run:  python ops/tests/test_check_goals_keyword_cluster_citation_fast.py
"""
import importlib.util
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OPS = os.path.dirname(HERE)
sys.path.insert(0, OPS)
sys.argv = ["preflight.py"]

import preflight as P  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "check_goals_keyword_cluster_citation_fast",
    os.path.join(OPS, "check_goals_keyword_cluster_citation_fast.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

LIVE = {
    "small space": {"covered": 17, "partial": 8, "gap": 0, "total": 25},
    "cheap/budget/DIY": {"covered": 40, "partial": 2, "gap": 0, "total": 42},
}

CURRENT_TEXT = ('"small space" is **17 covered / 8 partial / 0 gap of 25** '
                'and "cheap/budget/DIY" is **40 covered / 2 partial / 0 '
                'gap of 42**.\n')

STALE_TEXT = ('"small space" is **999 covered / 8 partial / 0 gap of 25** '
              'and "cheap/budget/DIY" is **40 covered / 2 partial / 0 '
              'gap of 42**.\n')


def _rows_for(live_counts):
    rows = []
    for status in ("covered", "partial", "gap"):
        for _ in range(live_counts["small space"][status]):
            rows.append({"query": "small space idea", "status": status})
        for _ in range(live_counts["cheap/budget/DIY"][status]):
            rows.append({"query": "diy project", "status": status})
    return rows


def _run(goals_text):
    with tempfile.TemporaryDirectory() as root:
        demand_fp = os.path.join(root, "keyword-demand.json")
        json.dump({"rows": _rows_for(LIVE)}, io.open(demand_fp, "w"))
        goals_fp = os.path.join(root, "GOALS.md")
        io.open(goals_fp, "w", encoding="utf-8").write(goals_text)
        old_fn = P.gate_goals_keyword_cluster_citation_current
        P.gate_goals_keyword_cluster_citation_current = (
            lambda: old_fn(goals_fp, demand_fp))
        C.preflight.gate_goals_keyword_cluster_citation_current = (
            P.gate_goals_keyword_cluster_citation_current)
        try:
            return C.main()
        finally:
            P.gate_goals_keyword_cluster_citation_current = old_fn
            C.preflight.gate_goals_keyword_cluster_citation_current = old_fn


def test_current_citation_passes():
    assert _run(CURRENT_TEXT) == 0


def test_stale_citation_fails():
    assert _run(STALE_TEXT) == 1


def main():
    tests = [test_current_citation_passes, test_stale_citation_fails]
    bad = []
    for t in tests:
        try:
            t()
        except AssertionError as e:
            bad.append("%s: %s" % (t.__name__, e))
    if bad:
        print("FAIL: check_goals_keyword_cluster_citation_fast wrapper")
        for b in bad:
            print("  - " + b)
        return 1
    print("OK: check_goals_keyword_cluster_citation_fast wrapper, %d/%d"
          % (len(tests), len(tests)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
