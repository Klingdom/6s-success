#!/usr/bin/env python3
"""
Measure the internal link graph among the site's content pages.

WHY THIS EXISTS
---------------
The site is 174 pages, 114 of them zone pages and 20 room pages. "Is the link
graph actually connected" is not a question anyone can eyeball at that size,
and guessing has already been wrong once this session: ops/build_resources.py
was, until this pass, silently regenerating site/resources.html WITHOUT any
link to the 20 room pages or the 114 zone pages at all, even though the live,
committed copy of that file had every one of those links. Nobody would catch
that by reading the generator's docstring. This script exists so the claim
"the graph is connected" is measured, not assumed, every time a generator
changes.

WHAT IT COUNTS
--------------
Only links found in <main>...</main> (or, failing that, the page body with
<header> and <footer> stripped). The primary nav and footer are byte-identical
on every page and link only to hub pages (resources.html, method.html,
shop.html, and so on), never to an individual zone or room, so counting them
would not change any zone or room's inbound count and would just inflate the
hub pages' numbers without telling us anything new. Stripping them keeps the
count to links an editor actually placed on that specific page.

WHAT IT DOES NOT DO
--------------------
It does not fix anything. It reports orphans and thin spots so a human or
another pass can decide what, if anything, should link to them. Wiring 114
zone pages to new content programmatically without a real reason for each
link is exactly the kind of thing CLAUDE.md tells this agent not to do.

Run:  python ops/link_graph_report.py
      python ops/link_graph_report.py --detail zones   list every zone's inbound count
"""
from __future__ import annotations

import collections
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

SKIP_DIRS = ("downloads/", "deck/", "nginx/")


def content_pages() -> list[str]:
    out = []
    for p in sorted(glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(p, SITE).replace("\\", "/")
        if any(rel.startswith(s) for s in SKIP_DIRS):
            continue
        out.append(p)
    return out


def body_only(html: str) -> str:
    """<main> if the page has one (every generated page does), otherwise the
    whole document with <header> and <footer> stripped (a few hand written
    pages, e.g. index.html, do not wrap content in <main>)."""
    m = re.search(r"<main\b[^>]*>(.*)</main>", html, re.S)
    if m:
        return m.group(1)
    t = re.sub(r"<header\b.*?</header>", " ", html, flags=re.S)
    t = re.sub(r"<footer\b.*?</footer>", " ", t, flags=re.S)
    return t


def links_from(path: str, html: str) -> set[str]:
    """Canonical site-relative targets ('zones/x.html') this page links to."""
    out = set()
    for href in re.findall(r'href="([^"]+)"', body_only(html)):
        if href.startswith(("http", "#", "mailto:", "tel:", "javascript:")):
            continue
        rel = re.split(r"[?#]", href)[0]
        if not rel:
            continue
        if rel.startswith("/"):
            target = os.path.normpath(os.path.join(SITE, rel.lstrip("/")))
        else:
            target = os.path.normpath(os.path.join(os.path.dirname(path), rel))
        if not target.endswith(".html"):
            target += ".html"
        if os.path.exists(target):
            out.add(os.path.relpath(target, SITE).replace("\\", "/"))
    return out


def main(detail: str | None) -> int:
    pages = content_pages()
    htmls = {p: io.open(p, encoding="utf-8", errors="replace").read() for p in pages}
    rel = {p: os.path.relpath(p, SITE).replace("\\", "/") for p in pages}

    outbound = {rel[p]: links_from(p, htmls[p]) for p in pages}
    inbound = collections.defaultdict(set)
    for src, targets in outbound.items():
        for t in targets:
            inbound[t].add(src)

    zones = sorted(r for r in rel.values() if r.startswith("zones/"))
    rooms = sorted(r for r in rel.values() if r.startswith("rooms/"))
    articles = sorted(r for r in rel.values() if r.startswith("articles/")
                      and r != "articles/index.html")

    def report(label, group):
        counts = {g: len(inbound[g]) for g in group}
        orphans = [g for g, c in counts.items() if c == 0]
        thin = [g for g, c in counts.items() if c == 1]
        no_out = [g for g in group if len(outbound.get(g, set())) == 0]
        print(f"\n  {label}: {len(group)} pages")
        if counts:
            vals = list(counts.values())
            print(f"    inbound links from other content pages: "
                 f"min {min(vals)}, max {max(vals)}, avg {sum(vals)/len(vals):.1f}")
        print(f"    orphans (0 inbound):  {len(orphans)}")
        for o in orphans[:15]:
            print(f"      {o}")
        if len(orphans) > 15:
            print(f"      ... and {len(orphans) - 15} more")
        print(f"    thin (exactly 1 inbound): {len(thin)}")
        print(f"    dead ends (0 outbound in body): {len(no_out)}")
        for o in no_out[:10]:
            print(f"      {o}")
        return counts

    print(f"  {len(pages)} pages scanned")
    zc = report("zone pages", zones)
    rc = report("room pages", rooms)
    ac = report("articles", articles)

    # resources.html is the hub every room and zone page's breadcrumb points
    # back to, and the only page the primary nav sends a reader to for rooms.
    # If it stopped linking out to the 114 zone pages, they would still be
    # crawlable (each links to its siblings and to resources.html), but a
    # reader or a crawler starting from the nav would never reach one.
    res_out = outbound.get("resources.html", set())
    zones_from_res = sum(1 for z in zones if z in res_out)
    rooms_from_res = sum(1 for r in rooms if r in res_out)
    print(f"\n  resources.html links directly to {rooms_from_res}/{len(rooms)} "
         f"room pages and {zones_from_res}/{len(zones)} zone pages")

    if detail:
        group = {"zones": zc, "rooms": rc, "articles": ac}.get(detail)
        if group is None:
            print(f"\n  unknown --detail '{detail}', use zones, rooms, or articles")
            return 2
        print(f"\n  every {detail} page, inbound count:")
        for g, c in sorted(group.items(), key=lambda kv: kv[1]):
            print(f"    {c:>3}  {g}")
        return 0

    total_orphans = sum(1 for g in (zc, rc, ac) for v in g.values() if v == 0)
    print(f"\n  {'0 orphans across zones, rooms and articles.' if total_orphans == 0 else str(total_orphans) + ' orphan page(s) found across zones, rooms and articles.'}")
    return 1 if total_orphans else 0


if __name__ == "__main__":
    d = None
    if "--detail" in sys.argv:
        i = sys.argv.index("--detail")
        d = sys.argv[i + 1] if len(sys.argv) > i + 1 else None
    sys.exit(main(d))
