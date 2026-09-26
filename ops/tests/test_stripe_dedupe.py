#!/usr/bin/env python3
"""
Prove stripe_dedupe.py's main() cannot report a clean account it never read.

Found 2026-09-18, PM cold-read of the money-domain ops/*.py tier.
duplicates() already raises when Stripe returns zero active products with a
sku, per its own docstring: "an empty dict means 'checked, none found' and a
caller that cannot tell those apart will report a clean account it never
read." main(), the --check/--apply CLI entry point, rebuilt the same
product-scanning loop inline without that guard, so the exact failure
duplicates() exists to catch (an unreachable or misbehaving account coming
back with nothing) printed "0 active products across 0 skus, 0 duplicated /
nothing to do" instead of surfacing as unchecked. Fixed by adding the same
raise to main()'s own loop.

Case 3 below was updated 2026-09-26 cold-reading this same file: it had
asserted `--check` returns 0 on a real duplicate PRODUCT, codifying a second
bug rather than catching it. `--check`'s exit code was unconditionally 0 no
matter what it found (products, links, or both), and a run that found
duplicate products returned before ever reaching dedupe_links(), so link
duplicates on the very same SKU went completely unread in that run. Both
fixed: main() now always calls dedupe_links() and returns 0 only when
nothing is left duplicated (see stripe_dedupe.py's own docstring on main()).

Run:  python ops/tests/test_stripe_dedupe.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import stripe_dedupe as sd                                    # noqa: E402


def product(pid, sku, price_cents, active=True, created=0):
    return {"id": pid, "active": active, "created": created,
            "metadata": {"sku": sku}, "_price": price_cents}


def main() -> int:
    fails = []
    orig_live, orig_list_all, orig_call, orig_invalidate = (
        sd.sc.live, sd.sc.list_all, sd.sc.call, sd.sc.invalidate)

    def prices_for(pid, catalog):
        p = next(x for x in catalog if x["id"] == pid)
        return [{"id": "price_" + pid, "active": True,
                  "unit_amount": p["_price"]}]

    def fake_list_all_factory(products, links=()):
        def fake_list_all(kind, params=None):
            if kind == "products":
                return products
            if kind == "prices":
                pid = (params or {}).get("product")
                return prices_for(pid, products)
            if kind == "payment_links":
                # Added 2026-09-23 when stripe_dedupe learned to collapse
                # duplicate payment links as well as duplicate products.
                # main() now falls through to dedupe_links() even when
                # products are clean, so this kind must be stubbed or the
                # product-side cases raise on an unstubbed call. An empty
                # list keeps those cases a clean no-op; a link population
                # that cannot be read must never become "no duplicates".
                # dedupe_links()'s own "serves neither candidate" branch is
                # covered separately by test_stripe_dedupe_links.py, which
                # is not exercised by cases 4-6 below.
                return list(links)
            raise AssertionError(f"unexpected kind: {kind}")
        return fake_list_all

    # Case 1: Stripe returns zero active products with a sku. This must not
    # look like a clean, deduplicated account; it must raise.
    sd.sc.live = lambda: False
    sd.sc.list_all = fake_list_all_factory([])
    try:
        sd.main(False)
    except RuntimeError:
        pass
    except SystemExit as e:
        fails.append(f"empty account raised SystemExit, not RuntimeError: {e}")
    else:
        fails.append("empty account returned normally instead of raising; "
                      "an unreachable/misbehaving account would report clean")

    # Case 2: one active product per sku, no duplicates: must report clean
    # for real, not raise.
    single = [product("prod_a", "BK-EB", 999, created=1)]
    sd.sc.list_all = fake_list_all_factory(single)
    try:
        rc = sd.main(False)
    except Exception as e:
        fails.append(f"single-product account raised unexpectedly: {e}")
    else:
        if rc != 0:
            fails.append(f"single-product --check returned {rc}, expected 0")

    # Case 3: a real duplicate, --check only, must not write and must pick
    # the product whose active price matches the catalogue, not merely the
    # oldest.
    want = sd.catalogue_prices()
    real_sku, real_price = next(iter(want.items()))
    dupes = [
        product("prod_old_wrong_price", real_sku, real_price + 100, created=1),
        product("prod_new_right_price", real_sku, real_price, created=2),
    ]
    sd.sc.list_all = fake_list_all_factory(dupes)
    calls = []
    sd.sc.call = lambda method, path, data=None: calls.append((method, path)) or {}
    sd.sc.invalidate = lambda kind: None
    try:
        rc = sd.main(False)
    except Exception as e:
        fails.append(f"--check on a real duplicate raised unexpectedly: {e}")
    else:
        if rc != 1:
            fails.append(f"--check on a real duplicate returned {rc}, expected "
                          "1 (a duplicate was found and not yet resolved)")
        if calls:
            fails.append(f"--check made write call(s): {calls}")

    # Cases 4-6: the payment-link half, added 2026-09-23 with the code it
    # exercises. Products are clean throughout, because the state actually
    # found on the live account was clean products and duplicated links, and
    # the old early return would have skipped them entirely.
    def link(lid, sku, slug):
        return {"id": lid, "active": True, "metadata": {"sku": sku},
                "url": "https://buy.stripe.com/" + slug}

    # Case 3b: the mirror gap this cycle found. A duplicate PRODUCT must
    # never stop a duplicate LINK on the same run from being read and
    # reported; the two populations are independent and both must be
    # checked every time, not only when the other is clean. Stub
    # live_link_ids so this does not depend on real network access: an
    # unreadable-site refusal still exercises dedupe_links(), which is the
    # thing case 3 (the old, buggy version of this test) never reached.
    dupe_links = [link("plink_x", real_sku, "XXXXXXX"),
                  link("plink_y", real_sku, "YYYYYYY")]
    link_calls = []
    orig_live_ids_3b = sd.live_link_ids
    sd.live_link_ids = lambda: ({"XXXXXXX"}, "")
    sd.sc.list_all = fake_list_all_factory(dupes, dupe_links)
    sd.sc.call = lambda method, path, data=None: link_calls.append((method, path)) or {}
    try:
        rc = sd.main(False)
    except Exception as e:
        fails.append(f"--check with product AND link duplicates raised: {e}")
    else:
        if rc != 1:
            fails.append(f"--check with both kinds duplicated returned {rc}, "
                          "expected 1")
        if not any("payment_links" in c[1] for c in link_calls
                   if "line_items" in c[1]):
            fails.append("dedupe_links() never ran when products were also "
                          "duplicated; the link duplicate on the same SKU "
                          "would have gone completely unreported")
    sd.live_link_ids = orig_live_ids_3b

    two = [link("plink_keep", "BK-EB", "SERVED1"),
           link("plink_orphan", "BK-EB", "ORPHAN1")]
    orig_live_ids = sd.live_link_ids

    # 4. The link the live site serves is kept; the other is deactivated.
    sd.sc.list_all = fake_list_all_factory(single, two)
    sd.live_link_ids = lambda: ({"SERVED1"}, "")
    wrote = []
    sd.sc.call = lambda method, path, data=None: wrote.append((path, data)) or {}
    try:
        sd.main(True)
    except Exception as e:                                     # noqa: BLE001
        fails.append("link dedupe raised: %r" % e)
    def deactivations(ws):
        # line_items is a READ on the same path prefix; counting it as a write
        # made this assertion fail against correct behaviour the first time.
        return [w for w in ws
                if "plink_" in w[0] and "line_items" not in w[0]
                and (w[1] or {}).get("active") in (False, "false")]

    hits = deactivations(wrote)
    if len(hits) != 1 or "plink_orphan" not in hits[0][0]:
        fails.append("expected exactly the orphan link to be deactivated, "
                      "got %r" % hits)
    elif hits[0][1].get("active") not in (False, "false"):
        fails.append("orphan was written but not deactivated: %r" % hits)

    # 5. An unreadable live site must refuse and write nothing. Unreadable is
    #    unknown, not safe.
    sd.live_link_ids = lambda: (set(), "could not read the live sitemap")
    wrote = []
    sd.main(True)
    if deactivations(wrote):
        fails.append("deactivated a link while the live site was unreadable: "
                      "%r" % wrote)

    # 6. If the live site serves BOTH, there is no obvious survivor and it
    #    must skip rather than guess.
    sd.live_link_ids = lambda: ({"SERVED1", "ORPHAN1"}, "")
    wrote = []
    sd.main(True)
    if deactivations(wrote):
        fails.append("picked a survivor when the site served both: %r" % wrote)

    sd.live_link_ids = orig_live_ids
    sd.sc.live, sd.sc.list_all, sd.sc.call, sd.sc.invalidate = (
        orig_live, orig_list_all, orig_call, orig_invalidate)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("stripe_dedupe.py: 7 case(s) passed (4 product, 3 payment link)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
