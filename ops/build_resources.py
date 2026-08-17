#!/usr/bin/env python3
"""
Build site/resources.html: the companion page the book points to.

The book contains zero URLs, so 233,000 words of demand generation currently
sends the reader nowhere. This is the destination. It is generated from the same
source of truth every product uses, so it cannot drift from the book: the Micro
Zone Manual's content.json (20 rooms, 114 zones) and zone_products.json.

One real page with an anchor per room, rather than 21 pages, so every link the
book prints resolves on day one.
"""
import json, os, html, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "content", "manual", "source")
OUT = os.path.join(ROOT, "site", "resources.html")
HEADER = open(os.path.join(ROOT,"site","_header.frag"),encoding="utf-8").read()
FOOTER = open(os.path.join(ROOT,"site","_footer.frag"),encoding="utf-8").read()

content = json.load(open(os.path.join(SRC, "content.json"), encoding="utf-8"))
zprod = json.load(open(os.path.join(SRC, "zone_products.json"), encoding="utf-8"))

# The book renames seven zones that the Manual names differently, and the chapter
# names are the better writing. This page is the book's companion, so it must use
# the book's names or a reader holding both sees two names for one zone. Extracted
# from the chapter manuscripts themselves, which is authoritative.
BOOK_ZONES = json.load(open(os.path.join(ROOT, "ops", "book_zone_names.json"), encoding="utf-8"))

CH = {"Entryway": 31, "Kitchen": 32, "Pantry": 33, "Dining Room": 34, "Living Room": 35,
      "Family Room": 36, "Primary Bedroom": 37, "Guest Bedroom": 38, "Kids Bedroom": 39,
      "Nursery": 40, "Primary Bathroom": 41, "Guest Bathroom": 42, "Laundry Room": 43,
      "Home Office": 44, "Garage": 45, "Workshop": 46, "Mudroom": 47, "Hall Closet": 48,
      "Stair Landing": 49, "Patio or Deck": 50}

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

e = lambda s: html.escape(str(s))

sections, toc = [], []
for r in content["rooms"]:
    room = r["room"]
    sl = slug(room)
    ch = CH.get(room)
    zones = r["zones"]
    kit = sorted({p.get("name") if isinstance(p, dict) else p
                  for z in zones for p in zprod.get(f"{room}||{z['zone']}", [])})
    surfaces = sum(len((z.get("shine_detail") or {}).get("surfaces") or []) for z in zones)
    toc.append(f'<a href="#{sl}">{e(room)}</a>')
    names = BOOK_ZONES.get(room) or [z["zone"] for z in zones]
    if len(names) != len(zones):
        names = [z["zone"] for z in zones]
    zl = "".join(f"<li>{e(n)}</li>" for n in names)
    kl = "".join(f"<li>{e(k)}</li>" for k in kit)
    sections.append(f"""<section id="{sl}" class="room">
  <h2>{e(room)}</h2>
  <p class="meta">Chapter {ch} &middot; {len(zones)} micro zones &middot; {surfaces} surfaces to clean &middot; {len(kit)} product types</p>
  <div class="cols">
    <div>
      <h3>The micro zones, in order</h3>
      <ol>{zl}</ol>
    </div>
    <div>
      <h3>What you clean it with</h3>
      <ul class="kit">{kl}</ul>
      <p class="note">Types, not brands. Buy whatever version of each you like, or use what you already own.</p>
    </div>
  </div>
</section>""")

doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rooms and micro zones: 20 rooms, 114 micro zones | 6S Success</title>
<meta name="description" content="Every room broken into its micro zones, in the order to work them, with the product types each one needs. Twenty rooms, 114 micro zones. Free companion to the book.">
<!-- ops/build_seo.py owns canonical, Open Graph and JSON-LD. Re-run it after this. -->
<link rel="stylesheet" href="assets/css/fonts.css">
<link rel="stylesheet" href="assets/css/site.css">
<style>
  .res{{max-width:900px;margin:0 auto;padding:52px 0 90px}}
  .res h1{{font-size:clamp(34px,5vw,52px);margin-bottom:.2em}}
  .res .lede{{max-width:640px}}
  .toc{{display:flex;flex-wrap:wrap;gap:8px;margin:30px 0 10px;padding:20px;background:var(--panel);border:1px solid var(--rule)}}
  .toc a{{font-family:var(--sans);font-size:13.5px;font-weight:600;text-decoration:none;color:var(--slate);
    background:var(--paper);border:1px solid var(--rule);padding:5px 11px;border-radius:2px}}
  .toc a:hover{{border-color:var(--terra);color:var(--terra)}}
  .room{{padding-top:30px;margin-top:34px;border-top:2px solid var(--rule);scroll-margin-top:84px}}
  .room h2{{font-size:28px;margin-bottom:.15em}}
  .room .meta{{font-family:var(--sans);font-size:12.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--soft);margin:0 0 18px}}
  .cols{{display:grid;grid-template-columns:1fr 1fr;gap:34px}}
  @media (max-width:700px){{.cols{{grid-template-columns:1fr;gap:20px}}}}
  .room h3{{font-family:var(--sans);font-size:11.5px;letter-spacing:.16em;text-transform:uppercase;
    color:var(--terra);font-weight:700;margin:0 0 10px}}
  .room ol,.room ul{{margin:0;padding-left:1.3em}}
  .room li{{margin:.32em 0;font-size:16.5px;line-height:1.45}}
  .kit li{{color:var(--ink)}}
  .note{{font-size:14px;color:var(--soft);margin:12px 0 0}}
  .safety{{background:var(--panel);border-left:3px solid var(--terra);padding:16px 20px;margin:26px 0}}
  .safety p{{margin:0;font-size:15.5px;color:var(--soft)}}
</style>
</head>
<body>
{HEADER}
<main class="wrap">
<article class="res">
<nav class="crumbs" aria-label="Breadcrumb">
  <a href="index.html">Home</a> &rsaquo; <span aria-current="page">Rooms and micro zones</span>
</nav>
<h1>Every room, micro zone by micro zone</h1>
<p class="lede">The companion page to <a href="book.html">6S Success: Home Edition</a>. Twenty rooms,
114 micro zones, and the product types that clean each of them. Free, no sign-up.</p>

<p><b>A micro zone is the smallest part of a room you can finish in one go.</b> A kitchen is too
big to start; the primary prep counter is not. Each room below breaks into its micro zones in the
order the book works them, because order matters: clearing the landing spot before the shoes means
you are not moving the same pile twice. Under each room is the kit, listed as product types rather
than brands, so you can use what you already own.</p>

<p>The six S's are how you work a micro zone once you are standing in it: Sort what does not
belong, Straighten what stays into a home you can reach, Shine it while inspecting for what is
wearing out, fix the Safety problem you just found, Standardize the result so it is repeatable, and
Sustain it on a rhythm. <a href="method.html">The method page</a> explains each S in full.</p>

<div class="safety">
  <p>Before you start any of this, please read the <a href="disclaimer.html">safety notice</a>.
  Cleaning products are chemicals, and some of these rooms contain tools, heat, or water near power.</p>
</div>

<div class="toc">{''.join(toc)}</div>

{''.join(sections)}

<section class="room">
  <h2>The method</h2>
  <p class="meta">Chapters 1 to 30 &middot; the six S's</p>
  <p>Sort, Straighten, Shine, Safety, Standardize, Sustain. The first half of the book
  teaches the loop; the twenty room chapters above apply it. If you only read one chapter
  first, read Chapter 2, which is what the six S's actually mean.</p>
  <p><a class="btn btn-primary" href="book.html">About the book</a>
  <a class="btn btn-ghost" href="method.html">Read the method</a></p>
</section>

<section class="room">
  <h2>Where to go next</h2>
  <p class="meta">If you have finished a room</p>
  <ul>
    <li><a href="method.html">The six-S method in full</a>, one section per S, with what each one asks of you.</li>
    <li><a href="book.html">6S Success: Home Edition</a>, the fifty-chapter book these rooms come from. Chapters 1 to 30 are free to read online.</li>
    <li><a href="shop.html?cat=Tools%20%26%20Supplies">Tools and supplies</a>, if you would rather buy the product types above than source them yourself.</li>
    <li><a href="consulting.html">Consulting</a>, if you would rather have someone run the reset with you.</li>
    <li><a href="disclaimer.html">The safety notice</a>, which is worth reading before any room that involves chemicals, height, or power.</li>
  </ul>
</section>
</article>
</main>
{FOOTER}
</body>
</html>"""
open(OUT, "w", encoding="utf-8").write(doc)
print(f"wrote {OUT}")
print(f"rooms: {len(content['rooms'])} | zones: {sum(len(r['zones']) for r in content['rooms'])}")
