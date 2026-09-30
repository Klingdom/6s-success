#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_owner_actions_zone_art_citation_current()
catches OWNER-ACTIONS.md citing a stale zone-hero-rejection count against
ops/hero-verdicts.json's own live "no" count.

Found 2026-09-30, scheduled operator: OWNER-ACTIONS.md's 1b section still
read "Eight zone pages ship with no picture at all", citing a
2026-09-09/2026-09-11 measurement, three weeks after a same-document
correction (2026-09-17) had already brought the real count down to three,
and twelve days after 7c6a83084 (2026-09-27) gave every rejected zone hero
an honest text-panel fallback, so none of them ship with nothing to look at
any more either. Corrected by hand; this gate stops the count drifting back
unnoticed.

Run:  python ops/tests/test_gate_owner_actions_zone_art_citation_current.py
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

DOC_TEMPLATE = (
    "gap behind this gate). **Current reading: ops/hero-verdicts.json "
    "reads %s\nrejected zone hero(es), and zero zone pages ship with no "
    "picture at all.**\n"
)


def _verdicts(no_count):
    d = {}
    for i in range(no_count):
        d["zone-%d" % i] = {"sha": "x", "verdict": "no"}
    d["zone-ok"] = {"sha": "y", "verdict": "yes"}
    return d


def _run(verdict_no_count, cited_n, no_doc=False):
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "ops"), exist_ok=True)
    if not no_doc:
        io.open(os.path.join(tmp, "OWNER-ACTIONS.md"), "w",
                encoding="utf-8").write(DOC_TEMPLATE % cited_n)
    json.dump(_verdicts(verdict_no_count),
              io.open(os.path.join(tmp, "ops", "hero-verdicts.json"), "w",
                      encoding="utf-8"))
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_owner_actions_zone_art_citation_current()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. The real regression shape: doc cites 8, verdicts file now holds 3.
    #    Must fail.
    r, w = _run(verdict_no_count=3, cited_n=8)
    if not r or "owner-actions-zone-art-citation-current" != r[0][0]:
        fails.append("the real regression shape was not caught: %r" % (r,))

    # 2. Doc and verdicts file agree: no failure.
    r, w = _run(verdict_no_count=5, cited_n=5)
    if r:
        fails.append("genuine agreement wrongly flagged: %r" % (r,))

    # 3. Verdicts file drops to zero (every hero eventually accepted), doc
    #    still cites a positive count: must fail.
    r, w = _run(verdict_no_count=0, cited_n=3)
    if not r:
        fails.append("a stale positive citation against zero was not "
                     "caught: %r" % (r,))

    # 4. OWNER-ACTIONS.md does not exist at all: silent, never a crash.
    r, w = _run(verdict_no_count=3, cited_n=3, no_doc=True)
    if r or w:
        fails.append("a missing OWNER-ACTIONS.md was not silent: %r/%r"
                     % (r, w))

    # 5. The real, committed documents: clean, now that the citation has
    #    been corrected in place.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_owner_actions_zone_art_citation_current()
    if preflight.FAIL:
        fails.append("the real committed documents failed: %r"
                     % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_owner_actions_zone_art_citation_current, 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
