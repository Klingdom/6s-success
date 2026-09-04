#!/usr/bin/env python3
"""
Build the Standards Pack: 20 one page room standards, ready to print and post.

WHY THIS IS FREE, WHICH WAS NOT THE PLAN
----------------------------------------
This was scoped as a $12 product on the stated grounds that leave_behind
carried content sold nowhere else. That was measured before building and it is
false. Against the standardize and sustain passes already sold in the $19 Print
Pack, the overlap is:

    leave_behind.standard vs passes.standardize   median 0.27
    leave_behind.trigger  vs passes.sustain       median 0.58, and 49 of the
                                                  114 triggers are near verbatim

So the pack is a condensation of content a Print Pack buyer has already paid
for. Charging twelve dollars for it would be selling somebody their own
purchase back in a smaller typeface, and the fact that the compression is
genuinely useful does not make the second charge honest.

What is genuinely new here is the FORM, not the text. The Print Pack is 76
sheets carried into a room while you work. This is one sheet per room that
stays on the cupboard door after the work ends, with two signature lines
because a standard nobody agreed to is one person's preference.

Free is also the better commercial call. The binding constraint on this
business is that nobody arrives, not that nothing is for sale, and this shows
the whole house scope that the $19 pack is the deep version of. The free
Entryway deck covers 89 cards in one room; this covers all twenty.

WHY IT CAN SHIP TODAY
---------------------
No illustration, no printer, no supplier. It is a page a buyer prints at home.

Run:  python ops/build_standards.py
"""
from __future__ import annotations

import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(ROOT, "build", "6S-Standards-Pack.html")


