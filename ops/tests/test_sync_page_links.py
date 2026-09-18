#!/usr/bin/env python3
"""Proves ops/sync_page_links.py's links_from_stripe() does not misclassify
an active, sku-less payment link as dead.

Found 2026-09-18: `active` used to gain a url only inside the `if s:`
branch, so an active link with no sku metadata never entered `active`,
was then treated as dead by main(), and printed as an unresolvable
orphan even though it was live and correct. --apply never touches an
orphan, so no live link was ever rewritten, but the --check report was
wrong. Uses the same monkeypatch-sc.list_all pattern as
test_stripe_dedupe.py, since this module needs no real Stripe credential
to unit test, only a fake payment_links list.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sync_page_links as spl                                  # noqa: E402


def _fake_list_all(links):
    def fake(kind, params=None):
        assert kind == "payment_links"
        return list(links)
    return fake


def _with_fake_links(links, fn):
    orig = spl.sc.list_all
    spl.sc.list_all = _fake_list_all(links)
    try:
        return fn()
    finally:
        spl.sc.list_all = orig


def test_active_link_without_sku_is_not_dropped_from_active():
    sku_of, active = _with_fake_links(
        [{"url": "https://buy.stripe.com/live_no_sku",
          "active": True, "metadata": {}}],
        spl.links_from_stripe)
    assert "https://buy.stripe.com/live_no_sku" in active
    assert "https://buy.stripe.com/live_no_sku" not in sku_of


def test_active_link_with_sku_is_in_both():
    sku_of, active = _with_fake_links(
        [{"url": "https://buy.stripe.com/live_with_sku",
          "active": True, "metadata": {"sku": "WHATEVER"}}],
        spl.links_from_stripe)
    assert "https://buy.stripe.com/live_with_sku" in active
    assert sku_of["https://buy.stripe.com/live_with_sku"] == "WHATEVER"


def test_inactive_link_with_sku_is_recorded_but_not_active():
    sku_of, active = _with_fake_links(
        [{"url": "https://buy.stripe.com/retired",
          "active": False, "metadata": {"sku": "WHATEVER"}}],
        spl.links_from_stripe)
    assert sku_of["https://buy.stripe.com/retired"] == "WHATEVER"
    assert "https://buy.stripe.com/retired" not in active


def test_inactive_link_without_sku_is_in_neither():
    sku_of, active = _with_fake_links(
        [{"url": "https://buy.stripe.com/orphan",
          "active": False, "metadata": {}}],
        spl.links_from_stripe)
    assert "https://buy.stripe.com/orphan" not in sku_of
    assert "https://buy.stripe.com/orphan" not in active


def test_no_metadata_key_at_all_does_not_crash():
    sku_of, active = _with_fake_links(
        [{"url": "https://buy.stripe.com/no_metadata_field", "active": True}],
        spl.links_from_stripe)
    assert "https://buy.stripe.com/no_metadata_field" in active
    assert "https://buy.stripe.com/no_metadata_field" not in sku_of


if __name__ == "__main__":
    test_active_link_without_sku_is_not_dropped_from_active()
    test_active_link_with_sku_is_in_both()
    test_inactive_link_with_sku_is_recorded_but_not_active()
    test_inactive_link_without_sku_is_in_neither()
    test_no_metadata_key_at_all_does_not_crash()
    print("5 of 5 cases pass")
