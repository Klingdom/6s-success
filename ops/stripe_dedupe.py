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


def _active_links_by_sku() -> dict:
    """Every ACTIVE payment link carrying a sku, grouped: {sku: [links]}."""
    import collections
    links = [L for L in sc.list_all("payment_links", {})
             if L.get("active") and (L.get("metadata") or {}).get("sku")]
    by = collections.defaultdict(list)
    for L in links:
        by[L["metadata"]["sku"]].append(L)
    return dict(by)


def duplicate_active_links() -> dict:
    """SKUs with more than one ACTIVE payment link, as {sku: [links]}.

    The quiet half of the pagination bug this file exists for: a duplicate
    PRODUCT breaks pricing loudly, at checkout, where a customer sees the
    wrong number. A duplicate LINK breaks it quietly, per dedupe_links()'s
    own docstring: both links usually charge the same amount on the day
    they are found, and only diverge the next time the price moves, when
    the orphan goes on selling at the old price to anyone holding its URL.
    Extracted the same way duplicates() is above, so preflight can ask the
    question without reading the live site to decide a survivor or running
    the fix.

    Raises rather than returning {} when Stripe cannot be reached, matching
    duplicates()'s own contract: an empty dict must mean "checked, none
    found," never "could not check."
    """
    by = _active_links_by_sku()
    if not by:
        raise RuntimeError("no active payment links with a sku came back "
                           "from Stripe, which is not a believable account "
                           "state")
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

    Returns the number of SKUs left with more than one active link once this
    call is done: 0 in `--check` means nothing to report; 0 in `--apply`
    means everything got resolved. Previously returned a "changed" counter
    that was always 0 in `--check` (nothing is changed in a dry run) even
    when real duplicates were printed, so a caller reading only the return
    value could never tell "--check found problems" from "--check found
    nothing." Fixed 2026-09-26 alongside main()'s own exit-code bug.

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
    by = _active_links_by_sku()
    dupes = {k: v for k, v in by.items() if len(v) > 1}
    links_total = sum(len(v) for v in by.values())
    print("  %d active payment links across %d skus, %d duplicated"
          % (links_total, len(by), len(dupes)))
    if not dupes:
        return 0

    served, note = live_link_ids()
    if note:
        print("  REFUSING to touch links: %s. Which link the site serves is "
              "the only thing that decides which one survives, so an "
              "unreadable site means unknown, not safe." % note)
        return len(dupes)

    import re
    unresolved = 0
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
            unresolved += 1
            continue
        drop = [L for L in ls if L["id"] != keep[0]["id"]]
        warn = "" if len(amounts) == 1 else "  PRICES DIFFER %s" % sorted(amounts)
        if not apply_it:
            print("  %-12s keep %s (served), deactivate %s%s"
                  % (sku, keep[0]["id"][-8:],
                     [d["id"][-8:] for d in drop], warn))
            unresolved += 1
            continue
        for d in drop:
            sc.call("POST", "payment_links/" + d["id"], {"active": False})
        print("  %-12s kept the served link, deactivated %d orphan(s)%s"
              % (sku, len(drop), warn))
    return unresolved


def main(apply_it: bool) -> int:
    """Dedupe products, THEN always dedupe links, and report a real exit code.

    Products and payment links are separate populations, both created by the
    same pagination bug and both able to be duplicated independently. The
    2026-09-23 fix made the "products clean" path fall through to
    dedupe_links() so a clean-products/duplicated-links account would still
    get checked. It missed the mirror case: when products WERE duplicated,
    the function returned before ever reaching dedupe_links(), so a run that
    found duplicate products silently skipped checking links in the same
    breath, even though the docstring above already names five real SKUs
    that had duplicated links on that very day. Found cold-reading this file
    2026-09-26; confirmed live with a mock account carrying both a
    duplicate product AND a duplicate link on the same SKU: dedupe_links()
    never ran, and `--check` still exited 0.

    The exit code itself was also unconditionally 0 in `--check` mode
    regardless of what was found, for both products and links, so nothing
    reading only the exit code (rather than the printed lines) could ever
    learn that a problem exists. Fixed: exit 0 only when nothing was left
    duplicated (nothing to report in `--check`, nothing unresolved after
    `--apply`); non-zero otherwise.
    """
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
    else:
        archived = 0
        for sku, prods in sorted(dupes.items()):
            target = want.get(sku)
            scored = []
            for p in prods:
                prices = [x for x in sc.list_all("prices", {"product": p["id"]})
                          if x.get("active")]
                match = any(x["unit_amount"] == target for x in prices) if target else False
                scored.append((not match, p.get("created") or 0, p["id"], p))

            # A product carrying the right price wins. Among equals the
            # oldest, because it is the one any purchase history hangs off.
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

        if apply_it:
            print(f"  archived {archived} duplicate products")
            left = {}
            for p in sc.list_all("products"):
                s = (p.get("metadata") or {}).get("sku")
                if s and p.get("active"):
                    left.setdefault(s, []).append(p)
            still = {k: v for k, v in left.items() if len(v) > 1}
            assert not still, f"still duplicated after the pass: {list(still)[:4]}"
            print("  every sku now resolves to exactly one active product")

    print()
    link_problem = dedupe_links(sc, apply_it)

    if not apply_it:
        if dupes or link_problem:
            print("\n  --check only, nothing written. Re-run with --apply.")
        return 1 if (dupes or link_problem) else 0

    return 1 if link_problem else 0


if __name__ == "__main__":
    raise SystemExit(main("--apply" in sys.argv))