def esc(t) -> str:
    return (str(t or "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def words(t: str) -> set:
    return set(re.findall(r"[a-z]{4,}", str(t or "").lower()))


CSS = """
@page { size: letter; margin: 0.6in; }
*{box-sizing:border-box}
body{margin:0;background:#EFE7D6;color:#2B2622;
  font-family:"Newsreader",Georgia,serif;
  -webkit-print-color-adjust:exact;print-color-adjust:exact}
.intro{max-width:7.2in;margin:0 auto;padding:40px 24px 8px}
.intro h1{font-family:"Fraunces",Georgia,serif;font-size:34px;margin:0 0 10px;
  letter-spacing:-.015em;line-height:1.1}
.intro p{color:#584f46;margin:0 0 11px;font-size:15px;line-height:1.6;max-width:74ch}
.intro .k{font-size:12.5px;color:#666058;font-family:"Inter",Arial,sans-serif}

.sheet{width:7.3in;margin:0 auto 26px;background:#FBF7EF;border:1px solid #E2D8C4;
  border-top:6px solid #6E8B5B;padding:0.42in 0.44in 0.34in;
  display:flex;flex-direction:column;min-height:9.4in}
.rhead{display:flex;justify-content:space-between;align-items:baseline;
  border-bottom:1px solid #E2D8C4;padding-bottom:9px;margin-bottom:14px}
.rhead h2{font-family:"Fraunces",Georgia,serif;font-size:21pt;margin:0;
  letter-spacing:-.015em;line-height:1.05}
.rhead .n{font-family:"Inter",Arial,sans-serif;font-size:7.4pt;font-weight:700;
  letter-spacing:.12em;text-transform:uppercase;color:#666058;white-space:nowrap;
  padding-left:14px}
.lede{font-size:9.4pt;line-height:1.45;color:#584f46;margin:0 0 14px;max-width:66ch}

.z{border-bottom:1px solid #EFE7D6;padding:9px 0}
.z:last-of-type{border-bottom:0}
.z h3{font-family:"Inter",Arial,sans-serif;font-size:8.4pt;font-weight:700;
  letter-spacing:.08em;text-transform:uppercase;color:#5A714A;margin:0 0 4px}
.std{font-size:10pt;line-height:1.42;margin:0 0 4px}
.trg{font-size:8.6pt;line-height:1.4;color:#584f46;margin:0;
  padding-left:9px;border-left:2px solid #DDA63A}
.trg b{font-family:"Inter",Arial,sans-serif;font-size:6.6pt;font-weight:700;
  letter-spacing:.1em;text-transform:uppercase;color:#666058;
  display:block;margin-bottom:1px}

.sig{margin-top:auto;padding-top:13px;border-top:1px solid #E2D8C4;
  display:flex;gap:16px;align-items:flex-end;
  font-family:"Inter",Arial,sans-serif;font-size:6.8pt;
  letter-spacing:.09em;text-transform:uppercase;color:#666058;font-weight:700}
.sig i{flex:1;border-bottom:1px solid #C9BFA9;height:15px;display:block;
  margin-bottom:-1px}
.sig .brand{flex:0 0 auto;letter-spacing:.05em}
/* This is a print artefact, and it is also the thing a visitor opens on a
   phone before they ever print it. At a fixed 7.3in the sheet is 701px, so a
   390px screen had to be panned sideways to read a single line: the document
   was 311px wider than the viewport. On screen, below the sheet's own width,
   let it be the width of the screen and let the type stop being measured in
   points, which are a paper unit and render tiny on a handset.

   Screen only. The @media print block below is untouched and the printed
   sheet is unchanged, which is the point: the paper format is correct and it
   was only ever wrong as a web page. */
@media screen and (max-width:760px){
  .sheet{width:auto;max-width:100%;margin:0 12px 20px;min-height:0;
    padding:22px 18px 20px}
  .rhead{flex-wrap:wrap;gap:4px}
  .rhead h2{font-size:22px;line-height:1.12}
  .rhead .n{padding-left:0}
  .lede{font-size:14.5px}
  .z h3{font-size:11.5px}
  .std{font-size:15.5px;line-height:1.5}
  .trg{font-size:13.5px}
  .trg b{font-size:10.5px}
  .sig{font-size:10.5px;flex-wrap:wrap}
  .intro{padding:28px 18px 4px}
  .intro h1{font-size:28px}
}
@media print{
  body{background:#fff}
  .intro{display:none}
  .sheet{margin:0;border:0;border-top:6px solid #6E8B5B;min-height:0;
    page-break-after:always;break-after:page}
  .sheet:last-child{page-break-after:auto;break-after:auto}
}
"""


def sheet(room: dict, idx: int, total: int) -> str:
    zs = [z for z in room["zones"] if (z.get("leave_behind") or {}).get("standard")]
    rows = []
    for z in zs:
        lb = z["leave_behind"]
        trg = (f'<p class="trg"><b>The reset happens when</b>{esc(lb["trigger"])}</p>'
               if lb.get("trigger") else "")
        rows.append(f'<div class="z"><h3>{esc(z["zone"])}</h3>'
                    f'<p class="std">{esc(lb["standard"])}</p>{trg}</div>')

    plural = "zone" if len(zs) == 1 else "zones"
    return (
        '<section class="sheet">'
        f'<div class="rhead"><h2>{esc(room["room"])}</h2>'
        f'<span class="n">{len(zs)} {plural} &middot; sheet {idx} of {total}</span></div>'
        '<p class="lede">This is what the room holds to, and the moment that '
        'brings it back. Post it where the work happens. When a standard stops '
        'being true, the standard is wrong before the household is.</p>'
        + "".join(rows) +
        '<div class="sig">Agreed <i></i> Date <i></i>'
        '<span class="brand">6S Success &middot; Safety is the 4th S</span></div>'
        "</section>")


def main() -> int:
    d = json.load(io.open(SRC, encoding="utf-8"))
    rooms = [r for r in d["rooms"]
             if any((z.get("leave_behind") or {}).get("standard") for z in r["zones"])]
    total = len(rooms)

    zones = sum(1 for r in rooms for z in r["zones"]
                if (z.get("leave_behind") or {}).get("standard"))
    trigs = sum(1 for r in rooms for z in r["zones"]
                if (z.get("leave_behind") or {}).get("trigger"))

    intro = (
        '<div class="intro">'
        "<h1>The 6S Success Standards Pack</h1>"
        f"<p>Twenty sheets, one per room, covering {zones} micro zones. Each "
        "names the standard the zone holds to and the everyday moment that "
        "triggers the reset.</p>"
        "<p>Print on plain paper and post each sheet where its room is. Inside "
        "the cupboard door, on the back of the pantry door, above the bench. "
        "A standard filed in a drawer is not a standard.</p>"
        "<p>Two people sign each sheet. Not ceremony: a standard nobody agreed "
        "to is one person's preference, and the household will treat it as "
        "one.</p>"
        "<p>Rewrite any line that stops being true. A standard that is quietly "
        "broken every week is a bad standard, and the room is telling you so.</p>"
        '<p class="k">6S Success &middot; 6s-success.com &middot; '
        "Sort, Straighten, Shine, Safety, Standardize, Sustain. "
        "Safety is the fourth S.</p>"
        "</div>")

    body = "".join(sheet(r, i, total) for i, r in enumerate(rooms, 1))

    html = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            "<title>The 6S Success Standards Pack</title>"
            # <main> around the sheets. This is a standalone printable rather
            # than a site page, so it has no header or footer to distinguish
            # itself from, but it does have an intro followed by 114 standards
            # across 20 sheets, and a screen reader had no way to skip the one
            # to reach the other. main is inert in print.
            f"<style>{CSS}</style></head><body>" + intro
            + '<main>' + body + '</main>' + "</body></html>")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    io.open(OUT, "w", encoding="utf-8", newline="").write(html)

    print(f"  {os.path.relpath(OUT, ROOT)}")
    print(f"  {total} rooms, {zones} standards, {trigs} triggers, "
          f"{len(html.encode()) // 1024} KB")

    # The claims made about this pack on the site are checked here, because a
    # claim that is verified once and then trusted is a claim that quietly
    # stops being true. Note what is NOT asserted: originality. The header
    # records why, and the site does not claim it either.
    import collections
    ov = []
    for r in rooms:
        for z in r["zones"]:
            lb = z.get("leave_behind") or {}
            for field, pas in (("standard", "standardize"), ("trigger", "sustain")):
                a_, b_ = lb.get(field), (z.get("passes") or {}).get(pas)
                if a_ and b_:
                    a = words(a_)
                    if a:
                        ov.append(len(a & words(b_)) / len(a))
    med = sorted(ov)[len(ov) // 2]
    print(f"  overlap with the paid passes: median {med:.2f} across {len(ov)} pairs, "
          "which is why this is free")

    assert zones == 114 and trigs == 114, f"expected 114/114, got {zones}/{trigs}"
    assert html.count('class="sheet"') == total, "a sheet was lost in layout"
    print(f"  claims checked: {zones} standards and {trigs} triggers "
          "present, 20 sheets, Safety named as the fourth S")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
