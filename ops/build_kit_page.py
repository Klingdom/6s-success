#!/usr/bin/env python3
"""
The kit page: the eight things every micro zone asks for, in method order.

WHY A KIT PAGE AND NOT THE ZONE PAGES
-------------------------------------
The zone pages are the highest intent pages on the site, which makes them the
obvious place for a product link and the wrong one. Each already carries the
nineteen dollar print pack, which nets about $17.90 at roughly 97 percent
margin. An affiliate conversion nets about $1.58. Moving a click from one to
the other loses about sixteen dollars.

This is also the only page where recommending a product without diagnosing the
reader's situation is defensible. CLAUDE.md section 6 says never prescribe
before diagnosing, and section 48 rules out dressing a commission up as
personalisation. These eight are called for by 109 to 114 of the 114 zones, so
the diagnosis was done at the level of the method rather than the person. No
other product in the catalogue of 123 has that property, which is exactly why
no other product is on this page.

SORT BEFORE STRAIGHTEN, ENFORCED BY THE PAGE
--------------------------------------------
Recommending storage to somebody who has not decided what stays is the failure
the method exists to prevent. So the sort container set comes first, and the
page says plainly that the organisers are for afterwards. The order of the
page is the method, not a merchandising decision.

HONEST ABOUT WHAT IS NOT LIVE
-----------------------------
No programme is approved yet, so ops/affiliate.py returns no link and this
page renders each product as a described type with no button. That is the
correct state: a product type a reader can go and buy anywhere is useful, and
an untracked link that looks tracked is not.

The disclosure block at the top of the page follows the same rule. With no
links to disclose it says so plainly, rather than warning about commissions
that cannot be earned, and it points at /affiliate-disclosure.html.

Run:  python ops/build_kit_page.py
"""
from __future__ import annotations

import csv
import html
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import affiliate as A                                          # noqa: E402

SITE = os.path.join(ROOT, "site")
OUT = os.path.join(SITE, "kit.html")
CATALOGUE = os.path.join(ROOT, "ops", "affiliate-catalogue.csv")

# The order is the method: decide what stays, give it a home, clean it, make
# the standard visible, keep it. Not by price and not by commission.
PHASE_ORDER = ["Sort", "Straighten", "Shine", "Safety", "Standardize", "Sustain"]

# Why this thing, in the method's own terms. Written per product because a
# recommendation nobody can audit is the thing section 48 forbids.
WHY = {
    "Keep, Relocate, Donate, Recycle, Trash container set":
        "Sort is a decision, and a decision needs somewhere to put the answer. "
        "Five labelled containers turn a vague sort into five clear piles, "
        "which is why this comes before any organiser on this page.",
    "Portable cleaning caddy":
        "Every zone gets cleaned, and walking back to the cupboard is the "
        "reason it stops happening. One caddy that travels means Shine costs "
        "a minute rather than a trip.",
    "Compact vacuum with attachments":
        "The attachments matter more than the vacuum. Most of what a micro "
        "zone needs is a crevice tool for the seam where grit collects, not "
        "power on open floor.",
    "Color-coded microfiber cloth set":
        "Colour coding is a visual control. One colour per job stops the "
        "bathroom cloth reaching the kitchen counter, and it does that "
        "without anybody having to remember a rule.",
    "Neutral pH multi-surface cleaner":
        "One neutral cleaner handles nearly every surface in the house, which "
        "means one bottle in the caddy rather than six under the sink. "
        "Neutral pH is the part that matters: it will not etch stone or strip "
        "a finish.",
    "Moisture Absorber or Humidity Monitor":
        "This is the Safety pass in most zones. Damp is what turns a storage "
        "problem into mould, and it is invisible until it is not, so it gets "
        "measured rather than guessed.",
    "Portable label maker":
        "Standardize means the right state is obvious without explanation. A "
        "label is the cheapest way to make a standard survive somebody who "
        "was not there when you set it.",
    "Removable write-on labels":
        "Removable matters. A standard that is wrong should be easy to change, "
        "and a label you cannot peel off makes people live with a bad system "
        "rather than fix it.",
}


def kit() -> list:
    rows = [r for r in csv.DictReader(io.open(CATALOGUE, encoding="utf-8-sig"))
            if r["Tier"].startswith("1")]

    def first_phase(r):
        ph = [p.strip() for p in re.split(r"[;,]", r["Supported 6S Phases"])]
        for i, name in enumerate(PHASE_ORDER):
            if name in ph:
                return i
        return len(PHASE_ORDER)

    return sorted(rows, key=first_phase)


def card(r: dict) -> str:
    name = r["Product Standard Name"].strip()
    lo, hi = r["Estimated Retail Low"], r["Estimated Retail High"]
    zones = r["_zone_count"]
    phases = " and ".join(p.strip() for p in re.split(r"[;,]", r["Supported 6S Phases"]) if p.strip())
    why = WHY.get(name, "")
    safety = (r.get("Safety / Compatibility Notes") or "").strip()

    link = A.build_link(r.get("Merchant", ""), r.get("Affiliate URL", ""))
    action = (f'<a class="btn btn-sm btn-primary" href="{html.escape(link)}" '
              f'rel="nofollow sponsored noopener" data-aff="1">See one</a>'
              if link else
              '<span class="pending">No retailer link yet. This is a product '
              'type, so any shop that sells it will do.</span>')

    return f"""
    <li class="kititem">
      <p class="phase">{html.escape(phases)}</p>
      <h2>{html.escape(name)}</h2>
      <p class="why">{html.escape(why)}</p>
      <p class="meta"><b>{html.escape(zones)} of 114 zones</b> ask for this
      &nbsp;&middot;&nbsp; typically ${html.escape(lo)} to ${html.escape(hi)}</p>
      {f'<p class="safety">{html.escape(safety)}</p>' if safety else ''}
      <p class="act">{action}</p>
    </li>"""


