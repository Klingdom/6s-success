#!/usr/bin/env python3
"""
Repoint every hardcoded Stripe link in the site at the link that is live now.

THE PROBLEM
-----------
166 pages carry a payment link typed straight into the HTML. Stripe rotates a
link whenever the price changes, because a payment link's line items are
immutable and a new price means a new link. The moment that happens, every
hardcoded copy is a button that takes a customer to a dead checkout, and
nothing on the page looks any different.

That is exactly what happened here: dropping the book to $9.99 and archiving
155 duplicate products retired several links, and 166 zone pages went on
pointing at a whole house pack link that no longer resolves.

HOW IT RESOLVES THEM
--------------------
Every payment link this system has ever created carries its SKU in
metadata, and Stripe keeps deactivated links. So a dead URL found on a page
can be looked up, its SKU read off it, and the current live link for that SKU
substituted. No mapping file to maintain, and it self heals after any future
rotation.

A URL that resolves to no SKU at all is reported and left alone rather than
guessed at. Guessing which product a stranger's link was for is how a page
ends up selling the wrong thing.

WHAT COUNTS AS A PAGE
----------------------
Not only *.html. ops/check_live_links.py already learned, the hard way, that
a hardcoded buy.stripe.com link hiding in a .js file is invisible to a checker
that only reads HTML: data.js carries 155 of them on its own and quest.js
carries the one offered at the end of a finished zone, the highest intent
moment on the site. That lesson was written into the checker and never carried
to this repair tool, which is the one that would actually have to fix it, so
for a long time this scanned *.html only and would have silently left every
.js file on the exact link it exists to retire.

Run:  python ops/sync_page_links.py --check
      python ops/sync_page_links.py --apply
"""
from __future__ import annotations

import collections
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import stripe_catalog as sc                                    # noqa: E402

SITE = os.path.join(ROOT, "site")
URL_RE = re.compile(r"https://buy\.stripe\.com/[A-Za-z0-9]+")


def current_by_sku() -> dict:
    js = io.open(os.path.join(SITE, "assets", "js", "data.js"),
                 encoding="utf-8").read()
    arr = json.loads(js[js.index("["):js.rindex("]") + 1])
    return {i["sku"]: i["buy"] for i in arr if i.get("buy")}


def discover_files() -> list:
    """Every file a hardcoded buy.stripe.com link could hide in.

    Not only *.html: see the module docstring's "WHAT COUNTS AS A PAGE".
    A standalone function so a gate can prove .js is covered without needing
    the Stripe credential the rest of this module requires.
    """
    return (glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True)
            + glob.glob(os.path.join(SITE, "**", "*.js"), recursive=True))


def main(apply_it: bool) -> int:
    live_for = current_by_sku()

    # Every link ever made, active or not, so a retired URL still resolves.
    sku_of, active = {}, set()
    for l in sc.list_all("payment_links"):
        s = (l.get("metadata") or {}).get("sku")
        if s:
            sku_of[l["url"]] = s
            if l.get("active"):
                active.add(l["url"])

    files = discover_files()
    seen = collections.Counter()
    for f in files:
        for u in URL_RE.findall(io.open(f, encoding="utf-8",
                                        errors="replace").read()):
            seen[u] += 1

    dead = {u: n for u, n in seen.items() if u not in active}
    fixable = {u: n for u, n in dead.items() if sku_of.get(u) in live_for}
    orphan = {u: n for u, n in dead.items() if u not in fixable}

    print(f"  {len(seen)} distinct stripe links across {len(files)} pages")
    print(f"  live: {len(seen) - len(dead)}   dead: {len(dead)}")
    for u, n in sorted(dead.items(), key=lambda kv: -kv[1]):
        s = sku_of.get(u)
        where = f"-> {live_for[s]}" if s in live_for else "UNRESOLVABLE"
        print(f"    {n:>4} uses  {u[-10:]}  sku={s or '?':<24} {where[:44]}")

    if orphan:
        print(f"\n  {len(orphan)} dead link(s) carry no sku this account knows, "
              f"so they are left alone rather than guessed at.")

    if not apply_it:
        print("\n  --check only, nothing written.")
        return 0

    changed = 0
    for f in files:
        s = io.open(f, encoding="utf-8").read()
        out = s
        for u in fixable:
            out = out.replace(u, live_for[sku_of[u]])
        if out != s:
            io.open(f, "w", encoding="utf-8", newline="").write(out)
            changed += 1

    # Verify by re-reading: no page may still carry a link that is not live.
    still = collections.Counter()
    for f in files:
        for u in URL_RE.findall(io.open(f, encoding="utf-8",
                                        errors="replace").read()):
            if u not in active:
                still[u] += 1
    assert not (set(still) - set(orphan)), (
        f"pages still carry dead links after the pass: {list(still)[:3]}")

    print(f"\n  rewrote {changed} pages")
    print(f"  every stripe link on the site is now an active one"
          + (f", except {sum(orphan.values())} unresolvable" if orphan else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--apply" in sys.argv))
