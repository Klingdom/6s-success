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
Events named outbound-click, which measure.js fires on ANY link leaving the
site that is not Stripe, not only a retailer one: site/method.html has linked
the live YouTube channel since 2026-09-10 (BACKLOG-2026-09-07.md item, "the
site linked to its own live YouTube channel nowhere... fixed"), and that link
fires the identical event with a youtube.com host. T2 is a retailer-click
trigger, not an any-outbound-click trigger, so this reader also requires the
event's own host to be one of the retailers ops/product_links.py actually
searches (read from MERCHANTS there, not duplicated here, so a retailer added
or retired in that file is reflected here automatically). Without that filter,
a reader clicking the YouTube link would count toward the Amazon-application
threshold, which is exactly the wrong evidence for that decision.

Excluded: anything labelled who=internal (a browser we marked ours) or
who=automated (headless or webdriver-controlled, stamped automatically since
2026-09-08). The trigger says "internal traffic excluded" and means it: on
2026-09-08 a single automated session produced 229 of 241 zone scroll events in
sixteen minutes, and a trigger that counted those would have fired on a crawler.

    python ops/check_affiliate_trigger.py
"""
from __future__ import annotations

import os
import re
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

TARGET = 60
WINDOW_DAYS = 90


def retailer_hosts() -> tuple:
    """The real retailer hosts our own outbound links point at.

    Read from product_links.MERCHANTS rather than a second hardcoded list, so
    a retailer added or retired there cannot drift out of step with what this
    trigger counts.
    """
    import product_links as PL
    hosts = set()
    for m in PL.MERCHANTS.values():
        h = urllib.parse.urlparse(m["search"]).hostname or ""
        h = re.sub(r"^www\.", "", h)
        if h:
            hosts.add(h)
    return tuple(sorted(hosts))


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
    hosts = retailer_hosts()
    if not hosts:
        return {"ok": False, "clicks": 0, "people": 0,
                "why": "product_links.MERCHANTS is empty; no retailer host "
                       "to count a click against"}
    host_list = ",".join("'%s'" % h for h in hosts)
    sql = """
        select count(*), count(distinct e.session_id)
        from website_event e
        left join event_data w
               on w.website_event_id = e.event_id and w.data_key = 'who'
        where e.website_id = %s
          and e.event_name = 'outbound-click'
          and e.created_at > now() - interval '%d days'
          and coalesce(w.string_value, '') not in ('internal', 'automated')
          and exists (
                select 1 from event_data h
                where h.website_event_id = e.event_id
                  and h.data_key = 'host'
                  and h.string_value in (%s)
              )
    """ % (X.W, WINDOW_DAYS, host_list)
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
