"""The link retirement must never take down a link the live site is serving.

This is the eight day revenue outage in test form. Dropping the book from $18
to $9.99 was handled correctly for the repository: a payment link's line items
are immutable, so the superseded link is retired and a new one built. But the
live site was an older build still pointing at the old link, so retiring it
took the live buy button down, and archiving the old product force-deactivated
five more links along with it.

Two cases, and the second matters more than the first:
  1. the live site serves the link  -> refuse
  2. the live site cannot be read   -> refuse, because unknown is not unused
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "6s-success", "ops"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

import stripe_catalog as sc                                     # noqa: E402

SLUG = "dRmfZa7nEacqgIifss0kE02"
LINK = {"id": "plink_test", "url": "https://buy.stripe.com/" + SLUG}

bad = []


def run_case(label, serving, expect_deactivate):
    posted = []

    def fake_call(method, path, params=None):
        if method == "POST":
            posted.append((path, params))
        return {"data": [], "id": "plink_new", "url": "https://buy.stripe.com/new"}

    sc.call = fake_call
    sc.find_by_sku = lambda kind, sku: LINK if kind == "payment_links" else None
    sc.link_charges = lambda link_id, price_id: False   # price is stale
    sc._LIVE_READ = True
    sc._LIVE_SLUGS = serving

    # Only the retirement decision is under test. Whatever ensure_link does
    # afterwards to build the replacement needs a full product spec and is a
    # different question, so a failure past this point must not be read as the
    # link having survived.
    try:
        sc.ensure_link("BK-EBOOK", "price_new", {}, True)
    except Exception:                                           # noqa: BLE001
        pass

    killed = any(p[0] == "payment_links/plink_test"
                 and (p[1] or {}).get("active") == "false" for p in posted)
    if killed != expect_deactivate:
        bad.append("%s: link was %s but should %s have been"
                   % (label, "retired" if killed else "left alone",
                      "" if expect_deactivate else "NOT"))


# The live site is still serving it. Retiring it is an outage, not cleanup.
run_case("live site serves the link", {SLUG}, False)

# The live site could not be read. Silence is not consent: this is the exact
# shape of defect that keeps recurring here, a run that could not look treating
# its own ignorance as an all clear.
run_case("live site unreadable", None, False)

# Nothing live points at it, so retiring the superseded link is correct.
run_case("link is genuinely unused", {"someOtherSlug"}, True)

if bad:
    for b in bad:
        print("  FAIL %s" % b)
    raise SystemExit(1)
print("  ok  a superseded link is retired only when the live site is readable "
      "and is not serving it")
