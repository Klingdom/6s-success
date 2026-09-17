#!/usr/bin/env python3
"""
Rewrite ops/hero-fallback.json from the zone pages as they are actually wired.

WHY THIS EXISTS
---------------
hero-fallback.json is the committed record of each zone page's hero figure,
used two ways:

  1. wire_zone_heroes.fallback_wire() restores the figure where the source
     photographs are absent, which is every CI checkout (build/heroes/ is
     gitignored).
  2. build_quest.py treats it as the PUBLISHED set: a picture only reaches the
     Home Quest app if it appears here, so an approved hero that never made it
     into this file is invisible to the app.

It was written once, by hand, when the gate that needs it was added, and
nothing has updated it since. On 2026-09-17 five newly approved zone heroes
went live on their pages while four of them stayed out of this file, so the
app kept showing "no picture" for zones whose picture was already on the web.
Its stored figure HTML also predates AVIF, so a restore would have quietly
served the heavier WebP.

This regenerates the record FROM THE PAGES, which are the thing that ships.
It never invents an entry: a page with no wired figure is simply absent, the
same meaning the file already carries.

    python ops/refresh_hero_fallback.py --check    report drift, write nothing
    python ops/refresh_hero_fallback.py --apply
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZONES = os.path.join(ROOT, "site", "zones")
OUT = os.path.join(ROOT, "ops", "hero-fallback.json")
BASE = "https://6s-success.com"

FIGURE = re.compile(
    r'\n<figure class="zone-hero" id="zone-hero">.*?</figure>\n', re.S)
OG = re.compile(r'<meta property="og:image" content="([^"]+)"')
TW = re.compile(r'<meta name="twitter:image" content="([^"]+)"')
STEM = re.compile(r'assets/zones/([a-z0-9-]+)-(?:sm|md|lg)\.(?:avif|webp|jpg)')


def build() -> dict:
    out = {}
    for path in sorted(os.listdir(ZONES)):
        if not path.endswith(".html") or path == "index.html":
            continue
        text = io.open(os.path.join(ZONES, path), encoding="utf-8").read()
        fig = FIGURE.search(text)
        if not fig:
            continue
        stem = STEM.search(fig.group(0))
        if not stem:
            continue
        og, tw = OG.search(text), TW.search(text)
        entry = {"figure_html": fig.group(0), "stem": stem.group(1)}
        # Only record a preview URL that actually points at this zone's own
        # image. A page falling back to the generic room map advertises that
        # map, and copying it in here would make the record claim a hero the
        # page does not have.
        for key, m in (("og_image", og), ("twitter_image", tw)):
            if m and "/assets/zones/" in m.group(1):
                entry[key] = m.group(1)
        out[path] = entry
    return dict(sorted(out.items()))


def main() -> int:
    fresh = build()
    old = json.load(io.open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    added = sorted(set(fresh) - set(old))
    dropped = sorted(set(old) - set(fresh))
    changed = sorted(k for k in set(fresh) & set(old) if fresh[k] != old[k])
    print("  pages with a wired hero  %d" % len(fresh))
    print("  new to the record        %d %s" % (len(added), added[:4]))
    print("  no longer wired          %d %s" % (len(dropped), dropped[:4]))
    print("  figure or preview moved  %d" % len(changed))
    if "--apply" not in sys.argv:
        print("\n  --check only, nothing written")
        return 0
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(
        json.dumps(fresh, indent=1, ensure_ascii=False) + "\n")
    print("  wrote %s" % os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
