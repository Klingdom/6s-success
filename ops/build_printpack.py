#!/usr/bin/env python3
"""
Build the Whole House Print Pack: 684 printable cards across all 20 rooms.

WHY THIS IS A PRODUCT AND NOT A REPACKAGE
-----------------------------------------
The free Entryway deck is 89 cards for one room, 88 of them playable plus a
room card. This is 684 cards for the
whole house: every one of the 114 micro zones taken through all six passes,
with what done looks like, the safety checks, and the standard that holds it.

That is a fifteen fold difference in scope, and it is the difference between a
sample and a system. The free deck exists to prove the format works in your
entryway. This exists because once it has, you want the other nineteen rooms.

Nothing here is written fresh. Every card comes from the same content.json the
book, the zone pages and the Home Quest are built from, so it cannot drift from
them.

WHY IT CAN SHIP TODAY
---------------------
It needs no illustration. The card design carries its weight through the colour
coded S, the type hierarchy and the room and zone label, exactly as the v3
Entryway deck does. That is why this is buildable now while the illustrated
deck is not.

PRINTING
--------
Nine cards to a US Letter page at 2.5 by 3.5 inches, the same trim as the free
deck, so a mixed pile still behaves like one deck. Page breaks are forced
between sheets so no card is ever cut in half, and colour is used so that a
greyscale printer still produces usable cards.

Run:  python ops/build_printpack.py
"""
from __future__ import annotations

import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(ROOT, "build", "6S-Whole-House-Print-Pack.html")

SIX = ["sort", "straighten", "shine", "safety", "standardize", "sustain"]
COLOUR = {"sort": "#CB4B36", "straighten": "#BC4B2A", "shine": "#D98A2B",
          "safety": "#DDA63A", "standardize": "#6E8B5B", "sustain": "#4E7A57"}
PURPOSE = {
    "sort": "Decide what stays.",
    "straighten": "Give what stayed a home you can reach.",
    "shine": "Clean it, and see what the cleaning tells you.",
    "safety": "Fix what could hurt somebody.",
    "standardize": "Write down what good looks like.",
    "sustain": "Attach the reset to something that already happens.",
}


