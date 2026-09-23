#!/usr/bin/env python3
"""
Collapse duplicate Stripe products down to one per SKU.

WHY THEY EXIST
--------------
ops/stripe_catalog.py looked up existing objects with a single unpaginated
call that took the first hundred as the whole account. Once the catalogue
passed a hundred SKUs, the idempotency check stopped finding things that
already existed, so a second --apply created a second Product, a second Price
and a second Payment Link for every SKU.

The duplicate links were cleaned up when they were found. The duplicate
products were not, and they cause a subtler failure: find_by_sku returns
product A while the live payment link sells a price belonging to product B.
Every run then decides the link charges an unrecognised price and replaces
it, so nothing is ever idempotent and the site's buy links change on every
run, going dead in between.

WHAT THIS KEEPS
---------------
For each SKU, the product whose active price matches the catalogue price. If
several qualify, the oldest, because it is the one with any purchase history
attached. Everything else is archived.

ARCHIVED, NOT DELETED. Stripe keeps archived products and they can be
restored. Deleting a product with a payment history is not something to do to
recover from a pagination bug.

Run:  python ops/stripe_dedupe.py --check
      STRIPE_ALLOW_LIVE=1 python ops/stripe_dedupe.py --apply
"""
from __future__ import annotations

import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import stripe_catalog as sc                                    # noqa: E402


def catalogue_prices() -> dict:
    js = io.open(os.path.join(ROOT, "site", "assets", "js", "data.js"),
                 encoding="utf-8").read()
    arr = json.loads(js[js.index("["):js.rindex("]") + 1])
    return {i["sku"]: int(round((i.get("price") or 0) * 100)) for i in arr}


def duplicates() -> dict:
    """SKUs with more than one ACTIVE product, as {sku: [products]}.

    Extracted so preflight can ask the question without running the fix or
    printing anything. Raises rather than returning {} when Stripe cannot be
    reached, because an empty dict means "checked, none found" and a caller
    that cannot tell those apart will report a clean account it never read.
    """
    by = {}
    for p in sc.list_all("products"):
        s = (p.get("metadata") or {}).get("sku")
        if s and p.get("active"):
            by.setdefault(s, []).append(p)
    if not by:
        raise RuntimeError("no active products with a sku came back from "
                           "Stripe, which is not a believable account state")
    return {k: v for k, v in by.items() if len(v) > 1}


def live_link_ids() -> tuple:
    """Every buy.stripe.com link id the LIVE site serves, and a note.

    The live site decides which duplicate survives. Not the repository, not
    the newest object, not the oldest: whichever link a customer can actually
    press today is the one that must keep working. Returns (ids, note) and
    the note is non-empty when nothing could be read, because an unreadable
    site is not an empty one.
    """
    import re
    import urllib.request
    base = "https://6s-success.com"

    def get(path):
        try:
            req = urllib.request.Request(
                base + path, headers={"User-Agent": "6s-dedupe-check"})
            return urllib.request.urlopen(req, timeout=30).read().decode(
                "utf-8", "replace")
        except Exception:                                      # noqa: BLE001
            return None

    sm = get("/sitemap.xml")
    if not sm:
        return set(), "could not read the live sitemap"
    paths = [u.replace(base, "") or "/"
             for u in re.findall(r"<loc>([^<]+)</loc>", sm)]
    paths += ["/assets/js/data.js", "/assets/js/shop.js"]
    ids, unreadable = set(), 0
    for path in paths:
        body = get(path)
        if body is None:
            unreadable += 1
            continue
        ids.update(re.findall(r"buy\.stripe\.com/([A-Za-z0-9]+)", body))
    if unreadable:
        return ids, "%d live page(s) unreadable" % unreadable
    return ids, ""


