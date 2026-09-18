#!/usr/bin/env python3
"""
Every YouTube video this site links to must still exist.

WHY
---
12 zone pages send a reader to a published video. Nothing checked that those
videos are still there, and one decision now on the table makes that a live
risk rather than a theoretical one: the same 12 videos show a checklist their
own zone page no longer agrees with (ops/check_video_standard.py), so replacing
them with corrected re-renders is a reasonable choice. YouTube cannot swap the
file behind an existing URL, so replacing means NEW urls, and the moment the
old ones are deleted every link here dead-ends with nothing to notice it.

A dead outbound link on the page a search engine already ranks is the cheap,
stupid kind of trust damage this project has paid for before.

HOW
---
YouTube's oEmbed endpoint answers 200 for a video anybody can watch and 401 or
404 for one that is deleted, private or unlisted. That is a real availability
test, unlike fetching the watch page, which returns 200 with "Video
unavailable" in the body.

Needs egress. Without it this says UNCHECKED and exits 0, because "could not
look" and "all fine" are different claims.

    python ops/check_video_links.py
"""
from __future__ import annotations

import glob
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
ID = re.compile(r"(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{6,})")
OEMBED = ("https://www.youtube.com/oembed?url="
          "https://www.youtube.com/watch%3Fv%3D{}&format=json")


def linked_ids() -> dict:
    """{video id: [files that link it]}, from what the site actually ships."""
    found = {}
    pats = ["**/*.html", "**/*.js", "**/*.json"]
    for pat in pats:
        for f in glob.glob(os.path.join(SITE, pat), recursive=True):
            try:
                text = io.open(f, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for vid in set(ID.findall(text)):
                found.setdefault(vid, []).append(os.path.relpath(f, ROOT))
    return found


def available(vid: str, timeout: int = 15):
    """(ok, detail). None for ok means the check could not run at all."""
    req = urllib.request.Request(
        OEMBED.format(vid),
        headers={"User-Agent": "6s-success-link-check/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = json.loads(r.read().decode("utf-8", "replace"))
            return True, body.get("title", "")[:60]
    except urllib.error.HTTPError as e:
        return False, "HTTP %s" % e.code
    except Exception as e:                                      # noqa: BLE001
        return None, "%s: %s" % (type(e).__name__, str(e)[:60])


def main() -> int:
    ids = linked_ids()
    if not ids:
        print("  no YouTube links on this site")
        return 0
    print("  video links found   %d" % len(ids))
    ok, dead, unchecked = [], [], []
    for vid in sorted(ids):
        good, detail = available(vid)
        if good is True:
            ok.append(vid)
        elif good is False:
            dead.append((vid, detail, ids[vid]))
        else:
            unchecked.append((vid, detail))
    print("  available           %d" % len(ok))
    if unchecked:
        print("  UNCHECKED           %d (%s), so this run proves nothing about them"
              % (len(unchecked), unchecked[0][1]))
    for vid, detail, files in dead:
        print("  DEAD  %s  %s  linked from %s"
              % (vid, detail, ", ".join(files[:3])))
    if dead:
        print("\n  A reader on those pages clicks through to nothing. Fix the "
              "link or remove it.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
