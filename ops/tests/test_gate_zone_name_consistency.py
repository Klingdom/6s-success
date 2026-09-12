#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_zone_name_consistency() catches both real
defect shapes found 2026-09-12: a zone page's own HowTo schema saying
"reset the The X" (113 of 114 real pages did, before the fix), and a
build/video/youtube/*.json whose title or description names a zone by its
raw internal key instead of the real site name a viewer would see on the
linked page.

Run:  python ops/tests/test_gate_zone_name_consistency.py
"""
import glob
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import build_zone_pages as bz                                  # noqa: E402
import video_zone                                               # noqa: E402

CLEAN_PAGE = (
    '<script type="application/ld+json">{"@type": "HowTo", '
    '"name": "How to reset The Landing Spot in the Entryway"}</script>'
)

REGRESSED_PAGE = (
    '<script type="application/ld+json">{"@type": "HowTo", '
    '"name": "How to reset the The Landing Spot in the Entryway"}</script>'
)

ROOM, ZONE = "Entryway", "Landing Zone"
SLUG = video_zone.zone_slug(ROOM, ZONE)
REAL_TITLE = bz.zone_seo_title(ROOM, ZONE)
REAL_NAME = bz.display(ROOM, ZONE)


def _run(pages: dict = None, yt_files: dict = None):
    tmp = tempfile.mkdtemp()
    try:
        zones_dir = os.path.join(tmp, "site", "zones")
        os.makedirs(zones_dir)
        for name, body in (pages or {}).items():
            io.open(os.path.join(zones_dir, name), "w", encoding="utf-8").write(body)

        yt_dir = os.path.join(tmp, "build", "video", "youtube")
        if yt_files is not None:
            os.makedirs(yt_dir)
            for name, meta in yt_files.items():
                io.open(os.path.join(yt_dir, name), "w", encoding="utf-8").write(
                    json.dumps(meta))

        old_root, old_site = preflight.ROOT, preflight.SITE
        preflight.ROOT = tmp
        preflight.SITE = os.path.join(tmp, "site")
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_zone_name_consistency()
            return list(preflight.FAIL), list(preflight.WARN)
        finally:
            preflight.ROOT, preflight.SITE = old_root, old_site
    finally:
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. A clean page, no youtube metadata directory at all: warns, not fails.
    f, w = _run(pages={"clean.html": CLEAN_PAGE}, yt_files=None)
    if f:
        fails.append("clean page with no yt dir wrongly FAILed: %r" % (f,))
    if not w:
        fails.append("missing yt dir should warn, warned nothing")

    # 2. The double-article regression: caught by name.
    f, _ = _run(pages={"regressed.html": REGRESSED_PAGE}, yt_files={})
    if not f or "regressed.html" not in f[0][1]:
        fails.append("double-article regression not caught: %r" % (f,))

    # 3. A clean page plus correct YouTube metadata: no failure.
    good_meta = {"title": REAL_TITLE,
                 "description": "This is %s in the Entryway." % REAL_NAME}
    f, _ = _run(pages={"clean.html": CLEAN_PAGE}, yt_files={SLUG + ".json": good_meta})
    if f:
        fails.append("correct metadata wrongly flagged: %r" % (f,))

    # 4. YouTube metadata with the raw-internal-key title regression: caught.
    bad_title_meta = {"title": "How to organize the %s | %s" % (ZONE.lower(), ROOM),
                       "description": "This is %s in the Entryway." % REAL_NAME}
    f, _ = _run(pages={"clean.html": CLEAN_PAGE},
                yt_files={SLUG + ".json": bad_title_meta})
    if not f or not any(SLUG in msg for _, msg in f):
        fails.append("stale-title regression not caught: %r" % (f,))

    # 5. YouTube metadata whose description never names the real display
    #    name at all: caught.
    bad_desc_meta = {"title": REAL_TITLE,
                      "description": "This is %s in the Entryway." % ZONE}
    f, _ = _run(pages={"clean.html": CLEAN_PAGE},
                yt_files={SLUG + ".json": bad_desc_meta})
    if not f or not any(SLUG in msg for _, msg in f):
        fails.append("stale-description regression not caught: %r" % (f,))

    # 6. The real, committed site: clean on every one of the 114 zone pages.
    real_pages = sorted(glob.glob(os.path.join(ROOT, "site", "zones", "*.html")))
    real_yt = sorted(glob.glob(os.path.join(ROOT, "build", "video", "youtube", "*.json")))
    if len(real_pages) < 100:
        print("  (skipped: fewer than 100 real zone pages found on disk)")
    else:
        old_fail, old_warn = preflight.FAIL, preflight.WARN
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_zone_name_consistency()
            if preflight.FAIL:
                fails.append("real committed site FAILed: %r" % (preflight.FAIL,))
        finally:
            preflight.FAIL, preflight.WARN = old_fail, old_warn
    if len(real_yt) < 100:
        print("  (real build/video/youtube/*.json not present or incomplete "
              "in this environment; case 6 only checked page-side)")

    if fails:
        print("FAIL")
        for f_ in fails:
            print("  - " + f_)
        return 1
    print("PASS (%d cases)" % 6)
    return 0


if __name__ == "__main__":
    sys.exit(main())
