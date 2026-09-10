#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_goals_revenue_current() catches GOALS.md
claiming "$0 in the last 30 days" while STATUS.md's own measured revenue
row disagrees.

Found 2026-09-10: GOALS.md's revenue baseline said "$19 lifetime, one
customer, $0 in the last 30 days," written 2026-09-02, eleven days after the
site's only sale (2026-08-21). STATUS.md's own measured revenue row has said
"$19 gross / $18.15 net | Last 30 days" for the same transaction the entire
time. Two authoritative documents disagreed about the single number the main
goal is measured against. Corrected by hand; this gate stops it drifting
back.

Run:  python ops/tests/test_gate_goals_revenue_current.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

STATUS_TEMPLATE = "| Revenue | %s | Last 30 days | some note |\n"


def _run(goals_text, status_revenue_cell):
    tmp = tempfile.mkdtemp()
    io.open(os.path.join(tmp, "GOALS.md"), "w", encoding="utf-8").write(goals_text)
    io.open(os.path.join(tmp, "STATUS.md"), "w", encoding="utf-8").write(
        STATUS_TEMPLATE % status_revenue_cell)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_goals_revenue_current()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. The real regression shape: GOALS.md claims $0 in the last 30 days,
    #    STATUS.md's measured row says $19 for the same window. Must fail.
    r, w = _run("Baseline: $19 lifetime, one customer, $0 in the last 30 "
                "days.", "$19 gross / $18.15 net")
    if not r or "goals-revenue-current" != r[0][0]:
        fails.append("the real regression shape was not caught: %r" % (r,))

    # 2. Both agree on zero: no failure.
    r, w = _run("Baseline: $0 lifetime, $0 in the last 30 days.", "$0")
    if r:
        fails.append("genuine agreement on $0 wrongly flagged: %r" % (r,))

    # 3. GOALS.md makes no 30-day revenue claim at all: no failure.
    r, w = _run("Baseline: $19 lifetime, one customer.", "$19 gross")
    if r:
        fails.append("silence on the 30-day figure wrongly flagged: %r"
                     % (r,))

    # 4. STATUS.md's row is missing/unparsable: warn, never a silent pass
    #    and never a fail.
    tmp = tempfile.mkdtemp()
    io.open(os.path.join(tmp, "GOALS.md"), "w", encoding="utf-8").write(
        "Baseline: $0 in the last 30 days.")
    io.open(os.path.join(tmp, "STATUS.md"), "w", encoding="utf-8").write(
        "no revenue table here.\n")
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_goals_revenue_current()
        r, w = list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root
        shutil.rmtree(tmp)
    if r:
        fails.append("an unparsable STATUS.md was failed instead of warned: "
                     "%r" % (r,))
    if not w:
        fails.append("an unparsable STATUS.md produced no warning at all")

    # 5. The real, committed documents: clean, now that GOALS.md has been
    #    corrected in place.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_goals_revenue_current()
    if preflight.FAIL:
        fails.append("the real committed documents failed: %r"
                     % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_goals_revenue_current, 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
