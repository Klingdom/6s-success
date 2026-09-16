#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_goals_published_videos_current() catches
GOALS.md's "Published videos" row disagreeing with either half of what it
claims: the numerator (ops/state-checkin.json's measured count) or the
denominator (the real number of zone metadata files ops/youtube_upload.py
can ever publish from).

Found 2026-09-16: GOALS.md's row read "12 of 228" for six weeks. The
numerator (12) was always right; the denominator was not. 228 is the total
number of rendered video FILES (114 zones, two orientations each), but
ops/youtube_upload.py's own docstring says only the wide 16:9 file is ever
uploaded ("Shorts are a separate distribution decision and are not posted
by this tool"), so the real ceiling is 114, one per zone, matching
MEDIA-OPERATIONS-PLAN.md and OWNER-ACTIONS.md's own "102 of 114 remaining."
The gate itself carried the same "228" as a hardcoded regex literal and so
could never have caught its own denominator being wrong; it is now derived
from build/video/youtube/*.json, the same directory ops/youtube_upload.py's
own jobs() reads from.

Run:  python ops/tests/test_gate_goals_published_videos_current.py
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

GOALS_TEMPLATE = "| Published videos | **%d of %d, measured today** | all of them |\n"


def _run(goals_row, state, meta_count, meta_dir_exists=True):
    tmp = tempfile.mkdtemp()
    try:
        io.open(os.path.join(tmp, "GOALS.md"), "w", encoding="utf-8").write(goals_row)
        os.makedirs(os.path.join(tmp, "ops"))
        io.open(os.path.join(tmp, "ops", "state-checkin.json"), "w",
                encoding="utf-8").write(json.dumps(state))
        if meta_dir_exists:
            meta_dir = os.path.join(tmp, "build", "video", "youtube")
            os.makedirs(meta_dir)
            for i in range(meta_count):
                io.open(os.path.join(meta_dir, "zone-%03d.json" % i), "w",
                        encoding="utf-8").write("{}")
            if meta_count:
                io.open(os.path.join(meta_dir, "playlists.json"), "w",
                        encoding="utf-8").write("{}")
        old_root = preflight.ROOT
        preflight.ROOT = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_goals_published_videos_current()
            return list(preflight.FAIL), list(preflight.WARN)
        finally:
            preflight.ROOT = old_root
    finally:
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. The real regression shape: GOALS.md's denominator (228) disagrees
    #    with the real metadata count (114), numerator matches. Must fail,
    #    naming the drift, not a numerator mismatch.
    r, w = _run(GOALS_TEMPLATE % (12, 228),
                {"youtube_published_last_measured": 12,
                 "youtube_published_measured_at": "2026-09-16"},
                meta_count=114)
    if not r or "goals-published-videos-current" != r[0][0]:
        fails.append("the real denominator-drift shape was not caught: %r" % (r,))
    elif "114" not in r[0][1] or "228" not in r[0][1]:
        fails.append("failure message did not name both the real and "
                      "claimed totals: %r" % (r[0][1],))

    # 2. Numerator disagrees with the measured count, denominator correct:
    #    must still fail, on the original defect shape.
    r, w = _run(GOALS_TEMPLATE % (5, 114),
                {"youtube_published_last_measured": 12,
                 "youtube_published_measured_at": "2026-09-16"},
                meta_count=114)
    if not r or "goals-published-videos-current" != r[0][0]:
        fails.append("a numerator mismatch against the real denominator "
                      "was not caught: %r" % (r,))

    # 3. Both agree with reality: no failure.
    r, w = _run(GOALS_TEMPLATE % (12, 114),
                {"youtube_published_last_measured": 12,
                 "youtube_published_measured_at": "2026-09-16"},
                meta_count=114)
    if r:
        fails.append("genuine agreement with reality wrongly flagged: %r" % (r,))

    # 4. state-checkin.json has no measurement yet: silent, no fail/warn.
    r, w = _run(GOALS_TEMPLATE % (0, 114), {}, meta_count=114)
    if r or w:
        fails.append("an unmeasured state-checkin.json was flagged instead "
                      "of silently skipped: fail=%r warn=%r" % (r, w))

    # 5. build/video/youtube/ missing entirely: warn, never a silent pass
    #    and never a fail (this environment may not have it).
    r, w = _run(GOALS_TEMPLATE % (12, 114),
                {"youtube_published_last_measured": 12,
                 "youtube_published_measured_at": "2026-09-16"},
                meta_count=0, meta_dir_exists=False)
    if r:
        fails.append("a missing metadata directory was failed instead of "
                      "warned: %r" % (r,))
    if not w:
        fails.append("a missing metadata directory produced no warning at all")

    # 6. GOALS.md's row has changed shape entirely: warn, never fail.
    r, w = _run("no such row here\n",
                {"youtube_published_last_measured": 12,
                 "youtube_published_measured_at": "2026-09-16"},
                meta_count=114)
    if r:
        fails.append("a reshaped row was failed instead of warned: %r" % (r,))
    if not w:
        fails.append("a reshaped row produced no warning at all")

    # 7. The real, committed documents: clean, now that GOALS.md has been
    #    corrected in place to 114 and the gate derives 114 itself.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_goals_published_videos_current()
    if preflight.FAIL:
        fails.append("the real committed documents failed: %r"
                     % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_goals_published_videos_current, 7/7 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
