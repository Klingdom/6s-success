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
FAMILIES = ("zones", "rooms", "articles")
LINK = re.compile(r'href="((?:\.\./)*(zones|rooms|articles)/[^"#?]*?\.html)"')
# The same defect written the other way round: a page inside one of those
# directories linking a sibling without naming the directory, e.g. a zone page
# linking "kitchen-the-cooking-zone.html". LINK above keys on the directory
# name, so it never saw these, and the tally at the end of this file printed a
# confident "0 .html" while 1,111 of them sat on 164 pages. Found 2026-09-03.
SIBLING = re.compile(r'href="([a-z0-9][a-z0-9._-]*\.html)"')


def _canonical_is_extensionless(fp: str) -> bool:
    """Never rewrite a link on the strength of which folder it is in.

    The whole point is to make links agree with canonicals, so the target's own
    canonical is the only thing that can authorise the rewrite. A page in these
    folders that declares a .html canonical is left exactly as it is.
    """
    try:
        s = io.open(fp, encoding="utf-8", errors="replace").read()
    except OSError:
        return False
    m = re.search(r'rel="canonical" href="([^"]+)"', s)
    return bool(m) and not m.group(1).endswith(".html")


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

    s = LINK.sub(sub, s)

    if os.path.basename(os.path.dirname(page)) in FAMILIES:
        def sib(m):
            href = m.group(1)
            fp = os.path.join(os.path.dirname(page), href)
            if not os.path.exists(fp) or not _canonical_is_extensionless(fp):
                changed[1] += 1
                return m.group(0)
            changed[0] += 1
            return 'href="%s"' % ("./" if href == "index.html"
                                  else href[: -len(".html")])
        s = SIBLING.sub(sib, s)

    return s, changed


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
    bare = []
    for f in glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True):
        s = io.open(f, encoding="utf-8").read()
        m = re.search(r'rel="canonical" href="([^"]+)"', s)
        if m:
            canon["html" if m.group(1).endswith(".html") else "ext"] += 1
        for h in re.findall(
                r'href="((?:\.\./)*(?:zones|rooms|articles)/[^"#?]*)"', s):
            forms["html" if h.endswith(".html") else "ext"] += 1
        # Same-directory links inside those three families, e.g. a zone page
        # linking a sibling zone as "foo.html" rather than "../zones/foo.html".
        # The tally above cannot see them because it keys on the directory
        # name, so it printed "0 .html" while 114 zone pages each carried
        # sibling links to the address their own canonical disowns. A counter
        # that cannot see a whole shape of the defect it exists to measure is
        # worse than no counter, because it reads as proof.
        fam = os.path.basename(os.path.dirname(f))
        if fam in ("zones", "rooms", "articles"):
            for h in re.findall(r'href="([a-z0-9][a-z0-9._-]*\.html)"', s):
                if os.path.exists(os.path.join(os.path.dirname(f), h)):
                    forms["html"] += 1
                    bare.append(os.path.relpath(f, SITE))
    print(f"  canonicals: {canon['ext']} extensionless, {canon['html']} .html")
    print(f"  internal links: {forms['ext']} extensionless, "
          f"{forms['html']} .html")
    if bare:
        u = sorted(set(bare))
        print(f"  of those, {len(bare)} are same-directory .html links on "
              f"{len(u)} page(s), which this pass does not rewrite: "
              f"{u[:3]}. Emit them as ../<family>/<name>.html instead.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
