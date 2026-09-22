#!/usr/bin/env python3
"""
Give the virtual consult a real button on every hand-authored article, with
its origin carried in the query string.

WHY
---
REVIEW-COMMERCE-2026-09-07.md section 3.1 (backlog C8): on every zone, room
and article page a stranger could land on, the print pack got two real
buttons and the consult got one de-emphasised sentence at
font-size:14.5px;opacity:.85 with a plain text link. The arithmetic in that
section is why this matters: the consult's contribution per order is 13.4x
the pack's, so a split that buries it behind a smaller, quieter link cannot
be right at any conversion rate.

ops/build_zone_pages.py's offer()/room_offer() and ops/build_articles.py's
offer() already carry the equivalent fix for the 114 zone pages, 20 room
pages and the 2 generic pillar articles those generators own. This script
covers the remaining articles under site/articles/, none of which any
generator owns (confirmed: grep across every ops/build_*.py finds no write
to site/articles/<slug>.html other than the two generic ones built by
ops/build_articles.py itself). Their CTA band already ends in a two-button
row (the print pack, then a free alternative); this inserts a third,
carrying ?from=article:<slug> so measure.js's new service-cta handler can
tell a click here apart from the pack's, and giving the click a real button
instead of a text link buried in a sentence.

WHAT THIS SKIPS, ON PURPOSE
----------------------------
- site/articles/index.html: no CTA band to touch.
- the two B2B articles (what-a-5s-engagement-costs.html,
  why-5s-decays-after-six-months.html): built for a different buyer with a
  different offer (the scoping conversation on corporate.html), not this
  consumer consult.
- any article whose band already carries a real CN-VIRTUAL or CN-INHOME
  button (why-you-cant-see-your-own-clutter.html already links straight to
  the Stripe payment link with data-sku set, which is a stronger version of
  this fix, not a gap).

Idempotent: a file that already carries data-sku="CN-VIRTUAL" in its band
is left alone, so a second run changes nothing.
"""
from __future__ import annotations

import glob
import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
ARTICLES = os.path.join(SITE, "articles")

SKIP = {"index.html", "what-a-5s-engagement-costs.html",
        "why-5s-decays-after-six-months.html"}

# The CTA band always ends with the print pack's primary button, then one
# free-alternative secondary button, then the section closes. This matches
# that closing shape regardless of the free alternative's own text or href,
# and inserts the new button just before the row closes.
ROW_END_RE = re.compile(
    r'(<a class="btn btn-on-deep"[^>]*>[^<]*</a>)(</p></section>)')


def consult_price() -> int:
    src = io.open(os.path.join(SITE, "assets", "js", "data.js"),
                  encoding="utf-8").read()
    catalog = json.loads(src[src.index("["):src.rindex("]") + 1])
    for p in catalog:
        if p.get("sku") == "CN-VIRTUAL":
            return int(p["price"])
    raise KeyError("CN-VIRTUAL not in data.js")


def button(slug: str, price: int) -> str:
    return ('<a class="btn btn-on-deep btn-sm" style="margin-left:10px" '
            f'data-sku="CN-VIRTUAL" href="../consulting.html?from=article:{slug}">'
            f'Talk it through, {price} dollars</a>')


def main() -> int:
    price = consult_price()
    n = 0
    for f in sorted(glob.glob(os.path.join(ARTICLES, "*.html"))):
        name = os.path.basename(f)
        if name in SKIP:
            continue
        slug = name[:-5]
        s = io.open(f, encoding="utf-8").read()
        if 'data-sku="CN-VIRTUAL"' in s or 'data-sku="CN-INHOME"' in s:
            continue
        m = ROW_END_RE.search(s)
        if not m:
            print(f"no CTA row found, skipped: {name}")
            continue
        new = m.group(1) + button(slug, price) + m.group(2)
        s2 = s[:m.start()] + new + s[m.end():]
        io.open(f, "w", encoding="utf-8", newline="").write(s2)
        n += 1
    print(f"{n} article page(s) gained a consult button")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
