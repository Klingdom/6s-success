#!/usr/bin/env python3
"""
ops/render_stale_narrated.py must never reimplement check_video_standard.py's
own stale/fresh judgement (the exact single-source-of-truth gap this corpus
has hit three times already: video_narrated.py's dead slug fallback,
render_all_narrated.py's own copy, and check_video_standard.py's own first
draft). It must also never claim success from a subprocess's exit code alone:
a renderer that returns 0 while the real .srt still disagrees with the
standard is not a fix.

Run:  python ops/tests/test_render_stale_narrated.py
"""
import io
import os
import subprocess
import sys
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import render_stale_narrated as R                                 # noqa: E402
import check_video_standard as cvs                                # noqa: E402
import video_zone as vz                                           # noqa: E402


FAKE_ZONES = [
    ("Entryway", {"zone": "The Landing Spot"}),
    ("Kitchen", {"zone": "The Cooking Zone"}),
]


def _run_quiet(fn, *a, **kw):
    captured = io.StringIO()
    old = sys.stdout
    sys.stdout = captured
    try:
        rc = fn(*a, **kw)
    finally:
        sys.stdout = old
    return rc, captured.getvalue()


def case_stale_pairs_uses_check_video_standard_compare() -> list[str]:
    """stale_pairs() must ask check_video_standard.compare() which zones are
    stale, never re-derive its own notion of staleness."""
    fails = []
    fake_stale = [("entryway--the-landing-spot", ["x"], ["MISSING: x"])]
    with patch.object(cvs, "compare", return_value=(fake_stale, [], [])), \
         patch.object(vz, "zones", return_value=FAKE_ZONES):
        pairs = R.stale_pairs()
    if pairs != [("entryway--the-landing-spot", "Entryway", "The Landing Spot")]:
        fails.append("stale_pairs() did not map compare()'s stale stem back "
                     "to the real (room, zone) pair via video_zone.zones(): "
                     "got %r" % (pairs,))
    return fails


def case_stale_pairs_ignores_a_stem_not_in_the_real_corpus() -> list[str]:
    """A stem compare() names that no longer exists in video_zone.zones()
    (e.g. a zone renamed since the .srt was last read) must be skipped, not
    crash the whole batch."""
    fails = []
    fake_stale = [("not-a-real-zone--anywhere", ["x"], ["MISSING: x"]),
                  ("kitchen--the-cooking-zone", ["x"], ["MISSING: x"])]
    with patch.object(cvs, "compare", return_value=(fake_stale, [], [])), \
         patch.object(vz, "zones", return_value=FAKE_ZONES):
        pairs = R.stale_pairs()
    if pairs != [("kitchen--the-cooking-zone", "Kitchen", "The Cooking Zone")]:
        fails.append("an unmatched stem was not safely skipped: got %r" % (pairs,))
    return fails


def case_check_mode_reports_without_rendering() -> list[str]:
    """--check must report the stale count and exit 1 without ever calling
    subprocess.run (no render spawned just to look)."""
    fails = []
    fake_stale = [("entryway--the-landing-spot", ["x"], ["MISSING: x"])]
    old_argv = sys.argv
    try:
        sys.argv = ["render_stale_narrated.py", "--check"]
        with patch.object(cvs, "compare", return_value=(fake_stale, [], [])), \
             patch.object(vz, "zones", return_value=FAKE_ZONES), \
             patch.object(subprocess, "run") as mock_run:
            rc, out = _run_quiet(R.main)
    finally:
        sys.argv = old_argv
    if rc != 1:
        fails.append("--check with one stale pair must exit 1, got %r" % rc)
    if "entryway--the-landing-spot" not in out:
        fails.append("--check must name the stale stem, got: %r" % out)
    if mock_run.called:
        fails.append("--check must never spawn a render subprocess")
    return fails


def case_check_mode_clean_exits_zero() -> list[str]:
    fails = []
    old_argv = sys.argv
    try:
        sys.argv = ["render_stale_narrated.py", "--check"]
        with patch.object(cvs, "compare", return_value=([], [], [])):
            rc, out = _run_quiet(R.main)
    finally:
        sys.argv = old_argv
    if rc != 0:
        fails.append("--check with nothing stale must exit 0, got %r" % rc)
    return fails


def case_render_calls_both_orientations_per_pair() -> list[str]:
    """A real run must invoke video_narrated.py once for the wide frame and
    once for the vertical frame per stale pair, since both captions come
    from the same (now stale) done_items() text."""
    fails = []
    fake_stale = [("entryway--the-landing-spot", ["x"], ["MISSING: x"])]
    old_argv = sys.argv
    try:
        sys.argv = ["render_stale_narrated.py"]
        with patch.object(cvs, "compare", return_value=(fake_stale, [], [])), \
             patch.object(vz, "zones", return_value=FAKE_ZONES), \
             patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout="", stderr="")
            # Still stale on re-check (the mocked subprocess never actually
            # fixed anything), so this also proves case below separately.
            rc, out = _run_quiet(R.main)
    finally:
        sys.argv = old_argv
    calls = [c.args[0] for c in mock_run.call_args_list]
    if len(calls) != 2:
        fails.append("expected exactly 2 subprocess calls (wide + vertical) "
                     "for one stale pair, got %d: %r" % (len(calls), calls))
    wide_calls = [c for c in calls if "--wide" in c]
    plain_calls = [c for c in calls if "--wide" not in c]
    if len(wide_calls) != 1 or len(plain_calls) != 1:
        fails.append("expected one --wide call and one plain call, got %r" % (calls,))
    for c in calls:
        if "--zone" not in c or "The Landing Spot" not in c:
            fails.append("render call missing --zone The Landing Spot: %r" % (c,))
        if "--room" not in c or "Entryway" not in c:
            fails.append("render call missing --room Entryway: %r" % (c,))
    return fails


def case_real_run_distrusts_a_green_exit_code() -> list[str]:
    """A subprocess that exits 0 is not proof the SRT now matches the
    standard. main() must re-run compare() after rendering and fail if the
    pair is still stale, exactly the "green exit code is not proof" shape
    CLAUDE.md names directly."""
    fails = []
    fake_stale = [("entryway--the-landing-spot", ["x"], ["MISSING: x"])]
    old_argv = sys.argv
    try:
        sys.argv = ["render_stale_narrated.py"]
        with patch.object(cvs, "compare", return_value=(fake_stale, [], [])), \
             patch.object(vz, "zones", return_value=FAKE_ZONES), \
             patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout="", stderr="")
            rc, out = _run_quiet(R.main)
    finally:
        sys.argv = old_argv
    if rc == 0:
        fails.append("main() returned 0 after every subprocess exited 0, "
                     "even though compare() still reports the pair stale "
                     "afterwards; a 0 exit code from ffmpeg/edge-tts is not "
                     "proof the caption text actually changed")
    if "still stale after render" not in out:
        fails.append("main() did not say the pair was still stale after "
                     "rendering, got: %r" % out)
    return fails


def main() -> int:
    cases = [
        case_stale_pairs_uses_check_video_standard_compare,
        case_stale_pairs_ignores_a_stem_not_in_the_real_corpus,
        case_check_mode_reports_without_rendering,
        case_check_mode_clean_exits_zero,
        case_render_calls_both_orientations_per_pair,
        case_real_run_distrusts_a_green_exit_code,
    ]
    fails = []
    for c in cases:
        fails.extend(c())
    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {len(cases) - len(fails)} of {len(cases)} cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
