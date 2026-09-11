#!/usr/bin/env python3
"""
Prove check_affiliate_trigger counts only real retailer clicks, not every
outbound click.

T2 (PLAN-AFFILIATE-MONETISATION.md section 7) is a retailer-click trigger:
"measured retailer-click count reaches 60 in a trailing 90 days". measure.js
fires the identical `outbound-click` event for ANY external, non-Stripe link,
and site/method.html has linked the live YouTube channel since 2026-09-10.
Before this fix, reading()'s SQL counted every outbound-click row regardless
of host, so a reader clicking the YouTube link would count toward the
Amazon-application threshold alongside a real Target or Home Depot click,
exactly the wrong evidence for that decision. Reproduced directly: with the
host filter removed, a query built the same way as the pre-fix code has no
way to tell a youtube.com row from a target.com row.

Run:  python ops/tests/test_check_affiliate_trigger.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import check_affiliate_trigger as T                             # noqa: E402
import experiments as X                                         # noqa: E402
import product_links as PL                                      # noqa: E402


def main() -> int:
    fails = []

    # Case 1: retailer_hosts() reads the real MERCHANTS config and returns
    # the actual retailer hosts, never the channel this trigger must exclude.
    hosts = T.retailer_hosts()
    if "youtube.com" in hosts:
        fails.append("retailer_hosts() must never include youtube.com, "
                      "which is not a retailer link")
    if not {"target.com", "homedepot.com"} <= set(hosts):
        fails.append("retailer_hosts() must include the real, live "
                      f"retailer hosts, got {hosts}")

    # Case 2: reading()'s own SQL must restrict to those hosts, not accept
    # every outbound-click row. Capture the SQL text rather than hit a real
    # database.
    captured = {}
    real_umami_rows = X.umami_rows

    def fake_umami_rows(sql, timeout=60):
        captured["sql"] = sql
        return [["0", "0"]]

    X.umami_rows = fake_umami_rows
    try:
        T.reading()
    finally:
        X.umami_rows = real_umami_rows
    sql = captured.get("sql", "")
    if "youtube.com" in sql:
        fails.append("the SQL must never name youtube.com as a counted host")
    if "'target.com'" not in sql:
        fails.append(f"the SQL must restrict to real retailer hosts, got:\n{sql}")
    if "data_key = 'host'" not in sql:
        fails.append("the SQL must filter on the event's own host field, "
                      "not accept any outbound-click row regardless of host")

    # Case 3: an empty MERCHANTS config must read as unreadable, never as a
    # silent "count everything" fallback.
    real_merchants = PL.MERCHANTS
    PL.MERCHANTS = {}
    try:
        r = T.reading()
    finally:
        PL.MERCHANTS = real_merchants
    if r["ok"]:
        fails.append("an empty retailer-host list must report unreadable, "
                      f"not a measured count, got {r}")

    if fails:
        print(f"FAIL: {len(fails)} of 3 cases")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 3 of 3 cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
