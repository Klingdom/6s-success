#!/usr/bin/env python3
"""
Lay the card template over a hero photograph to make a card front.

WHY THIS IS THE MISSING PIECE
-----------------------------
The regeneration prompts describe a two stage pipeline: a model makes a clean
hero photograph with no text on it, and "all card text, callout pins,
difficulty stars, and info rows are added afterward by the card template
layer". That is why the existing cards have no garbled AI lettering.

The template layer did not exist. Five generated heroes were sitting in
build/heroes with no way to become cards, and 88 more are coming. This is it.

WHAT IT RENDERS, AND WHAT IT HONESTLY CANNOT
--------------------------------------------
It renders from the data this project actually holds: the card code, its type,
its difficulty, its 6S step, its name, its objective and its canonical line.

It does NOT invent the parts it has no data for. The original cards carry
numbered callout pins on the photograph, a quick win, a pro tip, a reset time
and a maintenance figure. Those live in the original card artwork and were
never extracted to text. Making them up would put confident, wrong operating
instructions on a product, so the template omits them and the card is honestly
simpler than a hand made one rather than fictionally as rich.

HOW IT RENDERS
--------------
HTML and CSS in the site's own type and palette, screenshotted by a headless
browser at exact card dimensions. Not PIL: the existing cards are typographic
objects, and hand placing text in a bitmap library produces something that
looks like a spreadsheet.

Run:  python ops/build_card_template.py --list
      python ops/build_card_template.py --card EM-005
      python ops/build_card_template.py --all
"""
from __future__ import annotations

import glob
import html
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEROES = os.path.join(ROOT, "build", "heroes")
OUT = os.path.join(ROOT, "build", "card-fronts")

# 2.5 by 3.5 inches at 300 dpi, which is the real print size of these cards.
CARD_W, CARD_H = 750, 1050

TYPE_COLOUR = {
    "Micro Zone": "#2F5233", "Problem": "#BC4B2A", "Tool": "#3C5A6B",
    "Skill": "#6E5B8B", "Habit": "#4E7A57", "Upgrade": "#B07A18",
    "Event": "#8C5A2B", "Win / Reward": "#B8860B", "Win": "#B8860B",
    "Room": "#2B2622",
}


def cards() -> dict:
    out = {}
    for f in ("mudroom-cards.json", "entryway-cards.json"):
        p = os.path.join(ROOT, "build", f)
        if os.path.exists(p):
            for c in json.load(io.open(p, encoding="utf-8")):
                out[c["ID"]] = c
    return out


def hero_for(code: str) -> str | None:
    hits = glob.glob(os.path.join(HEROES, "*", f"{code}*"))
    return hits[0] if hits else None


def stars(d: str) -> int:
    """Filled stars from the source table, or 0 when it is not recorded.

    Returning 1 when the difficulty is unknown printed a confident one star
    on every entryway card, because that extraction has no difficulty column.
    One star is a claim, and a wrong one; no stars is the truth.
    """
    return min(5, sum(1 for ch in (d or "") if ch in "★⭐*"))


