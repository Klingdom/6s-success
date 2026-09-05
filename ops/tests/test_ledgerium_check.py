"""Prove the Ledgerium webhook check actually runs on the path that matters.

`ops/check_ledgerium.py`'s own docstring for gate_ledgerium says it "watches
the four prices and the webhook." That was only half true. The webhook check
lived in check_ledgerium.py's direct-key branch, reachable only when the
ambient Stripe key IS Ledgerium's own account (acct_1TG5Tu7QvDIBlvfc). By
design that never happens: Ledgerium's key lives only at
/docker/ledgerium/.env on the VPS, never in this repository's own
environment. Every realistic invocation instead calls _check_on_vps(), which
shipped ops/ledgerium_price_check.py to the VPS and ran it there, and that
file checked only the four prices, never the webhook. The one failure mode
the code's own comment names as worst case ("subscriptions would be paid for
and never activated") could happen and this gate would still print "intact."

Separately, EXPECTED/WEBHOOK/WEBHOOK_EVENTS were hand-copied into both files,
the same single-source-of-truth gap already fixed five times this week for
video_zone.zone_slug() (gate_video_slug_single_source): a price change
recorded in one file and not the other would drift silently.

Fixed by moving the checking logic into ledgerium_price_check.check(key), the
function that actually runs with Ledgerium's real key in every realistic
case, and having check_ledgerium.py import its constants and call that same
function on the rare path where it would otherwise duplicate it.

Two things have to both be true:

    ledgerium_price_check.check() must itself catch a missing/broken webhook,
    since that is the function that actually runs against the real key;
    check_ledgerium.py must hold no second copy of EXPECTED/WEBHOOK/
    WEBHOOK_EVENTS that could drift from the first.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OPS = os.path.join(ROOT, "ops")
sys.path.insert(0, OPS)

import check_ledgerium                                          # noqa: E402
import ledgerium_price_check as lpc                              # noqa: E402


def _priced_ok(pid, amount, interval):
    return {"active": True, "unit_amount": amount,
            "recurring": {"interval": interval}, "product": "prod_" + pid}


def _all_prices_and_products_healthy(path, params=None):
    if path.startswith("prices/"):
        pid = path.split("/", 1)[1]
        for _, (p, amount, interval) in lpc.EXPECTED.items():
            if p == pid:
                return _priced_ok(pid, amount, interval)
        raise AssertionError("unexpected price id requested: %s" % pid)
    if path.startswith("products/"):
        return {"active": True}
    raise AssertionError("unexpected path requested: %s" % path)


def test_single_source_of_truth_no_second_copy():
    assert check_ledgerium.EXPECTED is lpc.EXPECTED
    assert check_ledgerium.WEBHOOK is lpc.WEBHOOK
    assert check_ledgerium.WEBHOOK_EVENTS is lpc.WEBHOOK_EVENTS


def test_check_catches_a_missing_webhook():
    """The exact regression this file exists to prevent."""
    def fake_api(key, path, params=None):
        if path == "webhook_endpoints":
            return {"data": []}
        return _all_prices_and_products_healthy(path, params)

    old = lpc._api
    lpc._api = fake_api
    try:
        problems = lpc.check("fake_key")
    finally:
        lpc._api = old
    assert any("webhook endpoint is missing" in p for p in problems), problems


def test_check_catches_a_disabled_webhook_and_missing_events():
    def fake_api(key, path, params=None):
        if path == "webhook_endpoints":
            return {"data": [{"url": lpc.WEBHOOK, "status": "disabled",
                              "enabled_events": ["checkout.session.completed"]}]}
        return _all_prices_and_products_healthy(path, params)

    old = lpc._api
    lpc._api = fake_api
    try:
        problems = lpc.check("fake_key")
    finally:
        lpc._api = old
    assert any("Ledgerium webhook is disabled" in p for p in problems), problems
    assert any("missing events" in p for p in problems), problems


def test_check_reports_clean_when_everything_matches():
    def fake_api(key, path, params=None):
        if path == "webhook_endpoints":
            return {"data": [{"url": lpc.WEBHOOK, "status": "enabled",
                              "enabled_events": sorted(lpc.WEBHOOK_EVENTS)}]}
        return _all_prices_and_products_healthy(path, params)

    old = lpc._api
    lpc._api = fake_api
    try:
        problems = lpc.check("fake_key")
    finally:
        lpc._api = old
    assert problems == [], problems


def test_check_ledgerium_direct_branch_reuses_the_same_check():
    """If the ambient key were ever Ledgerium's own, it must not fall back
    to a second, unmaintained copy of the price/webhook logic."""
    def fake_api(key, path, params=None):
        if path == "webhook_endpoints":
            return {"data": []}
        return _all_prices_and_products_healthy(path, params)

    old_key = check_ledgerium._key
    old_acct = check_ledgerium._account_id
    old_api = lpc._api
    check_ledgerium._key = lambda: "sk_live_fake"
    check_ledgerium._account_id = lambda key: check_ledgerium.LEDGERIUM_ACCOUNT
    lpc._api = fake_api
    try:
        r = check_ledgerium.check()
    finally:
        check_ledgerium._key = old_key
        check_ledgerium._account_id = old_acct
        lpc._api = old_api
    assert r["state"] == "problems", r
    assert any("webhook endpoint is missing" in p for p in r["problems"]), r


if __name__ == "__main__":
    test_single_source_of_truth_no_second_copy()
    test_check_catches_a_missing_webhook()
    test_check_catches_a_disabled_webhook_and_missing_events()
    test_check_reports_clean_when_everything_matches()
    test_check_ledgerium_direct_branch_reuses_the_same_check()
    print("ok  ledgerium_price_check.check() catches a missing/broken "
          "webhook, and check_ledgerium.py holds no second copy of it")
