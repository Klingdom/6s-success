#!/usr/bin/env python3
"""
Prove preflight's check_payment_links_nofollow() refuses a followable Stripe
checkout link, and stays silent for an ordinary outbound link.

WHY THIS EXISTS
---------------
A Stripe Payment Link creates a Checkout Session when its page is OPENED, not
when a card is entered. A crawler that follows one has opened a checkout, and
the account records an expired unpaid session for it.

Found 2026-09-29 while asking a different question. buy-click had fired 11
times from 9 visitors all time and one person had ever paid, so the suspicion
was a dead checkout. It was not: the payment links were all live against the
real account. The session list showed 12 checkout sessions created on
2026-09-15, a day the website recorded ZERO buy-clicks, so something was
opening checkouts without touching a buy button. At that moment 420 <a> tags
across 171 shipped pages pointed at buy.stripe.com and not one carried
rel="nofollow"; site/shop.html alone had 126.

The cost that matters is not crawl budget. "Sessions created versus paid" is
the only conversion instrument this business has that does not need Search
Console, and it was being filled with rows nobody could attribute. A
conversion rate computed from it would have been wrong pessimistically, and it
would have looked like evidence.

Run:  python ops/tests/test_payment_links_nofollow.py
"""
import glob
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight as P                                          # noqa: E402

PAY = "https://buy.stripe.com/bJeeV623kcky0Jk4NO0kF0S"


def case_nofollowed_payment_link_is_silent():
    body = '<a href="%s" rel="nofollow noopener">Buy</a>' % PAY
    assert P.check_payment_links_nofollow({"a.html": body}) == []


def case_noopener_alone_is_not_enough():
    body = '<a href="%s" rel="noopener">Buy</a>' % PAY
    out = P.check_payment_links_nofollow({"a.html": body})
    assert len(out) == 1 and "a.html" in out[0], out
    assert "unpaid session" in out[0], out


def case_no_rel_at_all_is_caught():
    out = P.check_payment_links_nofollow({"a.html": '<a href="%s">Buy</a>' % PAY})
    assert len(out) == 1, out


def case_ordinary_outbound_link_is_left_alone():
    for href in ("https://www.youtube.com/@6SSuccess",
                 "https://www.linkedin.com/in/philipkling",
                 "downloads/sample.pdf", "#"):
        body = '<a href="%s" rel="noopener">x</a>' % href
        assert P.check_payment_links_nofollow({"a.html": body}) == [], href


def case_nofollow_among_other_rel_values_counts():
    for rel in ("nofollow", "noopener nofollow", "nofollow noreferrer",
                "NOFOLLOW noopener"):
        body = '<a href="%s" rel="%s">Buy</a>' % (PAY, rel)
        assert P.check_payment_links_nofollow({"a.html": body}) == [], rel


def case_every_offending_link_on_a_page_is_named():
    body = ('<a href="%s" rel="noopener">A</a>'
            '<a href="%s" rel="nofollow">B</a>'
            '<a href="%s">C</a>') % (PAY, PAY, PAY)
    out = P.check_payment_links_nofollow({"shop.html": body})
    assert len(out) == 2, out


def case_the_real_shipped_site_is_clean():
    bodies = {}
    site = os.path.join(ROOT, "site")
    for fp in sorted(glob.glob(os.path.join(site, "**", "*.html"),
                               recursive=True)):
        bodies[os.path.relpath(fp, site).replace("\\", "/")] = \
            io.open(fp, encoding="utf-8", errors="replace").read()
    assert bodies, "no pages under site/ at all"
    linked = sum(1 for b in bodies.values() if "buy.stripe.com" in b)
    assert linked > 50, ("expected many pages to carry a payment link, "
                         "found %d" % linked)
    out = P.check_payment_links_nofollow(bodies)
    assert out == [], out[:3]


def case_site_js_shop_button_carries_nofollow():
    """The shop's buttons are built at runtime, so the template counts too."""
    js = os.path.join(ROOT, "site", "assets", "js", "site.js")
    if not os.path.exists(js):
        print("  site.js absent, NOT VERIFIED.")
        return
    body = io.open(js, encoding="utf-8", errors="replace").read()
    if "p.buy" not in body:
        print("  site.js no longer builds buy buttons, NOT VERIFIED.")
        return
    import re
    for m in re.finditer(r'<a\b[^>]*?p\.buy[^>]*?>', body):
        assert "nofollow" in m.group(0), m.group(0)


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
