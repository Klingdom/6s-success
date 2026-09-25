#!/usr/bin/env python3
"""
Cut the primary navigation from seven items to five.

WHY
---
A UX review put this first and it is right. The header currently offers The
Method, Rooms, Micro zones, The Quest, Shop, Consulting and The Book: seven
doors before a visitor has chosen a room or understood what a micro zone is.
That is decision friction at the exact moment the brand promises to remove it.

Worse, three of the seven are the same door. Rooms, Micro zones and The Quest
are all "start working on your house", split three ways.

THE NEW FIVE, in the order a visitor needs them
-----------------------------------------------
    Start a reset   the primary action, pointing at the zone index
    How 6S works    the method, for somebody deciding whether to trust it
    Rooms           browse, once they know what they are looking for
    Cards and book  learn and buy
    Get help        the service

The visitor's task first, the method second, buying last. About, Articles,
Contact and the legal pages move to the footer, where they already appear.

WHAT THIS DELIBERATELY DOES NOT DO
----------------------------------
It does not rename the Quest to Guided Reset everywhere. The review suggests
splitting the utility from the game, which is a good idea and a bigger one: the
app, its manifest, its install prompt, its offline cache and 176 page footers
all carry the name. That is a rename, not a nav change, and doing half of it
would leave the site calling one thing two names.

Idempotent. Run after any builder, then ops/fingerprint_assets.py.
"""
from __future__ import annotations

import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

# (href without prefix, label). Order is the order shown.
NAV = [
    ("zones/", "Start a reset"),
    ("method.html", "How 6S works"),
    ("resources.html", "Rooms"),
    ("book.html", "Cards and book"),
    ("consulting.html", "Get help"),
]


def build(prefix: str) -> str:
    return "".join(f'<a href="{prefix}{href}">{label}</a>' for href, label in NAV)


def main() -> int:
    n, unreadable = 0, []
    for f in sorted(glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(f, SITE).replace(os.sep, "/")
        if rel.startswith("downloads/") or rel.startswith("deck/"):
            continue
        # A page must be read with its real encoding to be rewritten byte
        # for byte, so this cannot fall back to errors="replace" the way
        # the read-only link check below does; one file this script cannot
        # safely read must not crash the whole pass, only be skipped and
        # named, since a rewrite it could not perform is a smaller failure
        # than a rewrite it never got to attempt on 190 other pages.
        try:
            s = io.open(f, encoding="utf-8").read()
        except UnicodeDecodeError:
            unreadable.append(rel)
            continue
        m = re.search(r'(<nav class="nav"[^>]*>)(.*?)(</nav>)', s, re.S)
        if not m:
            continue

        # The prefix a page needs is the one its existing links already use,
        # read from the markup rather than derived from the path, so a page in
        # a directory nobody anticipated still gets working links.
        inner = m.group(2)
        pre = ""
        depth = re.search(r'href="((?:\.\./)+)', inner)
        if depth:
            pre = depth.group(1)
        elif rel.count("/"):
            pre = "../" * rel.count("/")

        new = m.group(1) + "\n      " + build(pre).replace("><", ">\n      <") + "\n    " + m.group(3)
        if new == m.group(0):
            continue
        s2 = s[:m.start()] + new + s[m.end():]
        io.open(f, "w", encoding="utf-8", newline="").write(s2)
        n += 1

    print(f"  navigation rewritten on {n} pages, {len(NAV)} items")
    if unreadable:
        print(f"  UNREADABLE, skipped rather than crashed on: {unreadable}")

    # A nav link that 404s is worse than a crowded nav. Read-only scan, so
    # errors="replace" is safe here the way it is not in the rewrite loop
    # above, and matches every other read-only scan in this codebase
    # (ops/preflight.py's gate_nav_canonical among them); without it, one
    # unrelated file under site/ with a bad encoding crashes this whole
    # script before the link check it exists to run ever completes.
    bad = []
    for f in glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True):
        s = io.open(f, encoding="utf-8", errors="replace").read()
        m = re.search(r'<nav class="nav"[^>]*>(.*?)</nav>', s, re.S)
        if not m:
            continue
        for href in re.findall(r'href="([^"]+)"', m.group(1)):
            target = os.path.normpath(os.path.join(os.path.dirname(f), href))
            if os.path.isdir(target):
                target = os.path.join(target, "index.html")
            if not os.path.exists(target):
                bad.append((os.path.relpath(f, ROOT), href))
    assert not bad, f"navigation links that resolve to nothing: {bad[:4]}"
    print(f"  every nav link on every page resolves")

    # build() writes a plain nav with no aria-current marker at all (it has
    # no notion of "which page is this"), so every page this script touches
    # loses its "you are here" mark for a screen reader until something else
    # restores it. Found 2026-09-25, cold-reading this file: running it
    # against the real, currently-committed site silently stripped
    # aria-current="page" from all 5 pages it touched (method.html,
    # resources.html, book.html, consulting.html, zones/index.html), the
    # exact live regression ops/preflight.py's gate_nav_current exists to
    # catch on the next run, but only on the NEXT run, not this one, and
    # this script's own docstring ("Idempotent. Run after any builder, then
    # ops/fingerprint_assets.py.") never mentions needing wire_aria_current
    # to follow, unlike wire_aria_current's own docstring, which names
    # wire_measure and wire_pwa by name as passes it has to run after.
    # Chain it here instead of trusting a human to remember a step nothing
    # documents, the same fix already applied to ops/wire_measure.py this
    # week for its own missing chain link.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import wire_aria_current
    wire_aria_current.main()

    if unreadable:
        # A page this script could not read is a page whose nav was not
        # checked or rewired; per CLAUDE.md 0.4, unknown is not a default,
        # so this cannot report success while one exists.
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
