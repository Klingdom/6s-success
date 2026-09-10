#!/usr/bin/env python3
"""
Build site/feed.xml, an Atom feed of the root-cause articles under
site/articles/.

Why this exists
----------------
GOALS.md O1 names the constraint plainly: the site is otherwise finished and
almost nobody arrives, and the one thing every unblocked cycle can still do is
put an existing asset in front of a person (decision rule 1, "distribution
beats production"). A feed is a zero-cost distribution surface: unlike
YouTube, Search Console, Instagram or Etsy it needs no account only Phil can
create, nothing to enable, and nothing to pay for. A feed reader, an
aggregator, or a script watching for new posts can follow this site's writing
without polling every page or waiting on a search engine's own crawl schedule.

Where the data comes from
--------------------------
Nothing here is typed by hand. Every field is read back off the article page
itself: <title>, the meta description, its own <link rel="canonical">, and
its own datePublished/dateModified JSON-LD, the same fields ops/build_seo.py
already stamps onto every page for search engines. That means this file
cannot drift from what the page actually says, and a new article under
site/articles/ is picked up the next time this runs with no edit needed here.

The two articles ops/build_articles.py writes (what-is-6s.html,
how-long-does-it-take-to-organise-a-room.html) predate the JSON-LD date
fields the other 28 articles carry, so they have none. Rather than invent a
date, this falls back to the git commit date that last touched the file, a
real, checkable date, not a guess.

site/articles/index.html is not an article and is skipped. Any file missing a
title, description or canonical link is skipped rather than guessed at.

Run:  python ops/build_feed.py           write site/feed.xml
      python ops/build_feed.py --check   exit 1 if the written file would differ
"""
from __future__ import annotations

import glob
import html
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
ARTICLES = os.path.join(SITE, "articles")
BASE = "https://6s-success.com"
FEED_URL = BASE + "/feed.xml"
OUT = os.path.join(SITE, "feed.xml")


def _committed_date(fp: str) -> str | None:
    """The date git last committed this file, stable across checkouts of the
    same commit. Only used as a fallback when a page carries no JSON-LD date."""
    rel = os.path.relpath(fp, ROOT).replace(os.sep, "/")
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", rel],
                            cwd=ROOT, capture_output=True, text=True, timeout=30)
    except Exception:                                             # noqa: BLE001
        return None
    d = (r.stdout or "").strip()
    return d if r.returncode == 0 and len(d) == 10 else None


def _entry(fp: str) -> dict | None:
    src = io.open(fp, encoding="utf-8", errors="replace").read()
    tm = re.search(r"<title>([^<]*)</title>", src)
    dm = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', src)
    cm = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', src)
    if not (tm and dm and cm):
        return None
    title = html.unescape(tm.group(1)).strip()
    desc = html.unescape(dm.group(1)).strip()
    url = cm.group(1).strip()
    pm = re.search(r'"datePublished"\s*:\s*"([^"]+)"', src)
    mm = re.search(r'"dateModified"\s*:\s*"([^"]+)"', src)
    published = pm.group(1) if pm else _committed_date(fp)
    modified = mm.group(1) if mm else (published or _committed_date(fp))
    if not published or not modified:
        return None
    return {"title": title, "desc": desc, "url": url,
            "published": published, "modified": modified}


def entries() -> list[dict]:
    out = []
    for fp in sorted(glob.glob(os.path.join(ARTICLES, "*.html"))):
        if os.path.basename(fp) == "index.html":
            continue
        e = _entry(fp)
        if e:
            out.append(e)
    # newest first, stable on a tie by title so re-runs never reorder by
    # accident (glob already returns files sorted, but modified dates repeat)
    out.sort(key=lambda e: (e["modified"], e["title"]), reverse=True)
    return out


def _index_meta() -> tuple[str, str]:
    fp = os.path.join(ARTICLES, "index.html")
    src = io.open(fp, encoding="utf-8", errors="replace").read()
    tm = re.search(r"<title>([^<]*)</title>", src)
    dm = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', src)
    title = html.unescape(tm.group(1)).strip() if tm else "6S Success: Articles"
    desc = html.unescape(dm.group(1)).strip() if dm else ""
    return title, desc


def esc(t: str) -> str:
    return html.escape(t or "", quote=True)


def render(rows: list[dict]) -> str:
    title, subtitle = _index_meta()
    updated = max((r["modified"] for r in rows), default=None)
    updated_ts = (updated + "T00:00:00Z") if updated else "1970-01-01T00:00:00Z"
    items = []
    for r in rows:
        items.append(
            "  <entry>\n"
            "    <title>%s</title>\n"
            "    <link href=\"%s\"/>\n"
            "    <id>%s</id>\n"
            "    <published>%sT00:00:00Z</published>\n"
            "    <updated>%sT00:00:00Z</updated>\n"
            "    <summary>%s</summary>\n"
            "  </entry>" % (esc(r["title"]), esc(r["url"]), esc(r["url"]),
                             r["published"], r["modified"], esc(r["desc"]))
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<feed xmlns="http://www.w3.org/2005/Atom">\n'
        '  <title>%s</title>\n'
        '  <subtitle>%s</subtitle>\n'
        '  <link href="%s" rel="self"/>\n'
        '  <link href="%s/articles/"/>\n'
        '  <id>%s/articles/</id>\n'
        '  <updated>%s</updated>\n'
        % (esc(title), esc(subtitle), FEED_URL, BASE, BASE, updated_ts)
        + "\n".join(items) + "\n</feed>\n"
    )
    return xml


def build() -> str:
    xml = render(entries())
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(xml)
    return xml


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        rows = entries()
        want = render(rows)
        have = io.open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if want != have:
            print("site/feed.xml is stale. Run python ops/build_feed.py.")
            sys.exit(1)
        print("site/feed.xml is current, %d entries." % len(rows))
        sys.exit(0)
    out = build()
    print("feed.xml written: %d entries" % out.count("<entry>"))
