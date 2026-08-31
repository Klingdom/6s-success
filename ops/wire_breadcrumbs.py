#!/usr/bin/env python3
"""
Mark up the breadcrumb every article already renders.

THE GAP
-------
All 29 article pages render a visible breadcrumb, "Home / The Method / Why you
always lose your keys", and two of them describe it in structured data. The
other 27 show a reader the trail and tell a search engine nothing about it.

This is the cheapest structured data on the site: the trail exists, it is
correct, and it is already on the page. Nothing here is invented, which matters
because the alternative kind of structured data, the kind that describes
something a page does not actually contain, is the kind that gets a site
penalised and deserves to.

HOW IT STAYS TRUE
-----------------
The JSON-LD is built by reading the rendered breadcrumb out of the page, so it
cannot describe a trail the page does not show. If the visible breadcrumb
changes, this describes the new one; if a page has no breadcrumb, it gets no
markup.

Idempotent, marker based.

Run:  python ops/wire_breadcrumbs.py
      python ops/wire_breadcrumbs.py --check
"""
from __future__ import annotations

import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
BASE = "https://6s-success.com"

BEGIN = "<!-- CRUMBLD:BEGIN -->"
END = "<!-- CRUMBLD:END -->"
MARKED = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.S)

NAV = re.compile(r'<nav class="crumb[^"]*"[^>]*>(.*?)</nav>', re.S)
PART = re.compile(r'<a href="([^"]+)">(.*?)</a>|([^<>/][^<>]*)', re.S)


def trail(page: str, html: str) -> list:
    """(name, absolute url or None) for each step the page actually shows."""
    m = NAV.search(html)
    if not m:
        return []
    out = []
    for a in PART.finditer(m.group(1)):
        href, text, plain = a.group(1), a.group(2), a.group(3)
        if href:
            name = re.sub(r"<[^>]+>", "", text).strip()
            if not name:
                continue
            target = os.path.normpath(
                os.path.join(os.path.dirname(page), href))
            rel = os.path.relpath(target, SITE).replace(os.sep, "/")
            out.append((name, f"{BASE}/{rel}"))
        elif plain:
            name = plain.replace("/", " ").strip()
            if name:
                out.append((name, None))
    return out


def block(items: list) -> str:
    nodes = []
    for i, (name, url) in enumerate(items, 1):
        item = {"@type": "ListItem", "position": i, "name": name}
        if url:
            item["item"] = url
        nodes.append(item)
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList",
          "itemListElement": nodes}
    return (BEGIN + '\n<script type="application/ld+json">\n'
            + json.dumps(ld, indent=1) + "\n</script>\n" + END)


def main() -> int:
    check = "--check" in sys.argv
    done, skipped = 0, 0
    for f in sorted(glob.glob(os.path.join(SITE, "articles", "*.html"))):
        if f.endswith("index.html"):
            continue
        s = io.open(f, encoding="utf-8").read()
        if "BreadcrumbList" in s and not MARKED.search(s):
            skipped += 1          # already has one from its own generator
            continue
        items = trail(f, s)
        if len(items) < 2:
            skipped += 1
            continue
        b = block(items)
        new = MARKED.sub(b, s) if MARKED.search(s) else \
            s.replace("</head>", b + "\n</head>", 1)
        if new != s and not check:
            io.open(f, "w", encoding="utf-8", newline="").write(new)
        done += 1

    print(f"  {'would mark up' if check else 'marked up'} {done} article "
          f"breadcrumb(s), {skipped} left alone")
    if done:
        sample = sorted(glob.glob(os.path.join(SITE, "articles", "*.html")))
        for f in sample:
            if f.endswith("index.html"):
                continue
            t = trail(f, io.open(f, encoding="utf-8").read())
            print("  sample trail: " + " / ".join(n for n, _ in t))
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
