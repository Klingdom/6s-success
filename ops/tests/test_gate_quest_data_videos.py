#!/usr/bin/env python3
"""
Prove gate_quest_data_videos_published() only lets the app offer a zone video
that is genuinely published.

Added 2026-09-16 with the app's "Watch this zone" link. Twelve zone videos are
live on YouTube; ops/youtube-published.json is the record of which, and
ops/build_quest.py copies those ids into site/assets/js/quest-data.js. A link
to an unpublished or mistyped id looks exactly like a working one until it is
pressed, inside the surface somebody is actually working in.

Run:  python ops/tests/test_gate_quest_data_videos.py
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

ALLOWED = {"entryway--landing-zone": "HJ2Uy0kSXkM",
           "kitchen--primary-prep-counter": "EGcVpRA27zA"}


def main() -> int:
    fails = []

    # 1. The published id for its own zone: never flagged.
    ok = {"rooms": [{"zones": [{"zone": "Landing Zone",
                                 "img": "entryway--landing-zone",
                                 "video": "HJ2Uy0kSXkM"}]}]}
    bad = preflight.quest_data_unpublished_videos(ok, ALLOWED)
    if bad:
        fails.append("a published id was wrongly flagged: %r" % bad)

    # 2. A zone whose video was never published at all.
    never = {"rooms": [{"zones": [{"zone": "Sock Drawer",
                                    "img": "bedroom--sock-drawer",
                                    "video": "AAAAAAAAAAA"}]}]}
    bad2 = preflight.quest_data_unpublished_videos(never, ALLOWED)
    if "AAAAAAAAAAA" not in bad2:
        fails.append("an unpublished id was not caught: %r" % bad2)

    # 3. A real zone carrying somebody else's id (a mistyped or stale copy).
    swapped = {"rooms": [{"zones": [{"zone": "Landing Zone",
                                      "img": "entryway--landing-zone",
                                      "video": "EGcVpRA27zA"}]}]}
    bad3 = preflight.quest_data_unpublished_videos(swapped, ALLOWED)
    if "EGcVpRA27zA" not in bad3:
        fails.append("a zone carrying another zone's id was not caught: %r" % bad3)
    elif "published id for it" not in bad3["EGcVpRA27zA"]:
        fails.append("the mismatch was reported as unpublished rather than wrong: %r" % bad3)

    # 4. A zone with a video but no approved picture is matched by name, which
    # is the real case: kitchen--primary-prep-counter has a published video and
    # no picture, because its hero verdict was withdrawn.
    nopic = {"rooms": [{"zones": [{"zone": "Primary Prep Counter",
                                    "video": "EGcVpRA27zA"}]}]}
    bad4 = preflight.quest_data_unpublished_videos(nopic, ALLOWED)
    if bad4:
        fails.append("a zone with a video and no picture was wrongly flagged: %r" % bad4)

    # 5. Zones with no video at all: nothing to check, never flagged.
    none = {"rooms": [{"zones": [{"zone": "Quiet Zone", "img": "x--quiet-zone"}]}]}
    if preflight.quest_data_unpublished_videos(none, ALLOWED):
        fails.append("a zone with no video was flagged")

    # 6. The real committed payload against the real publishing record.
    data_path = os.path.join(ROOT, "site", "assets", "js", "quest-data.js")
    pub_path = os.path.join(ROOT, "ops", "youtube-published.json")
    if os.path.exists(data_path) and os.path.exists(pub_path):
        js = io.open(data_path, encoding="utf-8").read()
        data = json.loads(js[js.index("{"):js.rindex(";")])
        allowed = {stem: rec["video_id"] for stem, rec
                   in json.load(io.open(pub_path, encoding="utf-8")).items()
                   if isinstance(rec, dict) and rec.get("video_id")}
        real = preflight.quest_data_unpublished_videos(data, allowed)
        if real:
            fails.append("the committed quest-data.js offers %d unpublished video(s): %r"
                         % (len(real), list(real.values())[:2]))
        shipped = sum(1 for r in data.get("rooms", []) for z in r.get("zones", []) if z.get("video"))
        if shipped != len(allowed):
            fails.append("quest-data.js carries %d video(s) against %d published"
                         % (shipped, len(allowed)))
    else:
        fails.append("quest-data.js or youtube-published.json is missing, so the "
                     "real payload was NOT checked")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: quest data videos, published ids pass, unpublished and mismatched "
          "ids caught, picture-less zones matched by name, real payload clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
