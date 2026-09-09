#!/usr/bin/env python3
"""
Watch the one trigger that would restart the affiliate argument.

PLAN-AFFILIATE-MONETISATION.md settles the question: affiliate earns about $7 a
month at the traffic level where the services line reaches $20,000, so it is an
option to hold open rather than a revenue line to plan. It authorises exactly
one application, to Amazon Associates and nothing else, and only when a written
trigger fires:

    T2: measured retailer-click count reaches 60 in a trailing 90 days,
        internal traffic excluded.

Then it says "re-litigate in June 2027 or when a trigger fires, not monthly",
which is the right instruction and has a hole in it: nothing was watching. A
trigger nobody evaluates is a decision that quietly becomes a memory, and this
plan's whole value is that it stops the argument being had every month on
feelings.

So this evaluates T2 against the real event stream, and says one of three
things: not fired and how far off, FIRED and what to do, or that it could not
look. The third matters as much as the others. This runs in CI, where there is
no ssh key and no database, and a checker that returns "0 of 60" when it cannot
see the data is worse than no checker, because zero is also the real answer
today and the two are indistinguishable.

WHAT COUNTS AS A CLICK HERE
---------------------------
Events named outbound-click, which measure.js fires on any link leaving the
site that is not Stripe, carrying the retailer host and the page type.

Excluded: anything labelled who=internal (a browser we marked ours) or
who=automated (headless or webdriver-controlled, stamped automatically since
2026-09-08). The trigger says "internal traffic excluded" and means it: on
2026-09-08 a single automated session produced 229 of 241 zone scroll events in
sixteen minutes, and a trigger that counted those would have fired on a crawler.

    python ops/check_affiliate_trigger.py
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

TARGET = 60
WINDOW_DAYS = 90


def reading() -> dict:
    """{'ok': bool, 'clicks': int, 'people': int, 'why': str}.

    ok is False when the database could not be read, never when the count is
    simply low. The caller must be able to tell "nobody clicked" from "nobody
    looked", which is the distinction this repository has paid for repeatedly.
    """
    try:
        import experiments as X
    except Exception as e:                                       # noqa: BLE001
        return {"ok": False, "clicks": 0, "people": 0,
                "why": "cannot import experiments (%s)" % str(e)[:70]}
    sql = """
        select count(*), count(distinct e.session_id)
        from website_event e
        left join event_data w
               on w.website_event_id = e.event_id and w.data_key = 'who'
        where e.website_id = %s
          and e.event_name = 'outbound-click'
          and e.created_at > now() - interval '%d days'
          and coalesce(w.string_value, '') not in ('internal', 'automated')
    """ % (X.W, WINDOW_DAYS)
    try:
        rows = X.umami_rows(sql)
    except Exception as e:                                       # noqa: BLE001
        return {"ok": False, "clicks": 0, "people": 0,
                "why": "analytics unreadable (%s)" % str(e)[:70]}
    if not rows or not rows[0]:
        return {"ok": False, "clicks": 0, "people": 0,
                "why": "the query returned nothing, which is not the same as zero"}
    return {"ok": True, "clicks": int(rows[0][0]), "people": int(rows[0][1]),
            "why": ""}


def verdict(r: dict) -> tuple:
    """(fired, line). fired is None when it could not be evaluated."""
    if not r["ok"]:
        return None, ("T2 NOT EVALUATED: %s. This is not a reading of zero."
                      % r["why"])
    if r["clicks"] >= TARGET:
        return True, ("T2 HAS FIRED: %d outbound retailer click(s) from %d "
                      "visitor(s) in the last %d days, against a threshold of "
                      "%d. PLAN-AFFILIATE-MONETISATION.md authorises ONE "
                      "action: apply to Amazon Associates, and nothing else. "
                      "Note amazon.com is not named in privacy.html, so no "
                      "Amazon link can publish until it is."
                      % (r["clicks"], r["people"], WINDOW_DAYS, TARGET))
    return False, ("T2 not fired: %d of %d outbound retailer click(s) in the "
                   "last %d days, from %d visitor(s), internal and automated "
                   "excluded. No application is authorised."
                   % (r["clicks"], TARGET, WINDOW_DAYS, r["people"]))


def main() -> int:
    r = reading()
    fired, line = verdict(r)
    print("  %s" % line)
    if fired is None:
        return 0          # unreadable is reported, not treated as a failure
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