def dedupe_links(sc, apply_it: bool) -> int:
    """One active payment link per SKU, keeping the one the live site serves.

    Products were the loud half of the pagination bug this file was written
    for. Links are the quiet half: on 2026-09-23 five SKUs still had two
    active links each (BK-BUNDLE, CN-INHOME, CN-VIRTUAL, MZ-MANUAL,
    PACK-HOUSE), and this file's own docstring said the duplicate links "were
    cleaned up when they were found", which is to say by hand, once, with
    nothing to stop them coming back.

    Today they are harmless: every pair charges the identical amount, checked
    before touching anything. The reason to clean them up is what happens
    next time a price moves. ensure_link rebuilds the link the site serves and
    leaves the orphan alone, so the orphan would go on selling at the old
    price to anyone holding the old URL, which is the shape of mispricing
    nobody would notice for months.
    """
    import collections
    links = [L for L in sc.list_all("payment_links", {})
             if L.get("active") and (L.get("metadata") or {}).get("sku")]
    by = collections.defaultdict(list)
    for L in links:
        by[L["metadata"]["sku"]].append(L)
    dupes = {k: v for k, v in by.items() if len(v) > 1}
    print("  %d active payment links across %d skus, %d duplicated"
          % (len(links), len(by), len(dupes)))
    if not dupes:
        return 0

    served, note = live_link_ids()
    if note:
        print("  REFUSING to touch links: %s. Which link the site serves is "
              "the only thing that decides which one survives, so an "
              "unreadable site means unknown, not safe." % note)
        return 1

    import re
    changed = 0
    for sku, ls in sorted(dupes.items()):
        amounts = set()
        for L in ls:
            for it in sc.call("GET", "payment_links/%s/line_items" % L["id"],
                              {"limit": 5}).get("data", []):
                amounts.add((it.get("price") or {}).get("unit_amount"))
        keep = [L for L in ls
                if re.search(r"buy\.stripe\.com/([A-Za-z0-9]+)",
                             L.get("url", ""))
                and re.search(r"buy\.stripe\.com/([A-Za-z0-9]+)",
                              L["url"]).group(1) in served]
        if len(keep) != 1:
            print("  %-12s SKIPPED: the live site serves %d of its %d active "
                  "links, so there is no single obvious survivor"
                  % (sku, len(keep), len(ls)))
            continue
        drop = [L for L in ls if L["id"] != keep[0]["id"]]
        warn = "" if len(amounts) == 1 else "  PRICES DIFFER %s" % sorted(amounts)
        if not apply_it:
            print("  %-12s keep %s (served), deactivate %s%s"
                  % (sku, keep[0]["id"][-8:],
                     [d["id"][-8:] for d in drop], warn))
            continue
        for d in drop:
            sc.call("POST", "payment_links/" + d["id"], {"active": False})
            changed += 1
        print("  %-12s kept the served link, deactivated %d orphan(s)%s"
              % (sku, len(drop), warn))
    return changed


def main(apply_it: bool) -> int:
    if apply_it and sc.live() and os.environ.get("STRIPE_ALLOW_LIVE") != "1":
        sys.exit("Refusing to write to a LIVE account without STRIPE_ALLOW_LIVE=1")

    want = catalogue_prices()
    by = {}
    for p in sc.list_all("products"):
        s = (p.get("metadata") or {}).get("sku")
        if s and p.get("active"):
            by.setdefault(s, []).append(p)
    if not by:
        raise RuntimeError("no active products with a sku came back from "
                            "Stripe, which is not a believable account state")

    dupes = {k: v for k, v in by.items() if len(v) > 1}
    print(f"  {sum(len(v) for v in by.values())} active products across "
          f"{len(by)} skus, {len(dupes)} duplicated")
    if not dupes:
        print("  no duplicate products")
        print()
        # Links are a separate population from products and can be
        # duplicated while products are clean, which is exactly the state
        # found on 2026-09-23. Returning here would have skipped them.
        return 1 if dedupe_links(sc, apply_it) and not apply_it else 0

    archived = 0
    for sku, prods in sorted(dupes.items()):
        target = want.get(sku)
        scored = []
        for p in prods:
            prices = [x for x in sc.list_all("prices", {"product": p["id"]})
                      if x.get("active")]
            match = any(x["unit_amount"] == target for x in prices) if target else False
            scored.append((not match, p.get("created") or 0, p["id"], p))

        # A product carrying the right price wins. Among equals the oldest,
        # because it is the one any purchase history hangs off.
        scored.sort()
        keep = scored[0][3]
        drop = [x[3] for x in scored[1:]]

        if not apply_it:
            print(f"  {sku:24} keep {keep['id'][-8:]}, "
                  f"archive {[d['id'][-8:] for d in drop]}")
            continue

        for d in drop:
            sc.call("POST", f"products/{d['id']}", {"active": "false"})
            archived += 1
    sc.invalidate("products")

    if not apply_it:
        print("\n  --check only, nothing written. Re-run with --apply.")
        return 0

    print(f"  archived {archived} duplicate products")

    left = {}
    for p in sc.list_all("products"):
        s = (p.get("metadata") or {}).get("sku")
        if s and p.get("active"):
            left.setdefault(s, []).append(p)
    still = {k: v for k, v in left.items() if len(v) > 1}
    assert not still, f"still duplicated after the pass: {list(still)[:4]}"
    print(f"  every sku now resolves to exactly one active product")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--apply" in sys.argv))