def main() -> int:
    rows = kit()
    src = io.open(os.path.join(SITE, "method.html"), encoding="utf-8").read()
    hdr = src[src.index("<header"):src.index("</header>") + 9]
    ftr = src[src.index("<footer"):src.index("</footer>") + 9]

    has_amazon = any(A.build_link("amazon", r.get("Affiliate URL", "")) for r in rows)
    live = sum(1 for r in rows if A.build_link(r.get("Merchant", ""),
                                               r.get("Affiliate URL", "")))

    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The eight things every micro zone asks for | 6S Success</title>
<meta name="description" content="Across all 114 micro zones the same eight
things keep coming up. What each one is for, in method order, and why Sort
comes before any organiser.">
<link rel="canonical" href="https://6s-success.com/kit.html">
<link rel="stylesheet" href="assets/css/site.css">
<style>
.kitlist{{list-style:none;padding:0;margin:0;display:flex;
  flex-direction:column;gap:18px}}
.kititem{{border:1px solid var(--line);background:var(--panel);
  border-radius:16px;padding:24px 28px}}
.kititem .phase{{font-family:var(--sans);font-size:11px;font-weight:700;
  letter-spacing:.16em;text-transform:uppercase;color:var(--accent);margin:0}}
.kititem h2{{margin:8px 0 10px;font-size:24px}}
.kititem .why{{margin:0 0 14px;max-width:64ch}}
.kititem .meta{{font-family:var(--sans);font-size:14px;color:var(--soft);
  margin:0 0 10px}}
.kititem .safety{{font-family:var(--sans);font-size:14px;color:var(--soft);
  border-left:3px solid var(--line-2, #D9CDB8);padding-left:12px;margin:0 0 10px}}
.kititem .pending{{font-family:var(--sans);font-size:14px;color:var(--soft)}}
.disclosure{{border:1px solid var(--line);background:var(--wash, #F2EADC);
  border-radius:14px;padding:22px 26px;margin:0 0 34px}}
.disclosure p{{margin:0 0 10px;font-size:16px;line-height:1.55}}
.disclosure p:last-child{{margin-bottom:0}}
</style>
</head>
<body>
{hdr}
<main>
<section class="section">
  <div class="wrap narrow">
    <p class="eyebrow">The kit</p>
    <h1>Eight things, and the reason for each</h1>
    <p class="lede">Across all 114 micro zones in this house, the same eight
    things keep being asked for. Not a shopping list: a short answer to what
    the method actually needs, in the order the method needs it.</p>
    <p>You almost certainly own several already. That is the point of putting
    them in one place, so you can check rather than buy.</p>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="wrap narrow">
    {A.disclosure(bool(has_amazon), bool(live))}
    <ul class="kitlist">{''.join(card(r) for r in rows)}</ul>

    <p style="margin-top:34px;color:var(--soft)">Nothing here is needed to
    start. The <a href="quest.html">guided reset</a> is free and the first
    zone takes about fifteen minutes with what is already in the house.</p>
  </div>
</section>
</main>
{ftr}
<script defer src="/stats/script.js"
  data-website-id="f1fc5160-4473-422d-a89e-73ff6cbdca7a"
  data-host-url="https://6s-success.com/stats"></script>
</body>
</html>
"""
    io.open(OUT, "w", encoding="utf-8", newline="").write(doc)

    assert A.DISCLOSURE_ID in doc, "the disclosure block is missing"
    if live:
        assert doc.index(A.DISCLOSURE_ID) < doc.index('data-aff="1"'), \
            "the disclosure must come before the first affiliate link"
    assert "Sort" in doc[:doc.index("Straighten")], \
        "Sort must appear before Straighten: the page order is the method"

    print(f"  wrote site/kit.html")
    print(f"  {len(rows)} products, in method order:")
    for r in rows:
        print(f"    {r['Supported 6S Phases'].split(';')[0].strip():14} "
              f"{r['Product Standard Name'][:44]}")
    print(f"  live retailer links: {live} of {len(rows)}")
    if not live:
        print(f"  no programme is approved, so every product renders as a type "
              f"with no button, which is correct")

    # This generator's own template carries none of the whole-site wiring
    # passes (PWA icons, the progressive marker, measure.js, the skip link
    # and main landmark, aria-current, the catalogue-script prune, or the
    # canonical link form): every other page generator in preflight's
    # gate_generator_ownership chain re-runs these on its own output for
    # exactly this reason, and this one had simply never been added to that
    # list. A plain rebuild of kit.html silently stripped all of it, the
    # same issue #26 shape every other single-page generator here already
    # closed.
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import canonical_links
    import prune_catalog_js
    import wire_landmarks
    import wire_progressive
    import wire_measure
    import wire_pwa
    import wire_aria_current
    import build_avif
    canonical_links.main()
    prune_catalog_js.main()
    wire_landmarks.main()
    wire_progressive.main()
    wire_measure.main()
    wire_pwa.main()
    wire_aria_current.main()
    # Same reason as the other generators: an unchained wiring pass
    # is drift waiting for the next rebuild.
    build_avif.wire()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
