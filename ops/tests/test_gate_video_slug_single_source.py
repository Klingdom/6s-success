#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_video_slug_single_source() catches a slug
reimplementation in ops/check_video_standard.py, not only in
ops/render_all_narrated.py.

Found 2026-09-18, cold-reading ops/check_video_standard.py per this
repository's own step 5d. It built its stem with a local regex-based
slug(), the exact single-source-of-truth gap this gate already existed to
catch for two other files, agreeing with video_zone.zone_slug() on all 114
real zones only by coincidence: neither normaliser has ever had to handle
a room or zone name containing "&". Proved directly (not assumed) that the
gate's existing synthetic case, a name with "/", would NOT have caught this
specific file, because a bare "/" collapses to "-" under both the old local
slug() and the canonical one; only an ampersand exposes the divergence. A
real one would have made ops/youtube_upload.py's stale-video hold-back
silently match nothing.

Run:  python ops/tests/test_gate_video_slug_single_source.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    # 1. The real, committed files: clean today.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_video_slug_single_source()
    if preflight.FAIL:
        fails.append("the real committed files failed: %r" % (preflight.FAIL,))

    # 2. Plant the exact pre-fix regression shape: check_video_standard's
    #    stem_for() reimplements slugging locally instead of calling
    #    video_zone.zone_slug(). Patched on the live module object, not the
    #    file on disk, and restored in a finally so this test leaves no
    #    trace either way.
    import check_video_standard as C
    import re as _re
    original_stem_for = C.stem_for

    def buggy_stem_for(room: str, zone: str) -> str:
        return "%s--%s" % (
            _re.sub(r"[^a-z0-9]+", "-", room.lower()).strip("-"),
            _re.sub(r"[^a-z0-9]+", "-", zone.lower()).strip("-"))

    try:
        C.stem_for = buggy_stem_for
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_video_slug_single_source()
        if not preflight.FAIL:
            fails.append("a reintroduced local slug() in "
                          "check_video_standard.py was not caught")
        elif not any("check_video_standard" in m or "ampersand" in m
                     for _g, m in preflight.FAIL):
            fails.append("the gate failed but did not name "
                         "check_video_standard: %r" % (preflight.FAIL,))
    finally:
        C.stem_for = original_stem_for

    # 3. Restoring the real function leaves it clean again.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_video_slug_single_source()
    if preflight.FAIL:
        fails.append("restoring the real stem_for did not leave it "
                     "clean: %r" % (preflight.FAIL,))

    # 4. stem_for() itself: on the real 114-zone corpus, it must equal
    #    video_zone.zone_slug() exactly (not just "the gate says so").
    import video_zone as V
    mismatches = [(room, z["zone"]) for room, z in V.zones()
                  if C.stem_for(room, z["zone"]) != V.zone_slug(room, z["zone"])]
    if mismatches:
        fails.append("stem_for() disagrees with zone_slug() on %d real "
                     "zone(s): %r" % (len(mismatches), mismatches[:3]))

    # 5. The ampersand case that actually distinguishes the two
    #    normalisers, proved directly rather than only through the gate.
    canonical = V.zone_slug("Kids Room", "Coats & Boots")
    checker = C.stem_for("Kids Room", "Coats & Boots")
    if canonical != checker:
        fails.append("stem_for() disagrees with zone_slug() on an "
                     "ampersand name: %r vs %r" % (checker, canonical))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_video_slug_single_source (check_video_standard.py "
          "coverage), 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
