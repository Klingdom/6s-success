#!/usr/bin/env python3
"""
A skip link on every page, and a main landmark on the fourteen without one.

THE DEFECT
----------
No page on this site had a skip link, and fourteen of them had no <main>
element either. Those fourteen are not obscure: they are the homepage, the
Quest, the shop, the method page, consulting, contact, the book, the deck and
the zone index. Every high traffic entry point except the generated zone, room
and article templates, which do have one.

So a keyboard or screen reader visitor traversed the brand link, the menu
button, five navigation links and Contact on every single page load, with no
landmark to jump to and nothing to skip with. Twenty two links in the footer of
every page, and no way past them either.

WHAT IT DOES
------------
Inserts a skip link as the first focusable thing in the body, and wraps the
content of a page that has no <main> in one, from after the header to before
the footer. It refuses rather than guesses when a page's shape is unfamiliar,
because wrapping the wrong span silently would be worse than leaving it.

Idempotent, marker based, and safe to re-run.

Run:  python ops/wire_landmarks.py
      python ops/wire_landmarks.py --check
"""
from __future__ import annotations

import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

BEGIN = "<!-- SKIP:BEGIN -->"
END = "<!-- SKIP:END -->"
LINK = (BEGIN + '\n<a class="skip-link" href="#main">Skip to content</a>\n'
        + END)
MARKED = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.S)


def pages() -> list:
    out = []
    for f in sorted(glob.glob(os.path.join(SITE, "**", "*.html"),
                              recursive=True)):
        rel = os.path.relpath(f, SITE)
        # Downloadable artefacts are opened from a buyer's own disk and are
        # not navigated, the same exclusion ops/wire_measure.py makes.
        if rel.startswith(("downloads" + os.sep, "deck" + os.sep)):
            continue
        out.append(f)
    return out


def add_skip(s: str) -> str:
    if MARKED.search(s):
        return MARKED.sub(LINK, s)
    m = re.search(r"<body[^>]*>", s)
    if not m:
        return s
    return s[:m.end()] + "\n" + LINK + s[m.end():]


def add_main(s: str) -> tuple:
    """Wrap the body content in <main id="main"> when there is no main.

    Only where the shape is recognisable: content sits between the end of the
    header and the start of the footer. Anything else is left alone and
    reported, because a landmark around the wrong span is worse than none.
    """
    if "<main" in s:
        # Give the existing main the id the skip link points at.
        if 'id="main"' not in s:
            s = re.sub(r"<main\b", '<main id="main"', s, count=1)
        return s, "had one"

    he = s.find("</header>")
    fs = s.find("<footer")
    if he == -1 or fs == -1 or fs <= he:
        return s, "unfamiliar shape, left alone"

    head, body, tail = s[:he + 9], s[he + 9:fs], s[fs:]
    return head + '\n<main id="main">\n' + body + '\n</main>\n' + tail, "wrapped"


def main() -> int:
    check = "--check" in sys.argv
    wrapped = existing = odd = 0
    for f in pages():
        s = io.open(f, encoding="utf-8").read()
        new, how = add_main(s)
        new = add_skip(new)
        if how == "wrapped":
            wrapped += 1
        elif how == "had one":
            existing += 1
        else:
            odd += 1
            print(f"  LEFT ALONE  {os.path.relpath(f, SITE)}: {how}")
        if new != s and not check:
            io.open(f, "w", encoding="utf-8", newline="").write(new)

    print(f"  {len(pages())} pages: {existing} already had a main landmark, "
          f"{wrapped} wrapped, {odd} left alone")
    print(f"  skip link {'would be' if check else ''} present on every page "
          f"that has a body")

    css = io.open(os.path.join(SITE, "assets", "css", "site.css"),
                  encoding="utf-8").read()
    if ".skip-link" not in css:
        print("  WARNING: site.css has no .skip-link rule, so the link would "
              "sit visibly at the top of every page")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
