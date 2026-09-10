#!/usr/bin/env python3
"""
Unit tests for ops/build_feed.py: the field parser, the date fallback, and
that the rendered feed is well-formed XML a reader can actually parse.

Run:  python ops/tests/test_build_feed.py
"""
import io
import os
import sys
import tempfile
import xml.dom.minidom as minidom

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import build_feed as bf                                        # noqa: E402

PAGE_WITH_DATES = """<!doctype html>
<html><head>
<title>Why the drawer never stays shut</title>
<meta name="description" content="A test article about drawers.">
<link rel="canonical" href="https://6s-success.com/articles/why-the-drawer-never-stays-shut">
<script type="application/ld+json">
{"datePublished": "2026-08-20", "dateModified": "2026-08-25"}
</script>
</head><body></body></html>
"""

PAGE_NO_DATES = """<!doctype html>
<html><head>
<title>A page with no JSON-LD dates</title>
<meta name="description" content="Falls back to the commit date.">
<link rel="canonical" href="https://6s-success.com/articles/no-dates">
</head><body></body></html>
"""

PAGE_NO_CANONICAL = """<!doctype html>
<html><head>
<title>Missing its canonical link</title>
<meta name="description" content="Should be skipped, not guessed at.">
</head><body></body></html>
"""


def _write(tmp, name, body):
    fp = os.path.join(tmp, name)
    io.open(fp, "w", encoding="utf-8").write(body)
    return fp


def main() -> int:
    fails = []
    tmp = tempfile.mkdtemp()

    # 1. A page with real JSON-LD dates: parsed exactly, nothing guessed.
    fp = _write(tmp, "a.html", PAGE_WITH_DATES)
    e = bf._entry(fp)
    if not e or e["published"] != "2026-08-20" or e["modified"] != "2026-08-25":
        fails.append("dated page parsed wrong: %r" % (e,))
    if not e or e["title"] != "Why the drawer never stays shut":
        fails.append("title parsed wrong: %r" % (e,))

    # 2. A page with no JSON-LD dates falls back to a real value, not None
    #    and not a fabricated one; here it falls back to _committed_date,
    #    which returns None for a file git has never seen, so the whole
    #    entry is correctly dropped rather than guessed.
    fp = _write(tmp, "b.html", PAGE_NO_DATES)
    e = bf._entry(fp)
    if e is not None:
        fails.append("an untracked file with no JSON-LD date should have "
                     "been skipped (no honest date available), got: %r" % (e,))

    # 3. A page missing a canonical link must be skipped, not guessed at.
    fp = _write(tmp, "c.html", PAGE_NO_CANONICAL)
    e = bf._entry(fp)
    if e is not None:
        fails.append("a page with no canonical link should be skipped, "
                     "got: %r" % (e,))

    # 4. The real, committed corpus renders to well-formed XML a reader can
    #    actually parse, with at least 20 entries (there are 29 articles).
    rows = bf.entries()
    xml = bf.render(rows)
    try:
        doc = minidom.parseString(xml.encode("utf-8"))
    except Exception as exc:                                     # noqa: BLE001
        fails.append("rendered feed.xml is not well-formed XML: %s" % exc)
    else:
        n = len(doc.getElementsByTagName("entry"))
        if n != len(rows):
            fails.append("rendered <entry> count (%d) does not match "
                         "entries() (%d)" % (n, len(rows)))
    if len(rows) < 20:
        fails.append("only %d real articles found, expected 20+" % len(rows))

    # 5. Two runs back to back are byte-identical (the generator-ownership
    #    property every other generator in this repo is required to hold).
    if bf.render(bf.entries()) != bf.render(bf.entries()):
        fails.append("build_feed.render() is not stable across two "
                     "back-to-back runs on the same tree")

    # 6. index.html itself is never included as an article.
    urls = [r["url"] for r in rows]
    if any(u.rstrip("/").endswith("/articles") for u in urls):
        fails.append("site/articles/index.html was wrongly included as an "
                     "article entry")

    import shutil
    shutil.rmtree(tmp)

    if fails:
        print("FAIL")
        for x in fails:
            print(" -", x)
        return 1
    print("OK: build_feed, 6/6 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
