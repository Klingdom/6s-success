#!/usr/bin/env python3
"""
Prove stripe_dedupe.py's dedupe_links() the way its own docstring claims,
directly: a real, live, money-adjacent function (it deactivates payment
links) shipped 2026-09-23 (`a5f9bc4f`) with no committed regression test,
only a same-day manual proof described in the commit message ("that refusal
was proved by stubbing the fetch and watching it report a note instead of a
confident empty set"). Found while fixing the sibling test this commit broke
(test_stripe_dedupe.py's Case 2 did not stub the new "payment_links" list_all
kind, so a single-product account with no product duplicates started raising
AssertionError instead of completing).

What this proves, each fail-then-pass provable against a reverted function:

  * no active links at all: no-op, no Stripe call of any kind
  * one active link per sku: no-op, no Stripe call of any kind
  * an unreadable live site: REFUSES before touching anything, not "found
    zero duplicates" (unknown is not safe)
  * a real duplicate where the live site serves neither or both candidate
    links: SKIPPED, not guessed at
  * a real duplicate where the live site serves exactly one: --check reports
    it and makes no write call; --apply deactivates only the orphan(s), by
    id, and leaves the served link untouched

Run:  python ops/tests/test_stripe_dedupe_links.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import stripe_dedupe as sd                                    # noqa: E402


def link(lid, sku, url_id, active=True):
    return {"id": lid, "active": active,
            "metadata": {"sku": sku},
            "url": "https://buy.stripe.com/" + url_id}


def _run(links, served, apply_it, note="", price_amount=1900):
    """Drive dedupe_links() against a fake Stripe and a fake live site.

    Returns (result, calls) where calls is every sc.call() made, so a test
    can assert not just the return value but that no write happened when
    none should have.
    """
    orig_list_all, orig_call, orig_live_link_ids = (
        sd.sc.list_all, sd.sc.call, sd.live_link_ids)
    calls = []

    def fake_list_all(kind, params=None):
        if kind == "payment_links":
            return links
        raise AssertionError(f"unexpected kind: {kind}")

    def fake_call(method, path, data=None):
        calls.append((method, path, data))
        if method == "GET" and "line_items" in path:
            return {"data": [{"price": {"unit_amount": price_amount}}]}
        return {}

    sd.sc.list_all = fake_list_all
    sd.sc.call = fake_call
    sd.live_link_ids = lambda: (served, note)
    try:
        result = sd.dedupe_links(sd.sc, apply_it)
        return result, calls
    finally:
        sd.sc.list_all, sd.sc.call, sd.live_link_ids = (
            orig_list_all, orig_call, orig_live_link_ids)


def main() -> int:
    fails = []

    # 1. No active links at all: no-op, and dedupe_links must not even ask
    #    which link the live site serves (nothing to decide between).
    r, calls = _run([], served=set(), apply_it=False)
    if r != 0 or calls:
        fails.append(f"empty account not a clean no-op: result={r} calls={calls}")

    # 2. One active link per sku, no duplicates: no-op, no Stripe call.
    r, calls = _run([link("l1", "BK-EB", "abc"), link("l2", "CN-VIRTUAL", "def")],
                     served=set(), apply_it=False)
    if r != 0 or calls:
        fails.append(f"no-duplicate account not a clean no-op: result={r} calls={calls}")

    # 3. A real duplicate, but the live site is unreadable: REFUSE, not
    #    "found none". Must not read line_items or write anything either.
    dupe = [link("l_old", "PACK-HOUSE", "old123"), link("l_new", "PACK-HOUSE", "new456")]
    r, calls = _run(dupe, served=set(), apply_it=True,
                     note="could not read the live sitemap")
    if r != 1 or calls:
        fails.append(f"unreadable site did not refuse cleanly: result={r} calls={calls}")

    # 4. A real duplicate, live site serves NEITHER candidate (a third,
    #    already-known link, or none): skip, do not guess, no write call.
    r, calls = _run(dupe, served={"unrelated999"}, apply_it=True)
    writes = [c for c in calls if c[0] == "POST"]
    if writes:
        fails.append(f"ambiguous survivor (serves neither) still wrote: {writes}")

    # 5. A real duplicate, live site serves BOTH: equally ambiguous, skip,
    #    no write call.
    r, calls = _run(dupe, served={"old123", "new456"}, apply_it=True)
    writes = [c for c in calls if c[0] == "POST"]
    if writes:
        fails.append(f"ambiguous survivor (serves both) still wrote: {writes}")

    # 6. A real duplicate, live site serves exactly one: --check reports it
    #    (reads price line items to check for a mismatch) but writes nothing.
    r, calls = _run(dupe, served={"new456"}, apply_it=False)
    writes = [c for c in calls if c[0] == "POST"]
    if writes:
        fails.append(f"--check made a write call: {writes}")
    if r != 0:
        fails.append(f"--check on a real duplicate returned {r}, expected 0")

    # 7. Same duplicate, --apply: deactivates only the orphan (l_old), by
    #    id, and never touches the served link (l_new).
    r, calls = _run(dupe, served={"new456"}, apply_it=True)
    writes = [c for c in calls if c[0] == "POST"]
    if r != 1:
        fails.append(f"--apply on one real duplicate returned {r}, expected 1 change")
    if [c[1] for c in writes] != ["payment_links/l_old"]:
        fails.append(f"--apply wrote the wrong link(s): {writes}")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("stripe_dedupe.py dedupe_links(): 7 case(s) passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
