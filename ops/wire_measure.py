#!/usr/bin/env python3
"""
Load the funnel instrumentation on every page, after the analytics tag.

ORDER MATTERS. measure.js queues events until window.umami exists, so it is
tolerant of loading first, but loading it after the tracker means the queue is
almost always empty and the first click on a page is recorded rather than held.

Idempotent. Run after any builder, then run ops/fingerprint_assets.py.
"""
from __future__ import annotations

import glob
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

MARK, END = "<!-- MEASURE:BEGIN -->", "<!-- MEASURE:END -->"
TAG = 'data-website-id="f1fc5160-4473-422d-a89e-73ff6cbdca7a"'


def main() -> int:
    n = skipped = 0
    for f in sorted(glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(f, SITE).replace(os.sep, "/")
        # Downloads and the print-and-play deck are artifacts a buyer opens from
        # their own disk. They must not reach for site assets or phone home.
        if rel.startswith("downloads/") or rel.startswith("deck/"):
            continue

        s = io.open(f, encoding="utf-8").read()
        if TAG not in s:
            # No analytics tag means nothing to measure with. The page audit
            # already flags those; silently adding a measurer would hide it.
            skipped += 1
            continue

        pre = "../" * rel.count("/")
        block = (MARK + f'\n<script defer src="{pre}assets/js/measure.js"></script>\n'
                 + END)

        if MARK in s:
            s2 = re.sub(re.escape(MARK) + r".*?" + re.escape(END), block, s, flags=re.S)
        else:
            # Immediately after the analytics tag, so the tracker is already
            # requested when this parses.
            i = s.find(TAG)
            j = s.find("</script>", i)
            if j < 0:
                skipped += 1
                continue
            j += len("</script>")
            s2 = s[:j] + "\n" + block + s[j:]

        if s2 != s:
            io.open(f, "w", encoding="utf-8", newline="").write(s2)
        n += 1

    print(f"  measure.js on {n} pages, {skipped} skipped")

    # A script tag pointing at nothing is worse than no instrumentation: the
    # console fills with 404s and the next person assumes analytics is broken.
    for f in glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True):
        s = io.open(f, encoding="utf-8").read()
        for m in re.finditer(r'src="((?:\.\./)*assets/js/measure\.js)"', s):
            target = os.path.normpath(os.path.join(os.path.dirname(f), m.group(1)))
            assert os.path.exists(target), \
                f"{os.path.relpath(f, ROOT)} loads {m.group(1)}, which is not there"
    print("  every measure.js path checked, all resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
