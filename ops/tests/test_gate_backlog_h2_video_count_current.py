#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_backlog_h2_video_count_current() catches
BACKLOG-2026-H2.md's 3.10 row repeating a stale published-video count from
its own last dated note, independently of GOALS.md.

Found 2026-09-17: gate_goals_published_videos_current already protects
GOALS.md's "Published videos" row against ops/state-checkin.json, but the
identical fact is stated a second time in BACKLOG-2026-H2.md's 3.10 row
("5 narrated videos live 2026-09-02/03... 109 to go"), which nothing
checked. The real count reached 12 of 114 (measured 2026-09-17 01:34) two
weeks before this was caught by an end-to-end read of the file, not by any
gate. This test proves the new gate would have caught it.

Run:  python ops/tests/test_gate_backlog_h2_video_count_current.py
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

ROW_TEMPLATE = (
    "| 3.10 | Post the 114 zone-reset videos to a social video platform | "
    "at least one clip live | 0.2 | **%d narrated videos live "
    "2026-09-02/03, Phil.** %d to go, same wall, no operator credential |\n"
)


def _run(row_text, state):
    tmp = tempfile.mkdtemp()
    try:
        io.open(os.path.join(tmp, "BACKLOG-2026-H2.md"), "w",
                encoding="utf-8").write(row_text)
        os.makedirs(os.path.join(tmp, "ops"))
        io.open(os.path.join(tmp, "ops", "state-checkin.json"), "w",
                encoding="utf-8").write(json.dumps(state))
        old_root = preflight.ROOT
        preflight.ROOT = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_backlog_h2_video_count_current()
            return list(preflight.FAIL), list(preflight.WARN)
        finally:
            preflight.ROOT = old_root
    finally:
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. The real regression shape: row says 5, real measurement says 12.
    r, w = _run(ROW_TEMPLATE % (5, 109),
                {"youtube_published_last_measured": 12,
                 "youtube_published_measured_at": "2026-09-17 01:34"})
    if not r or "backlog-h2-video-count-current" != r[0][0]:
        fails.append("the real stale-count shape was not caught: %r" % (r,))
    elif "5" not in r[0][1] or "12" not in r[0][1]:
        fails.append("failure message did not name both the claimed and "
                      "real counts: %r" % (r[0][1],))

    # 2. Row already matches reality: no failure.
    r, w = _run(ROW_TEMPLATE % (12, 102),
                {"youtube_published_last_measured": 12,
                 "youtube_published_measured_at": "2026-09-17 01:34"})
    if r:
        fails.append("genuine agreement with reality wrongly flagged: %r" % (r,))

    # 3. state-checkin.json has no measurement yet: silent, no fail/warn.
    r, w = _run(ROW_TEMPLATE % (5, 109), {})
    if r or w:
        fails.append("an unmeasured state-checkin.json was flagged instead "
                      "of silently skipped: fail=%r warn=%r" % (r, w))

    # 4. The row has been rewritten to no longer state a bare count this
    #    way (e.g. once 3.10 is closed as done): silent, nothing to check.
    r, w = _run("| 3.10 | ~~Post the videos~~ | done | 0.2 | **done, "
                "2026-12-01, operator.** |\n",
                {"youtube_published_last_measured": 12,
                 "youtube_published_measured_at": "2026-09-17 01:34"})
    if r or w:
        fails.append("a rewritten row with no bare count was flagged: "
                      "fail=%r warn=%r" % (r, w))

    # 5. The row has moved or changed shape entirely (no 3.10 row at all):
    #    warn, never fail.
    r, w = _run("no such row here\n",
                {"youtube_published_last_measured": 12,
                 "youtube_published_measured_at": "2026-09-17 01:34"})
    if r:
        fails.append("a reshaped file was failed instead of warned: %r" % (r,))
    if not w:
        fails.append("a reshaped file produced no warning at all")

    # 6. The real, committed documents: clean, now that the row has been
    #    corrected in place.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_backlog_h2_video_count_current()
    if preflight.FAIL:
        fails.append("the real committed documents failed: %r"
                     % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_backlog_h2_video_count_current, 6/6 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
