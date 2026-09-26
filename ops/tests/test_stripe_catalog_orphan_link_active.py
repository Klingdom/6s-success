"""Prove ensure_link() never adopts a retired payment link as a SKU's buy link.

`ensure_link()`'s orphan-adoption loop exists to attach this script's sku
metadata to payment links Stripe already held before this file existed. It
matched an orphan link by price alone and never checked whether that link was
still active. A retired link that happened to sell the same price as a
current SKU would be tagged with that SKU's metadata and its URL returned
from ensure_link(). Traced the consequence rather than assuming the worst
shape: `sync_site_links()` re-reads payment links itself and only ever
writes an active one into the site's buy links, so the dead link is never
published directly. What actually happens is worse in a different way: once
tagged, `find_by_sku()` keeps returning that same inactive link as this SKU's
match on every future run (it prefers active, then falls back to inactive
rather than ignoring it), so `ensure_link()` returns early believing the SKU
already has a link and never creates a real one. `sync_site_links()` then
either strips an existing buy button (loudly, "no active payment link ...
carries that sku") or the SKU simply never gets one: a silent, persistent,
self-reinforcing loss of that SKU's ability to be bought, until someone edits
Stripe by hand. Found 2026-09-26 cold-reading stripe_catalog.py; no evidence
yet of a specific SKU actually hit by it, but the account has retired well
over a hundred links by hand since 2026-08-31 (see stripe_catalog.py's own
find_by_sku docstring), so an inactive orphan sharing a price with a live SKU
is a real, not hypothetical, possibility, and CLAUDE.md 0.4 says unknown is
not unused.

Run:  python ops/tests/test_stripe_catalog_orphan_link_active.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OPS = os.path.join(ROOT, "ops")
sys.path.insert(0, OPS)

import stripe_catalog                                            # noqa: E402


def _rig(monkeypatch, orphan_active):
    """Wire fakes for a single ensure_link() call: no link carries this SKU's
    metadata yet, and one orphan link (no sku metadata) sells the same price,
    with the given active state."""
    calls = []

    def fake_list_all(kind, params=None):
        if kind == "payment_links":
            return [{"id": "plink_orphan", "active": orphan_active,
                      "metadata": {}, "url": "https://buy.stripe.com/orphan"}]
        return []

    def fake_call(method, path, data=None):
        calls.append((method, path, data))
        if path.startswith("payment_links/") and path.endswith("/line_items"):
            return {"data": [{"price": {"id": "price_123"}}]}
        if method == "POST" and path == "payment_links":
            return {"id": "plink_new", "url": "https://buy.stripe.com/new"}
        return {}

    monkeypatch(stripe_catalog, "list_all", fake_list_all)
    monkeypatch(stripe_catalog, "call", fake_call)
    monkeypatch(stripe_catalog, "find_by_sku",
                lambda kind, sku, adopt_names=None: None)
    return calls


class _Patcher:
    """Tiny monkeypatch substitute so this file has no third-party dependency."""

    def __init__(self):
        self._saved = []

    def __call__(self, obj, name, value):
        self._saved.append((obj, name, getattr(obj, name)))
        setattr(obj, name, value)

    def restore(self):
        for obj, name, value in reversed(self._saved):
            setattr(obj, name, value)


def case_inactive_orphan_link_is_never_adopted():
    p = _Patcher()
    try:
        calls = _rig(p, orphan_active=False)
        spec = {"kind": "digital", "deliverable": "x"}
        url = stripe_catalog.ensure_link("TEST-SKU", "price_123", spec, apply_it=True)
        assert url == "https://buy.stripe.com/new", url
        assert not any(c[1] == "payment_links/plink_orphan" for c in calls), (
            "a retired orphan link must never be tagged with a live SKU")
    finally:
        p.restore()


def case_active_orphan_link_is_still_adopted():
    """The adoption path itself must keep working for a genuinely live,
    hand-made link, or this fix would silently break the migration case it
    exists for."""
    p = _Patcher()
    try:
        _rig(p, orphan_active=True)
        spec = {"kind": "digital", "deliverable": "x"}
        url = stripe_catalog.ensure_link("TEST-SKU", "price_123", spec, apply_it=True)
        assert url == "https://buy.stripe.com/orphan", url
    finally:
        p.restore()


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
    print("stripe_catalog.ensure_link() orphan-adoption: %d case(s) passed" % len(cases))
    return 0


if __name__ == "__main__":
    sys.exit(main())
