#!/usr/bin/env python3
"""
Link to the URL the site says is canonical.

THE SPLIT
---------
166 pages declare an extensionless canonical, and internal links point at the
.html form 2,704 times against 499 extensionless. So the site tells a crawler
"the real address of this page has no extension" and then, on every page,
links the other one. Both forms return 200, because nginx's try_files serves
either, so nothing breaks and nothing complains.

What it costs: a crawler follows 2,704 links to addresses the site itself
disowns, every one of which then has to be reconciled against a canonical
pointing somewhere else. Analytics is worse, because Umami stores the path
verbatim, so an organic visitor landing on /zones/foo and an internal visitor
arriving at /zones/foo.html are two different rows for the same page. Every
per-page number is split by an arbitrary ratio.

WHAT IT DOES
------------
Rewrites internal links to zones, rooms and articles into the extensionless
form, and directory index links into a trailing slash. Only where the target
file actually exists, so a typo in a generator becomes a link this pass
declines to touch rather than one it silently rewrites into a new shape.

Nothing else moves: downloads keep their extensions because they are files,
and top-level pages keep theirs because their own canonicals say .html.
Making those consistent is a separate decision with a different blast radius.

Run:  python ops/canonical_links.py
      python ops/canonical_links.py --check
"""
from __future__ import annotations

import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

# Only the three generated page families whose canonicals are extensionless.
LINK = re.compile(r'href="((?:\.\./)*(zones|rooms|articles)/[^"#?]*?\.html)"')


def target_exists(page: str, href: str) -> bool:
    return os.path.exists(os.path.normpath(
        os.path.join(os.path.dirname(page), href)))


def rewrite(page: str, s: str) -> tuple:
    changed = [0, 0]

    def sub(m):
        href = m.group(1)
        if not target_exists(page, href):
            changed[1] += 1
            return m.group(0)          # leave a broken link exactly as it is
        if href.endswith("/index.html"):
            new = href[: -len("index.html")]
        else:
            new = href[: -len(".html")]
        changed[0] += 1
        return 'href="%s"' % new

    return LINK.sub(sub, s), changed


def main() -> int:
    check = "--check" in sys.argv
    total, skipped, pages = 0, 0, 0
    for f in sorted(glob.glob(os.path.join(SITE, "**", "*.html"),
                              recursive=True)):
        rel = os.path.relpath(f, SITE)
        if rel.startswith(("downloads" + os.sep, "deck" + os.sep)):
            continue
        s = io.open(f, encoding="utf-8").read()
        new, (n, miss) = rewrite(f, s)
        total += n
        skipped += miss
        if new != s:
            pages += 1
            if not check:
                io.open(f, "w", encoding="utf-8", newline="").write(new)

    print(f"  {'would rewrite' if check else 'rewrote'} {total} internal "
          f"link(s) across {pages} page(s) to the canonical form")
    if skipped:
        print(f"  left {skipped} link(s) alone because the target file does "
              f"not exist, which is a broken link this pass will not disguise")

    # Say what the site now looks like, both halves, because the whole defect
    # was that these two numbers disagreed and nobody printed them together.
    canon = {"ext": 0, "html": 0}
    forms = {"ext": 0, "html": 0}
    for f in glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True):
        s = io.open(f, encoding="utf-8").read()
        m = re.search(r'rel="canonical" href="([^"]+)"', s)
        if m:
            canon["html" if m.group(1).endswith(".html") else "ext"] += 1
        for h in re.findall(
                r'href="((?:\.\./)*(?:zones|rooms|articles)/[^"#?]*)"', s):
            forms["html" if h.endswith(".html") else "ext"] += 1
    print(f"  canonicals: {canon['ext']} extensionless, {canon['html']} .html")
    print(f"  internal links: {forms['ext']} extensionless, "
          f"{forms['html']} .html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
