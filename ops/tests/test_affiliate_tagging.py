#!/usr/bin/env python3
"""
Prove the tagged-link path works, before there is any money riding on it.

WHY THIS EXISTS
---------------
1,725 retailer links are live across 114 zone pages and the kit page,
all of them to exactly two merchants: target.com (1,535) and homedepot.com (190). Every one
of them is currently a plain link that earns nothing, and that is correct: no
programme is approved, so `affiliate.build_link()` returns None and
`zone_supplies._link()` falls back to the plain URL and labels it "plain".

The whole affiliate mechanism therefore has NEVER EXECUTED. Not once, not in
production and not in a test. It runs for the first time on the day a programme
is approved, which is also the first day it can lose money, and
`build_link()`'s own docstring names the failure mode exactly:

    An untracked link earns nothing and looks identical to a working one, so
    the failure would be silent and permanent.

That is the definition of a path that must not be discovered at run time. Amazon
is the closest to approving (status "verification pending", and it is the one
network that accepts small publishers), so the day this matters may be soon.

WHAT IS PROVED HERE, with fixtures rather than a live account:

    the untagged present:  no approved programme means a plain URL, never a
                           half-tagged one;
    the Amazon shape:      ?tag=<publisher_id>, and &tag= when the target
                           already carries a query string, which is the case
                           that silently produces a broken URL if it is wrong;
    the network shape:     a deep_link_template gets the target URL-encoded
                           into {url} and the publisher id into {id};
    the seam:              zone_supplies._link(), the function the page
                           generator actually calls, returns kind "tracked"
                           rather than "plain" once a programme is approved.

The last one is the point. The first three could all pass while the generator
still emits plain links, because nothing would have exercised the join between
them.

Run:  python ops/tests/test_affiliate_tagging.py
"""
import io
import json
import os
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import affiliate as A                                            # noqa: E402
import zone_supplies as Z                                        # noqa: E402


def with_accounts(accounts: dict):
    """Swap affiliate.accounts() for a fixture, restoring it afterwards.

    Patching the reader rather than the file on disk, so a failed run can never
    leave a fake approved programme in ops/affiliate-accounts.json. That file
    decides whether real links carry a real publisher id; a test that can
    corrupt it is more dangerous than the bug it is looking for.
    """
    real = A.accounts

    class Ctx:
        def __enter__(self):
            A.accounts = lambda: accounts
            return self

        def __exit__(self, *a):
            A.accounts = real
            return False
    return Ctx()


AMAZON_OK = {"amazon": {"status": "approved", "publisher_id": "6ssuccess-20",
                        "affiliate_network": "amazon", "deep_link_template": ""}}
TARGET_OK = {"target": {"status": "approved", "publisher_id": "PID999",
                        "affiliate_network": "impact",
                        "deep_link_template":
                            "https://track.example/c/{id}?u={url}"}}
NETWORK_OK = {"lowes": {"status": "approved", "publisher_id": "PID123",
                        "affiliate_network": "impact",
                        "deep_link_template":
                            "https://track.example/c/{id}?u={url}"}}