def card_html(c: dict, hero_rel: str) -> str:
    cat = c.get("Category", "").strip()
    colour = TYPE_COLOUR.get(cat, "#2B2622")
    n = stars(c.get("Difficulty", ""))
    star_row = ("<span class='on'>&#9733;</span>" * n
                + "<span class='off'>&#9733;</span>" * (5 - n)) if n else ""
    six = html.escape(c.get("Primary 6S", "").strip())
    # The entryway extraction had no objective column and fell back to the
    # card name, so this box rendered as "What this card does: Shoe Zone."
    # A box that repeats the title is worse than no box.
    raw_obj = c.get("Objective / Behavior", "").strip().rstrip(".")
    if raw_obj.lower() == c.get("Card", "").strip().lower():
        raw_obj = ""
    obj = html.escape(raw_obj)
    canon = html.escape(c.get("Canonical text", "").strip())
    benefit = html.escape(c.get("Benefit / Effect", "").strip())

    objective_box = (f'<div class="box"><h2>What this card does</h2>'
                     f'<p>{obj}.</p></div>') if obj else ""

    return f"""<!doctype html><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=Newsreader:wght@400;500&display=swap">
<style>
*{{box-sizing:border-box;margin:0}}
body{{background:#8C8478}}
.card{{width:{CARD_W}px;height:{CARD_H}px;background:#FBF7EF;
  border:1px solid #E2D8C4;border-radius:22px;overflow:hidden;
  display:flex;flex-direction:column;font-family:"Newsreader",Georgia,serif;
  color:#2B2622}}
.band{{background:{colour};color:#FBF7EF;display:flex;align-items:center;
  gap:14px;padding:16px 22px;font-family:"Inter",system-ui,sans-serif}}
.code{{font-weight:700;font-size:19px;letter-spacing:.02em;
  font-variant-numeric:tabular-nums}}
.kind{{font-weight:600;font-size:12.5px;letter-spacing:.16em;
  text-transform:uppercase;opacity:.92}}
.diff{{margin-left:auto;font-size:15px;letter-spacing:1px;white-space:nowrap}}
.diff .off{{opacity:.34}}
.head{{padding:22px 26px 16px}}
h1{{font-family:"Fraunces",Georgia,serif;font-weight:700;font-size:44px;
  line-height:1.02;letter-spacing:-.022em;text-wrap:balance}}
.tag{{margin-top:9px;font-family:"Inter",system-ui,sans-serif;font-size:13px;
  font-weight:600;letter-spacing:.05em;text-transform:uppercase;color:#6A625A}}
.shot{{margin:0 26px;border-radius:14px;overflow:hidden;
  border:1px solid #E2D8C4;flex:1 1 auto;min-height:340px;background:#F2EADC}}
.shot img{{width:100%;height:100%;object-fit:cover;display:block}}
.body{{padding:20px 26px 0;display:flex;flex-direction:column;gap:15px;
  flex:0 0 auto}}
.box{{border:1px solid #E2D8C4;background:#F7F2E9;border-radius:12px;
  padding:14px 17px}}
.box h2{{font-family:"Inter",system-ui,sans-serif;font-size:10.5px;
  font-weight:700;letter-spacing:.15em;text-transform:uppercase;
  color:{colour};margin-bottom:6px}}
.box p{{font-size:17px;line-height:1.42}}
.lesson p{{font-style:italic}}
.foot{{margin-top:auto;display:flex;align-items:center;gap:12px;
  padding:15px 26px 20px;font-family:"Inter",system-ui,sans-serif;
  font-size:11px;font-weight:600;letter-spacing:.13em;text-transform:uppercase;
  color:#8C8478;border-top:1px solid #E2D8C4}}
.foot .s{{color:{colour}}}
.foot .brand{{margin-left:auto;letter-spacing:.18em}}
</style>
<div class="card">
  <div class="band">
    <span class="code">{html.escape(c['ID'])}</span>
    <span class="kind">{html.escape(cat)} card</span>
    <span class="diff">{star_row}</span>
  </div>
  <div class="head">
    <h1>{html.escape(c.get('Card',''))}</h1>
    <p class="tag">{six}</p>
  </div>
  <div class="shot"><img src="{hero_rel}" alt=""></div>
  <div class="body">
    {objective_box}
    <div class="box lesson"><h2>The 6S lesson</h2><p>{canon}</p></div>
  </div>
  <div class="foot">
    <span class="s">{six}</span>
    <span>{html.escape(benefit[:44])}</span>
    <span class="brand">6S Success</span>
  </div>
</div>
"""


def main() -> int:
    allc = cards()
    have = {}
    for f in glob.glob(os.path.join(HEROES, "*", "*")):
        m = re.match(r"([A-Z]{2}-\d{3})", os.path.basename(f))
        if m:
            have[m.group(1)] = f

    if "--list" in sys.argv or len(sys.argv) == 1:
        print(f"  heroes available : {len(have)}")
        for code, f in sorted(have.items()):
            c = allc.get(code, {})
            ok = "ok" if c else "NO CARD DATA"
            print(f"    {code}  {c.get('Card','?'):26} {ok}")
        missing = [c for c in have if c not in allc]
        if missing:
            print(f"\n  {len(missing)} heroes have no card data and cannot be "
                  f"rendered: {missing}")
        return 0

    want = list(have)
    if "--card" in sys.argv:
        want = [sys.argv[sys.argv.index("--card") + 1].upper()]

    os.makedirs(OUT, exist_ok=True)
    made = []
    for code in want:
        if code not in have:
            print(f"  {code}: no hero photograph in build/heroes")
            continue
        if code not in allc:
            print(f"  {code}: no card data, refusing to invent it")
            continue
        rel = os.path.relpath(have[code], OUT).replace(os.sep, "/")
        p = os.path.join(OUT, f"{code}.html")
        io.open(p, "w", encoding="utf-8", newline="").write(
            card_html(allc[code], rel))
        made.append((code, p))

    print(f"  wrote {len(made)} card fronts as HTML to build/card-fronts/")
    print(f"  card size {CARD_W}x{CARD_H} (2.5 by 3.5 inches at 300 dpi)")
    print(f"\n  These are HTML. Rendering them to PNG is the next step and "
          f"needs a\n  headless browser; ops/render_cards.py does that.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