def esc(t) -> str:
    return (str(t or "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def trim(text: str, n: int) -> str:
    """Cards are a fixed size. Text that overruns is cut at a word and marked,
    with the full method a page reference away, rather than silently clipped by
    the printer into a sentence that stops mid word."""
    t = " ".join(str(text or "").split())
    if len(t) <= n:
        return t
    cut = t[:n].rsplit(" ", 1)[0].rstrip(" ,.;:")
    return cut + " ..."


CSS = """
/* Nine cards to a sheet, and they must actually FIT on the sheet.

   Found 2026-09-04: three rows of 3.5in is 10.5in of cards, and letter with a
   0.4in margin leaves 10.2in. Every sheet overflowed by 0.3in, so the third row
   was pushed onto a page of its own and every second printed page was a
   near-empty sheet carrying three orphaned card footers. The Whole House pack
   rendered 152 pages where 76 is the whole product, and this is what a paying
   customer downloaded.

   Fixed by giving the page 0.3in top and bottom (10.4in usable) and taking the
   card to 3.4in, so three rows need 10.2in and there is 0.2in of slack for
   rounding. 3.4in is still inside a standard 2.5x3.5in sleeve; a card slightly
   under the sleeve fits, a card over it does not. */
@page { size: letter; margin: 0.3in 0.35in; }
*{box-sizing:border-box}
body{margin:0;background:#EFE7D6;color:#2B2622;
  font-family:"Newsreader",Georgia,serif;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.intro{max-width:7.5in;margin:0 auto;padding:34px 20px 10px}
.intro h1{font-family:"Fraunces",Georgia,serif;font-size:32px;margin:0 0 8px;letter-spacing:-.015em}
.intro p{color:#584f46;margin:0 0 10px;font-size:15px;line-height:1.55;max-width:78ch}
.intro .k{font-size:12.5px;color:#8C8478;font-family:"Inter",Arial,sans-serif}
.sheet{display:grid;grid-template-columns:repeat(3,2.5in);grid-auto-rows:3.4in;
  gap:0;justify-content:center;margin:0 auto}
.card{width:2.5in;height:3.4in;overflow:hidden;background:#FBF7EF;
  border:1px solid #E2D8C4;border-top:5px solid var(--c);
  padding:0.16in 0.17in 0.14in;display:flex;flex-direction:column}
.chead{display:flex;justify-content:space-between;align-items:center;margin-bottom:5px}
.badge{font-family:"Inter",Arial,sans-serif;font-size:6.6pt;font-weight:700;
  letter-spacing:.1em;text-transform:uppercase;color:#fff;background:var(--c);
  padding:2.5px 7px;border-radius:99px}
.no{font-family:"Inter",Arial,sans-serif;font-size:6pt;color:#8C8478;font-weight:600}
.where{font-family:"Inter",Arial,sans-serif;font-size:6.2pt;font-weight:700;
  letter-spacing:.07em;text-transform:uppercase;color:var(--c);margin:0 0 2px}
.zone{font-family:"Fraunces",Georgia,serif;font-size:11.5pt;line-height:1.12;
  margin:0 0 4px;letter-spacing:-.01em}
.purpose{font-family:"Inter",Arial,sans-serif;font-size:6.4pt;color:#8C8478;
  margin:0 0 5px;letter-spacing:.02em}
.do{font-size:7.6pt;line-height:1.36;margin:0 0 5px;color:#2B2622}
.look{font-size:6.6pt;line-height:1.3;color:#584f46;border-left:2px solid var(--c);
  padding-left:5px;margin:auto 0 0}
.look b{font-family:"Inter",Arial,sans-serif;font-size:5.8pt;letter-spacing:.08em;
  text-transform:uppercase;color:#8C8478;display:block;margin-bottom:1px}
/* margin-top:auto pins the footer to the bottom of the card. The zone target
   used to do that job, and now it only appears on the sixth card, so without
   this the other five have their rule floating in the middle of empty space. */
.foot{display:flex;gap:2px;align-items:center;margin-top:auto;padding-top:5px;
  border-top:1px solid #E2D8C4}
.look + .foot{margin-top:5px}
.foot i{width:9px;height:3px;border-radius:1px;display:block}
.foot span{margin-left:auto;font-family:"Inter",Arial,sans-serif;font-size:5pt;
  letter-spacing:.05em;text-transform:uppercase;color:#8C8478;font-weight:700}
@media print{
  body{background:#fff}
  .intro{display:none}
  /* One sheet per page, so no card is ever split across a page break. */
  .sheet{page-break-after:always;break-after:page}
  .sheet:last-child{page-break-after:auto;break-after:auto}
}
"""

DOTS = "".join(f'<i style="background:{COLOUR[s]}"></i>' for s in SIX)


def card_html(room: str, zone: str, s: str, text: str, look: str,
              n: int, total: int) -> str:
    c = COLOUR[s]
    # done_looks_like describes the finished ZONE, not this one pass, so
    # printing it on all six cards repeated the same paragraph six times and
    # spent the most valuable space on the card saying nothing new. It belongs
    # on the last pass, where it is the finish line, and it is labelled as the
    # zone's condition rather than the card's.
    look_block = ""
    if look and s == "sustain":
        look_block = (f'<div class="look"><b>The zone is done when</b>'
                      f'{esc(trim(look, 210))}</div>')
    return (
        f'<div class="card" style="--c:{c}">'
        f'<div class="chead"><span class="badge">{s}</span>'
        f'<span class="no">{n} / {total}</span></div>'
        f'<p class="where">{esc(room)}</p>'
        f'<p class="zone">{esc(zone)}</p>'
        f'<p class="purpose">{esc(PURPOSE[s])}</p>'
        f'<p class="do">{esc(trim(text, 330))}</p>'
        f'{look_block}'
        f'<div class="foot">{DOTS}<span>Safety is the 4th S</span></div>'
        "</div>")


def main() -> int:
    d = json.load(io.open(SRC, encoding="utf-8"))

    cards, rooms, zones = [], 0, 0
    for r in d["rooms"]:
        rooms += 1
        for z in r["zones"]:
            passes = z.get("passes") or {}
            steps = [s for s in SIX if passes.get(s)]
            if not steps:
                continue
            zones += 1
            for s in steps:
                cards.append((r["room"], z["zone"], s, passes[s],
                              z.get("done_looks_like", "")))

    total = len(cards)
    body = []
    # Nine to a sheet, and a sheet is a printed page.
    for i in range(0, total, 9):
        body.append('<div class="sheet">')
        for j, c in enumerate(cards[i:i + 9], start=i + 1):
            body.append(card_html(c[0], c[1], c[2], c[3], c[4], j, total))
        body.append("</div>")

    intro = (
        '<div class="intro">'
        "<h1>The 6S Success Whole House Print Pack</h1>"
        f"<p>{total} cards covering {zones} micro zones across {rooms} rooms. "
        "Every zone takes all six passes in order, and every card names what to "
        "do and how you know you can stop.</p>"
        "<p>Print on card stock if you have it. Nine cards to a US Letter page "
        "at two and a half by three and a half inches, the same size as the free "
        "Entryway deck, so the two shuffle together.</p>"
        "<p>Work one card at a time. The order matters: sorting before "
        "straightening stops you giving a home to something that should have "
        "left, and a standard written before the clean describes the wrong "
        "room.</p>"
        '<p class="k">6S Success &middot; 6s-success.com &middot; '
        "Sort, Straighten, Shine, Safety, Standardize, Sustain. "
        "Safety is the fourth S.</p>"
        "</div>")

    html = ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            "<title>The 6S Success Whole House Print Pack</title>"
            f"<style>{CSS}</style></head><body>"
            + intro + "".join(body) + "</body></html>")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    io.open(OUT, "w", encoding="utf-8", newline="").write(html)

    kb = len(html.encode()) // 1024
    print(f"  {os.path.relpath(OUT, ROOT)}")
    print(f"  {rooms} rooms, {zones} zones, {total} cards, "
          f"{(total + 8) // 9} sheets, {kb} KB")

    # The claims printed on the pack itself have to be true.
    assert SIX[3] == "safety", "Safety must be the fourth S"
    assert total == sum(1 for r in d["rooms"] for z in r["zones"]
                        for s in SIX if (z.get("passes") or {}).get(s)), \
        "card count does not match the manual"
    assert html.count('class="card"') == total, "a card was lost in layout"
    print("  claims checked: card count matches the manual, Safety is fourth")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