def main() -> int:
    fails = []

    # 1. The untagged present. This is what production does today, and it has
    #    to keep doing it: a bare merchant URL returned from build_link() would
    #    be indistinguishable from a tagged one and would earn nothing forever.
    if A.build_link("amazon", "https://www.amazon.com/dp/B000") is not None:
        fails.append("build_link returned a link with no approved programme; "
                     "an untracked link that looks tracked is the exact "
                     "failure its own docstring warns about")

    # 2. The Amazon shape, including the case that breaks quietly.
    with with_accounts(AMAZON_OK):
        plain = A.build_link("amazon", "https://www.amazon.com/dp/B000")
        if plain != "https://www.amazon.com/dp/B000?tag=6ssuccess-20":
            fails.append("amazon tag on a clean URL: got %r" % plain)

        # A target that already has a query string. Using "?" here a second
        # time produces a URL Amazon reads as one parameter named
        # "s=x?tag", the tag is lost, and the link still works for the
        # customer. It earns nothing and looks perfect.
        q = A.build_link("amazon", "https://www.amazon.com/s?k=broom")
        if q != "https://www.amazon.com/s?k=broom&tag=6ssuccess-20":
            fails.append("amazon tag on a URL that already has a query "
                         "string: got %r" % q)
        if q and q.count("?") != 1:
            fails.append("amazon tagged URL has %d question marks: %r"
                         % (q.count("?"), q))

        # An approved programme still must not invent a link out of nothing.
        if A.build_link("amazon", "") is not None:
            fails.append("build_link invented a link from an empty target")
        if A.build_link("walmart", "https://www.walmart.com/ip/1") is not None:
            fails.append("build_link tagged a merchant that is not approved")

    # 3. The network shape. The target has to be URL-encoded into the template,
    #    or the tracking host reads our query string as its own.
    with with_accounts(NETWORK_OK):
        target = "https://www.lowes.com/pd/thing?store=1&size=L"
        got = A.build_link("lowes", target)
        want = "https://track.example/c/PID123?u=" + urllib.parse.quote(
            target, safe="")
        if got != want:
            fails.append("deep link template: got %r want %r" % (got, want))
        if got and ("&size=L" in got.split("u=", 1)[-1]):
            fails.append("deep link template left the target unencoded, so the "
                         "tracker will read our parameters as its own: %r" % got)

    # 4. THE SEAM. zone_supplies._link() is what the page generator calls, and
    #    it is where a correct build_link() can still produce a plain page.
    # target.com, not amazon.com, and that choice is the finding.
    # zone_supplies._link() refuses any host privacy.html does not name, so an
    # Amazon row returns ("", "") today no matter what build_link() does. The
    # site links exactly two merchants, target.com and homedepot.com, and
    # privacy.html names exactly those two. See group 6 below, which pins that as a known state rather than leaving it to be
    # rediscovered on approval day.
    row = {"Affiliate URL": "https://www.target.com/p/broom/-/A-123",
           "Link Status": "verified 2026-09-01",
           "Merchant": "Target"}
    href, kind = Z._link(row)
    if kind != "plain":
        fails.append("with nothing approved, _link() reported kind %r, "
                     "expected 'plain'" % kind)

    with with_accounts(TARGET_OK):
        href, kind = Z._link(row)
        if kind != "tracked":
            fails.append("with target approved, the generator's own _link() "
                         "still reported %r: approval would not tag a single "
                         "one of the 1,725 live links" % kind)
        if "track.example" not in (href or ""):
            fails.append("_link() returned an untracked href: %r" % href)

    # 5. The gates that stop a bad row publishing at all must survive approval.
    with with_accounts(TARGET_OK):
        unverified = dict(row, **{"Link Status": "pending"})
        if Z._link(unverified) != ("", ""):
            fails.append("an unverified row published once a programme was "
                         "approved; approval must not relax the link checks")

    # 6. WHAT APPROVAL WOULD ACTUALLY BUY, pinned rather than assumed.
    #
    # The site links two merchants and privacy.html names those same two, so the
    # disclosure gate and the link set agree today. They agree because both grew
    # together, not because anything keeps them in step.
    #
    # Amazon is the programme most likely to approve, and amazon.com is named
    # nowhere in privacy.html, so _link() would return ("", "") for every Amazon
    # row however correct build_link() is. Approval alone would publish nothing.
    # That is not a bug to fix here, because adding Amazon links is a product
    # decision about which merchant we recommend, not a code change. It is
    # recorded so that approval day starts with the real list of what is needed.
    amazon_row = {"Affiliate URL": "https://www.amazon.com/dp/B000",
                  "Link Status": "verified 2026-09-01", "Merchant": "Amazon"}
    with with_accounts(AMAZON_OK):
        if Z._link(amazon_row) != ("", ""):
            fails.append("amazon.com now publishes, so privacy.html has changed "
                         "and this test's note about approval day is stale: "
                         "reread it rather than deleting this case")
    linked = {"target.com", "homedepot.com"}
    for host in linked:
        if not Z._host_disclosed("https://www." + host + "/x"):
            fails.append("%s is linked on the site but privacy.html does not "
                         "name it, so those links stopped publishing" % host)

    for f in fails:
        print("  FAIL  %s" % f)
    if fails:
        print("  %d group(s) failed" % len(fails))
    else:
        print("  ok  the tagged path works end to end: no programme means a "
              "plain link, Amazon tags cleanly on both URL shapes, a network "
              "template encodes its target, and the generator's own seam "
              "reports 'tracked'")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
