"""Guard the three things about the corporate page that would cost real money.

WHY THIS EXISTS
---------------
site/corporate.html is the only page on this site aimed at a buyer with a
budget, and REVENUE-REVIEW-2026-09-04.md is blunt about why that matters: the
catalogue is 97% priced between $4 and $19, and at a 2% conversion the $4 packs
would need a quarter of a million visitors a month to reach $20,000. Corporate
Lean 6S is the one line that needs no consumer traffic at all.

Three properties carry that, and all three are the kind that break silently:

  1. NO PRICE. Corporate Lean 6S is scoped per engagement and nothing has ever
     been charged for it. The $5,000 to $15,000 in the revenue review is a
     market range read off the industry, and the review says so itself. A
     figure on this page would be somebody else's benchmark presented as our
     price, which is CLAUDE.md section 8, on the page where the reader is most
     likely to check.

  2. THE ENQUIRY REACHES A HUMAN. The page has no server behind it. It composes
     a mailto, and ops/service_orders.py picks the message out of the support@
     inbox by matching a service phrase. If the subject stops matching, or the
     body starts matching one of the other two services first, a corporate
     lead is either dropped or forwarded as a household booking. Neither
     failure is visible from the page.

  3. THE CATALOGUE AND THE PAGE AGREE. CN-CORP must still have price: null, no
     payment link, and a quote route pointing at this page. A "Request a quote"
     badge that leads nowhere is the exact defect this work was done to fix,
     and it is one careless catalogue edit away from returning.

Fast and deterministic on purpose: it reads files and calls two functions, so
it runs everywhere, including CI with no browser.
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OPS = os.path.join(ROOT, "ops")
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, OPS)

PAGE = os.path.join(SITE, "corporate.html")
DATA_JS = os.path.join(SITE, "assets", "js", "data.js")


def main() -> int:
    bad = []

    if not os.path.exists(PAGE):
        print("  FAIL site/corporate.html does not exist. Run "
              "ops/build_corporate.py.")
        return 1

    html = io.open(PAGE, encoding="utf-8").read()
    import build_corporate as BC
    import service_orders as SO

    # --- 1. no price, in prose or in markup ------------------------------
    figures = re.findall(r"\$\s?\d[\d,\.]*", html)
    if figures:
        bad.append("a dollar figure is on the corporate page: %r" % figures[:3])

    ld = re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
                   html, re.S)
    if not ld:
        bad.append("the corporate page carries no JSON-LD at all")
    else:
        try:
            graph = json.loads(ld.group(1))
        except ValueError as e:
            graph = None
            bad.append("the corporate page's JSON-LD does not parse: %s" % e)
        if graph:
            types = [n.get("@type") for n in graph.get("@graph", [])]
            for want in ("Service", "FAQPage", "BreadcrumbList"):
                if want not in types:
                    bad.append("JSON-LD is missing a %s node" % want)
            blob = json.dumps(graph).lower()
            # An invented price is worse in machine-readable form than in
            # prose, because that is the form an answer engine repeats.
            for key in ('"price"', '"pricerange"', '"lowprice"',
                        '"highprice"'):
                if key in blob:
                    bad.append("JSON-LD asserts %s for a quote-only service"
                               % key)

    # --- 2. the enquiry actually routes to a human -----------------------
    if SO.which_service(BC.SUBJECT) != "Corporate Lean 6S":
        bad.append("the subject %r no longer routes to Corporate Lean 6S, so "
                   "ops/service_orders.py would not forward the enquiry"
                   % BC.SUBJECT)

    # The composed body's own labels must not carry another service's phrase.
    body_text = (" ".join(l for l, _ in BC.BODY_FIELDS) + " " +
                 BC.SUBJECT).lower()
    for name, keys in SO.PHRASES:
        if name == "Corporate Lean 6S":
            continue
        for k in keys:
            if k in body_text:
                bad.append("the enquiry body carries %r, which routes to %s"
                           % (k, name))

    # Routing must survive a sender who mentions a home service in free text.
    noisy = (BC.SUBJECT + ": Acme Manufacturing\n\nService: Corporate Lean 6S"
             "\n\nWhat prompted this: our 5S reset day last year decayed")
    if SO.which_service(noisy) != "Corporate Lean 6S":
        bad.append("an enquiry mentioning a home service in free text is "
                   "misrouted to %r" % SO.which_service(noisy))

    # The date example must produce a calendar invite, which is what the page
    # promises in words a few lines above the field.
    when = SO.find_time(BC.DATE_EXAMPLE)
    if when is None:
        bad.append("the date example %r cannot be parsed by "
                   "service_orders.find_time, so the invite the page promises "
                   "would never be attached" % BC.DATE_EXAMPLE)
    else:
        try:
            SO.ics("Corporate Lean 6S", when, "a buyer")
        except Exception as e:                                  # noqa: BLE001
            bad.append("an invite cannot be built for the example time: %s" % e)

    if ("mailto:%s" % BC.TO) not in html:
        bad.append("the page does not carry a mailto to %s" % BC.TO)

    # The mechanism has to be stated before the ask, not confessed after it.
    # cro-growth's pattern, and the reason the newsletter form reads honestly.
    m_expl = html.find("opens your own")
    m_form = html.find('<form id="corp-form"')
    if m_expl < 0 or m_form < 0 or m_expl > m_form:
        bad.append("the explanation of how the enquiry is delivered does not "
                   "come before the form")

    # --- 3. the catalogue record and the page agree ----------------------
    js = io.open(DATA_JS, encoding="utf-8").read()
    cat = json.loads(js[js.index("["):js.rindex("]") + 1])
    corp = [p for p in cat if p.get("sku") == "CN-CORP"]
    if not corp:
        bad.append("CN-CORP is not in the catalogue")
    else:
        c = corp[0]
        if c.get("price") is not None:
            bad.append("CN-CORP has a price: %r" % c["price"])
        if "buy" in c:
            bad.append("CN-CORP has a payment link, which it must not")
        if c.get("quote") != "corporate.html":
            bad.append("CN-CORP does not route to corporate.html: %r"
                       % c.get("quote"))

    # The shop renderer has to honour that route, or the badge leads nowhere
    # again. Checked in the source rather than in a browser so this stays fast.
    site_js = io.open(os.path.join(SITE, "assets", "js", "site.js"),
                      encoding="utf-8").read()
    if "p.price === null && p.quote" not in site_js:
        bad.append("site.js no longer renders a quote-only product's own page, "
                   "so the CN-CORP button falls back to the contact form")

    # And the click has to be countable, or nobody can tell whether this page
    # did anything at 1.7 visitors a day.
    measure = io.open(os.path.join(SITE, "assets", "js", "measure.js"),
                      encoding="utf-8").read()
    if "corporate.html" not in measure:
        bad.append("measure.js does not record a click through to "
                   "corporate.html, so quote intent from the shop is invisible")

    # The prerendered shop grid is what a crawler and a JS-less phone read.
    shop = io.open(os.path.join(SITE, "shop.html"), encoding="utf-8").read()
    if 'href="corporate.html"' not in shop:
        bad.append("the pre-rendered shop grid still points CN-CORP somewhere "
                   "else. Run ops/prerender_shop.py")

    for b in bad:
        print("  FAIL " + b)
    if not bad:
        print("  ok  corporate page carries no price, its enquiry subject "
              "routes to Corporate Lean 6S, its date example builds a real "
              "calendar invite, and CN-CORP still has price: null with no "
              "payment link and a route to the page")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
