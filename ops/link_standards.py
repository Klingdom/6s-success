#!/usr/bin/env python3
"""
Put the Standards Pack in the footer of every page, beside the Entryway deck.

A free artifact nobody can find is not a free artifact. The footer is the one
element on all 167 pages, and the deck link next to it is the closest thing to
it in kind, so it belongs there rather than in the primary nav, which is already
six items wide on a phone.

Idempotent: pages that already carry the link are left alone. Safe to run on
every build.

Run:  python ops/link_standards.py
"""
from __future__ import annotations

import glob
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


def main() -> int:
    n = skipped = 0
    for f in glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True):
        s = io.open(f, encoding="utf-8").read()
        if "standards.html\">The Standards Pack" in s:
            skipped += 1
            continue

        # The prefix a sibling link already uses is the prefix this page needs.
        # Deriving it from the existing markup rather than from the path means a
        # page in a directory nobody anticipated still gets a working link.
        #
        # Two footer shapes exist. Most pages list the Entryway deck and the new
        # link belongs beside it. The articles list neither deck, so there the
        # anchor is the Articles link itself, which is the last Learn item they
        # share with everything else.
        done = False
        for pre in ("", "../", "../../"):
            for anchor in (f'<a href="{pre}deck.html">The Entryway Deck</a>',
                           f'<a href="{pre}articles/">Articles</a>'):
                if anchor in s:
                    s = s.replace(
                        anchor,
                        anchor + f'<a href="{pre}standards.html">The Standards Pack</a>',
                        1)
                    io.open(f, "w", encoding="utf-8", newline="").write(s)
                    n += 1
                    done = True
                    break
            if done:
                break

    print(f"  footer link added to {n} pages, {skipped} already had it")

    # A link that resolves to nothing is worse than no link.
    for f in glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True):
        s = io.open(f, encoding="utf-8").read()
        for pre in ("", "../", "../../"):
            if f'href="{pre}standards.html"' in s:
                target = os.path.normpath(
                    os.path.join(os.path.dirname(f), pre, "standards.html"))
                assert os.path.exists(target), \
                    f"{os.path.relpath(f, ROOT)} links {pre}standards.html, which is not there"
    print("  every link checked, all resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
