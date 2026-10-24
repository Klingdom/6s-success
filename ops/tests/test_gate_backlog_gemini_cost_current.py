#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_backlog_gemini_cost_current() catches
BACKLOG-2026-09-07.md's section 6 "Gemini billing" row repeating a dollar
figure that OWNER-ACTIONS.md 1b's own measured cost table has since
superseded.

Found 2026-10-24, scheduled operator cycle: row C5 (section 2) of this same
file already carried a note that its original $13.53/$47.26 pair was
superseded by OWNER-ACTIONS.md 1b's table, but the section 6 row for the
identical ask, two sections later in the same file, still quoted the stale
pair with no such note. This test proves the new gate would have caught it.

Run:  python ops/tests/test_gate_backlog_gemini_cost_current.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

OA_TEMPLATE = (
    "| Job | Images | Flash | Flash batch | Pro |\n"
    "|---|---|---|---|---|\n"
    "| Entryway deck card art | 89 | $3.47 | $1.74 | $11.93 |\n"
    "| **Everything** | **221** | **$8.62** | **$4.32** | **$29.62** |\n"
)

BACKLOG_TEMPLATE = (
    "| 2 | Search Console | 2 min | done |\n"
    "| 3 | **Gemini billing** | 5 min | every image on the roadmap, %s |\n"
    "| 4 | Amazon KDP and Etsy accounts | 30 min | buyers already in them |\n"
)


def _run(oa_text, backlog_text):
    tmp = tempfile.mkdtemp()
    try:
        io.open(os.path.join(tmp, "OWNER-ACTIONS.md"), "w",
                encoding="utf-8").write(oa_text)
        io.open(os.path.join(tmp, "BACKLOG-2026-09-07.md"), "w",
                encoding="utf-8").write(backlog_text)
        old_root = preflight.ROOT
        preflight.ROOT = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_backlog_gemini_cost_current()
            return list(preflight.FAIL), list(preflight.WARN)
        finally:
            preflight.ROOT = old_root
    finally:
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. The real regression shape: row quotes a stale, superseded pair.
    r, w = _run(OA_TEMPLATE, BACKLOG_TEMPLATE % "$13.53 to $47.26")
    if not r or "backlog-gemini-cost-current" != r[0][0]:
        fails.append("the real stale-cost shape was not caught: %r" % (r,))
    elif "4.32" not in r[0][1] or "29.62" not in r[0][1]:
        fails.append("failure message did not name the current range: %r"
                      % (r[0][1],))

    # 2. Row already matches the current Flash-batch-to-Pro range: no fail.
    r, w = _run(OA_TEMPLATE, BACKLOG_TEMPLATE % "$4.32 to $29.62")
    if r:
        fails.append("genuine agreement with the current range wrongly "
                      "flagged: %r" % (r,))

    # 3. Row matches the current Flash-to-Pro range instead: also no fail.
    r, w = _run(OA_TEMPLATE, BACKLOG_TEMPLATE % "$8.62 to $29.62")
    if r:
        fails.append("the Flash-to-Pro range was wrongly flagged: %r" % (r,))

    # 4. OWNER-ACTIONS.md's cost table has moved or changed shape: warn,
    #    never fail.
    r, w = _run("no such table here\n", BACKLOG_TEMPLATE % "$13.53 to $47.26")
    if r:
        fails.append("a reshaped OWNER-ACTIONS.md was failed instead of "
                      "warned: %r" % (r,))
    if not w:
        fails.append("a reshaped OWNER-ACTIONS.md produced no warning")

    # 5. BACKLOG-2026-09-07.md's row has moved or changed shape: warn, never
    #    fail.
    r, w = _run(OA_TEMPLATE, "no such row here\n")
    if r:
        fails.append("a reshaped BACKLOG row was failed instead of "
                      "warned: %r" % (r,))
    if not w:
        fails.append("a reshaped BACKLOG row produced no warning")

    # 6. The real, committed documents: clean, now that the row has been
    #    corrected in place.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_backlog_gemini_cost_current()
    if preflight.FAIL:
        fails.append("the real committed documents failed: %r"
                     % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_backlog_gemini_cost_current, 6/6 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
