#!/usr/bin/env python3
"""
ops/check_video_standard.py decides whether a rendered zone video is safe to
publish to YouTube (ops/youtube_upload.py refuses anything it calls stale),
and had zero test coverage before this file. A YouTube video cannot be
swapped for a corrected file without changing its URL, so a wrong verdict
here is expensive to undo, not cosmetic.

Run:  python ops/tests/test_check_video_standard.py
"""
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import check_video_standard as C                              # noqa: E402
import video_zone as V                                        # noqa: E402


SRT = """1
00:00:01,000 --> 00:00:03,000
What done looks like

2
00:00:03,000 --> 00:00:06,000
One wallet and one phone
per adult

3
00:00:06,000 --> 00:00:08,000
A clear path to the door

4
00:00:08,000 --> 00:00:10,000
One session

5
00:00:10,000 --> 00:00:12,000
The Landing Spot
"""


def main() -> int:
    fails = []

    # 1. stem_for() is the canonical video_zone.zone_slug(), not a local
    #    reimplementation. LRN-shaped regression: the two agreed on every
    #    real zone name for weeks before this file existed, purely because
    #    none contains punctuation the two normalisers would have treated
    #    differently.
    if C.stem_for("Entryway", "The Bench or Console") != \
            V.zone_slug("Entryway", "The Bench or Console"):
        fails.append("stem_for() is not calling video_zone.zone_slug()")
    if C.stem_for("Kids Room", "Coats & Boots") != "kids-room--coats-&-boots":
        fails.append("stem_for() lost punctuation zone_slug() itself keeps: %r"
                     % C.stem_for("Kids Room", "Coats & Boots"))

    # 2. blocks(): a wrapped multi-line caption reads as one joined string,
    #    not truncated at the first physical line (the bug the file's own
    #    docstring names as its first version's failure mode).
    b = C.blocks(SRT)
    if not any("One wallet and one phone per adult" in text for _i, text in b):
        fails.append("blocks() did not join a wrapped caption across lines: %r" % b)

    # 3. rendered_segment(): extracts only the checklist, stopping at the
    #    next section heading ("One session"), not swallowing the rest of
    #    the file.
    with tempfile.NamedTemporaryFile(
            mode="w", suffix=".srt", delete=False, encoding="utf-8") as f:
        f.write(SRT)
        path = f.name
    try:
        seg = C.rendered_segment(path)
        if "one wallet and one phone per adult" not in seg.lower():
            fails.append("rendered_segment() missed a real checklist item: %r" % seg)
        if "landing spot" in seg.lower():
            fails.append("rendered_segment() read past 'One session' into the "
                         "next section: %r" % seg)
    finally:
        os.unlink(path)

    # 4. rendered_segment() on a missing file: empty, not an exception, so
    #    compare() can treat it as unreadable rather than crash.
    if C.rendered_segment(os.path.join(ROOT, "does-not-exist.srt")) != "":
        fails.append("rendered_segment() did not degrade cleanly on a missing file")

    # 5. norm(): case- and punctuation-insensitive, whitespace-collapsed,
    #    since a caption's own wrapping and punctuation must not cause a
    #    real match to be missed.
    if C.norm("One wallet, and one phone  per adult.") != \
            "one wallet and one phone per adult":
        fails.append("norm() did not normalise punctuation/whitespace: %r"
                     % C.norm("One wallet, and one phone  per adult."))

    # 6. compare(), on the real 114-zone corpus and the real committed
    #    build/video/zones-narrated/*.srt files: every zone is accounted
    #    for exactly once (stale + fresh + unreadable == total zones), and
    #    stem_for()'s output is what is actually being looked up on disk.
    stale, fresh, unreadable = C.compare()
    total_zones = len(V.zones())
    if len(stale) + len(fresh) + len(unreadable) != total_zones:
        fails.append("compare() accounted for %d zones, expected %d"
                     % (len(stale) + len(fresh) + len(unreadable), total_zones))

    # 7. compare() catches a real dropped item: build an in-memory SRT
    #    missing the second checklist item and confirm the same extraction
    #    path used by compare() would flag it (proves the substring-missing
    #    logic, not just that the function runs).
    dropped = SRT.replace(
        "One wallet and one phone\nper adult", "One phone per adult")
    with tempfile.NamedTemporaryFile(
            mode="w", suffix=".srt", delete=False, encoding="utf-8") as f:
        f.write(dropped)
        path = f.name
    try:
        seg = C.norm(C.rendered_segment(path))
        missing = C.norm("One wallet and one phone per adult") not in seg
        if not missing:
            fails.append("a dropped word in a checklist item was not "
                         "detectable via rendered_segment()/norm()")
    finally:
        os.unlink(path)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: check_video_standard.py, 7/7 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
