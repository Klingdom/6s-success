#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_keyword_demand_global_rescored_current() catches
ops/keyword-demand-global.json's per-query statuses drifting stale against
site/ between rescores (LRN-0032), the same shape
test_gate_keyword_demand_rescored_current.py already proves for the US file,
but exercised here against the wrapper itself, not just the shared pure
function (which that file already covers in full).

Found live 2026-10-23, scheduled operator cycle: ops/keyword_demand_global.py
had no --rescore at all and nothing watched this file for the drift its US
sibling already had a gate for, so "coat cupboard organisation" sat scored
`gap` with heading_page pointing at an unrelated downloads page long after
/zones/entryway-the-coats-and-outerwear.html ("Also called the coat
cupboard") became the real best match.

Run:  python ops/tests/test_gate_keyword_demand_global_rescored_current.py
"""
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

REAL_PATH = os.path.join(ROOT, "ops", "keyword-demand-global.json")


def _run_in_temp(payload):
    """No real git history needed. Point preflight.ROOT at a throwaway dir
    holding only this payload at ops/keyword-demand-global.json, run the
    gate, return its warnings, then always restore the real ROOT."""
    tmp = tempfile.mkdtemp()
    try:
        ops_dir = os.path.join(tmp, "ops")
        os.makedirs(ops_dir)
        if payload is not None:
            io.open(os.path.join(ops_dir, "keyword-demand-global.json"),
                    "w", encoding="utf-8").write(json.dumps(payload))
        old_root = preflight.ROOT
        preflight.ROOT = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_keyword_demand_global_rescored_current()
            return list(preflight.WARN)
        finally:
            preflight.ROOT = old_root
    finally:
        shutil.rmtree(tmp)


def _run_against_real_file(scored_against_commit):
    """Needs real git history (the gate's own `git log ...site/` call runs
    with cwd=ROOT), so this backs up the real committed file, swaps in
    one differing only by scored_against_commit, runs the gate against
    the real ROOT, then restores the original bytes no matter what."""
    original = io.open(REAL_PATH, encoding="utf-8").read()
    try:
        payload = json.loads(original)
        payload["scored_against_commit"] = scored_against_commit
        io.open(REAL_PATH, "w", encoding="utf-8").write(json.dumps(payload))
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_keyword_demand_global_rescored_current()
        return list(preflight.WARN)
    finally:
        io.open(REAL_PATH, "w", encoding="utf-8").write(original)
        restored = io.open(REAL_PATH, encoding="utf-8").read()
        assert restored == original, "restore failed to reproduce the original"


def main() -> int:
    fails = []

    # 1. No file at all: the gate must do nothing (missing-harvest staleness
    #    is gate_keyword_demand_global_not_stale's job, not this one's).
    warns = _run_in_temp(None)
    if warns:
        fails.append("missing file wrongly warned: %r" % warns)

    # 2. A payload with no scored_against_commit: must warn, by name, and
    #    point at the global tool's own --rescore, not the US one's.
    warns = _run_in_temp({"rows": []})
    if not warns:
        fails.append("missing scored_against_commit did not warn")
    else:
        msg = warns[0][1]
        if "keyword-demand-global.json" not in msg:
            fails.append("warning did not name the global file: %r" % msg)
        if "keyword_demand_global.py --rescore" not in msg:
            fails.append("warning pointed at the wrong fix: %r" % msg)

    # 3. The real committed file, freshly rescored this same cycle,
    #    pointed at the real current HEAD: must NOT warn. Uses the real
    #    ROOT so the gate's own `git log` call runs against real history.
    head = preflight.subprocess.run(
        ["git", "rev-parse", "--short=9", "HEAD"],
        cwd=ROOT, capture_output=True, text=True, timeout=20,
    ).stdout.strip()
    warns = _run_against_real_file(head)
    if warns:
        fails.append("0 commits since rescore wrongly warned: %r" % warns)

    # 4. Pointed at a commit 5+ real site/-touching commits back: must
    #    warn. Walks real git log rather than a fake hash, so this proves
    #    the subprocess call itself, not just the shared pure function.
    out = preflight.subprocess.run(
        ["git", "log", "--format=%H", "-n", "400", "--", "site/"],
        cwd=ROOT, capture_output=True, text=True, timeout=60,
    ).stdout.splitlines()
    if len(out) >= 6:
        old_commit = out[5].strip()[:9]
        warns = _run_against_real_file(old_commit)
        if not warns:
            fails.append("a real 5-commit-stale scored_against_commit "
                          "did not warn")
        elif "keyword-demand-global.json" not in warns[0][1]:
            fails.append("5-commit-stale warning did not name the global "
                          "file: %r" % warns[0][1])
    else:
        fails.append("could not find 6 real site/ commits to test against "
                      "(repository history too short for this case)")

    # 5. The real committed file exactly as it stands now: must pass
    #    clean, proving the live fix rather than only a synthetic
    #    stand-in. (Belt-and-braces: case 3 above already proves this at
    #    HEAD; this re-checks without rewriting the file at all.)
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_keyword_demand_global_rescored_current()
    if preflight.WARN:
        fails.append("the real freshly-rescored file still warns: %r"
                     % preflight.WARN)

    if fails:
        print("FAIL (%d):" % len(fails))
        for f in fails:
            print("  - %s" % f)
        return 1
    print("test_gate_keyword_demand_global_rescored_current: all cases pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
