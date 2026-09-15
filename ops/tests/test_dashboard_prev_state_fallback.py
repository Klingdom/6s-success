#!/usr/bin/env python3
"""
A working-tree state.json that fails to parse must not erase carry-forward memory.

Found 2026-09-15: merge commit d9893032 regenerated the dashboard while
ops/state.json still held its own unresolved conflict markers. json.load()
threw, the old bare `except: pass` swallowed it, and _prev silently became
{}, which then poisoned every carry-forward field (traffic_line,
affiliate_trigger, revenue_month, paying_customers) for every run after it,
because there was nothing left to carry from. _load_prev_state() now falls
back to the last COMMITTED copy (`git show HEAD:ops/state.json`) instead of
{} when the working-tree file will not parse.

dashboard.py runs its whole pipeline at import, so the function is lifted
out of the source rather than imported, matching test_carry_forward.py's own
method for the same reason.

Run:  python ops/tests/test_dashboard_prev_state_fallback.py
"""
import io
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "ops", "dashboard.py")

src = open(SRC, encoding="utf-8").read()
ns = {"io": io, "json": json, "os": os, "sys": sys, "subprocess": subprocess,
      "ROOT": ROOT}
m = re.search(r"^def sh\(.*?(?=\ndef sh_checked)", src, re.S | re.M)
exec(m.group(0), ns)
m = re.search(r"^def _load_prev_state.*?(?=\n\n_prev = _load_prev_state)",
              src, re.S | re.M)
exec(m.group(0), ns)
load_prev_state = ns["_load_prev_state"]


def main() -> int:
    fails = []

    with tempfile.TemporaryDirectory() as d:
        # A file that parses fine must be read directly, no git fallback.
        good = os.path.join(d, "state.json")
        io.open(good, "w", encoding="utf-8").write(
            json.dumps({"traffic_line_last_measured": "70 pageviews"}))
        r = load_prev_state(good)
        if r.get("traffic_line_last_measured") != "70 pageviews":
            fails.append(f"a parseable file must be read as-is, got {r!r}")

        # A file holding literal, unresolved conflict markers (exactly the
        # 2026-09-15 shape) must fall back to git, not silently become {}.
        conflicted = os.path.join(d, "state.json")
        io.open(conflicted, "w", encoding="utf-8").write(
            '{\n<<<<<<< HEAD\n "traffic_line": "a",\n=======\n '
            '"traffic_line": "b",\n>>>>>>> branch\n}\n')
        r = load_prev_state(conflicted)
        if r == {}:
            fails.append("a conflict-marked file must not silently become "
                         "{}; it must fall back to the last committed copy")
        # The real repository's committed ops/state.json always carries a
        # "generated" key; confirm the fallback actually reached git rather
        # than returning some other non-empty accident.
        if "generated" not in r:
            fails.append(f"the git fallback must return the real committed "
                         f"state.json, got keys {sorted(r)!r}")

        # A missing file must also fall back to git rather than raise.
        r = load_prev_state(os.path.join(d, "does-not-exist.json"))
        if "generated" not in r:
            fails.append("a missing file must fall back to the committed "
                         f"copy too, got {r!r}")

    total = 3
    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {total - len(fails)} of {total} cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
