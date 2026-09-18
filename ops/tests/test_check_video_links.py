#!/usr/bin/env python3
"""
Prove ops/check_video_links.py's linked_ids() finds a video ID by every real
way this site names one, not only a literal youtube.com/watch or youtu.be
URL.

Found 2026-09-18, cold-reading this file (0 mentions in ops/NIGHTLY-LOG.md,
never reviewed). Its own claim is "every YouTube video this site links to
must still exist," but the regex only matched a literal watch/youtu.be URL.
The zone pages' actual click-to-play embed uses youtube-nocookie.com/embed/ID
and a data-yt="ID" attribute; the app (quest.js) builds its own watch link at
runtime from a bare "video":"ID" field in quest-data.js, no URL in the source
text. Today all three still resolve to the same 12 IDs the old pattern
already found via each zone page's JSON-LD contentUrl, purely because both
are generated from one file (ops/youtube-published.json); that is an
accident of the current generators, not something this checker enforced.
Proved directly against a planted fixture carrying ONLY the new surfaces, so
each one is checked because the pattern matches it, not because another
literal URL happens to sit nearby in the real files.

Run:  python ops/tests/test_check_video_links.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import check_video_links as C                                  # noqa: E402


def _find(text, name="page.html"):
    """linked_ids() against a single fixture file, real SITE untouched."""
    with tempfile.TemporaryDirectory() as d:
        old_site = C.SITE
        C.SITE = d
        try:
            with open(os.path.join(d, name), "w", encoding="utf-8") as f:
                f.write(text)
            return C.linked_ids()
        finally:
            C.SITE = old_site


def main() -> int:
    fails = []

    # 1. The original literal shapes still work (regression guard).
    ids = _find('<a href="https://www.youtube.com/watch?v=AAAAAAAAAAA">w</a>')
    if "AAAAAAAAAAA" not in ids:
        fails.append("literal youtube.com/watch?v= no longer matched")

    ids = _find('<a href="https://youtu.be/BBBBBBBBBBB">w</a>')
    if "BBBBBBBBBBB" not in ids:
        fails.append("literal youtu.be/ no longer matched")

    # 2. youtube-nocookie.com/embed/ID, the zone pages' real click-to-play
    #    iframe target, with no watch/youtu.be URL anywhere else in the file.
    ids = _find('f.src="https://www.youtube-nocookie.com/embed/CCCCCCCCCCC"'
                '+"?autoplay=1";')
    if "CCCCCCCCCCC" not in ids:
        fails.append("youtube-nocookie.com/embed/ id not matched")

    # 3. Plain youtube.com/embed/ID (no -nocookie), in case a future page
    #    embeds it directly rather than through the click-to-play button.
    ids = _find('<iframe src="https://www.youtube.com/embed/DDDDDDDDDDD">')
    if "DDDDDDDDDDD" not in ids:
        fails.append("youtube.com/embed/ id not matched")

    # 4. data-yt="ID", the attribute the click handler reads, with no URL
    #    of any kind in the same file.
    ids = _find('<button data-yt="EEEEEEEEEEE" aria-label="Play"></button>')
    if "EEEEEEEEEEE" not in ids:
        fails.append("data-yt attribute not matched")

    # 5. "video":"ID", quest-data.js's own bare JSON field, the exact shape
    #    quest.js reads at runtime to build a watch link with no literal URL
    #    anywhere in either file.
    ids = _find('{"zone":"kitchen-x","video":"FFFFFFFFFFF","room":"Kitchen"}',
                name="quest-data.js")
    if "FFFFFFFFFFF" not in ids:
        fails.append('"video":"ID" JSON field not matched')

    # 6. A short, unrelated "video" field (well under a real 11-char id)
    #    must not be swept in under the new {6,} floor by accident.
    ids = _find('{"video":"no"}', name="quest-data.js")
    if ids:
        fails.append("a short non-id \"video\" value was wrongly matched: %r"
                     % (ids,))

    # 7. The real, committed site: every data-yt id and every quest-data.js
    #    "video" id must still resolve, now checked because the pattern
    #    matches that exact surface, not only because the same id also sits
    #    in the page's own JSON-LD contentUrl.
    real = C.linked_ids()
    import re
    site_dir = C.SITE
    data_yt_ids = set()
    for root, _dirs, files in os.walk(site_dir):
        for fn in files:
            if fn.endswith(".html"):
                try:
                    text = open(os.path.join(root, fn), encoding="utf-8").read()
                except OSError:
                    continue
                data_yt_ids.update(re.findall(r'data-yt="([A-Za-z0-9_-]{6,})"',
                                               text))
    missing = data_yt_ids - set(real)
    if missing:
        fails.append("data-yt id(s) on the real site not found by "
                     "linked_ids(): %r" % (missing,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: check_video_links.linked_ids, 7/7 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
