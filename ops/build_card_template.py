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
    """Card data, richest source first.

    build/entryway-cardtext.json is the full copy transcribed back off the 90
    finished cards: objective, quick win, pro tip, reset time, callouts, the
    lot. The two thin json files only carry a name and a canonical line, so
    they fill gaps rather than override.
    """
    out = {}
    for f in ("mudroom-cards.json", "entryway-cards.json"):
        p = os.path.join(ROOT, "build", f)
        if os.path.exists(p):
            for c in json.load(io.open(p, encoding="utf-8")):
                out[c["ID"]] = {
                    "id": c["ID"], "title": c.get("Card", ""),
                    "type": (c.get("Category", "") + " card").upper().strip(),
                    "difficulty": sum(1 for ch in (c.get("Difficulty") or "")
                                      if ch in "★⭐*") or None,
                    "six_s": c.get("Primary 6S", ""),
                    "objective": c.get("Objective / Behavior", ""),
                    "six_s_lesson": c.get("Canonical text", ""),
                    "benefit": c.get("Benefit / Effect", ""),
                }
    rich = os.path.join(ROOT, "build", "entryway-cardtext.json")
    if os.path.exists(rich):
        for c in json.load(io.open(rich, encoding="utf-8"))["cards"]:
            base = out.get(c["id"], {})
            merged = {k: v for k, v in base.items()}
            for k, v in c.items():
                if v not in (None, "", [], "UNREADABLE"):
                    merged[k] = v
            merged.setdefault("six_s", base.get("six_s", ""))
            out[c["id"]] = merged
    return out


def approved_heroes() -> set:
    """Only heroes a person has looked at may become a card.

    Same rule as the zone pages, for the same reason: a card is published
    under the deck's name, and a hero that shows the wrong thing makes the
    card say something its own text does not. The verdict is bound to the
    image's sha, so regenerating a hero drops its card out of the deck until
    somebody looks again rather than silently shipping the new picture.
    """
    p = os.path.join(ROOT, "ops", "card-hero-verdicts.json")
    if not os.path.exists(p):
        return set()
    import hashlib
    raw = json.load(io.open(p, encoding="utf-8"))
    ok = set()
    for stem, rec in raw.items():
        f = os.path.join(HEROES, "entryway", stem + ".png")
        if not isinstance(rec, dict) or rec.get("verdict") != "ok":
            continue
        if not os.path.exists(f):
            continue
        got = hashlib.sha256(io.open(f, "rb").read()).hexdigest()[:10]
        if rec.get("sha") == got:
            ok.add(stem)
    return ok


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


def concept_hero(c: dict, colour: str) -> str:
    """A designed panel for cards a photograph cannot serve.

    Twelve of the 88 failed three rounds of prompting, and the failures were
    structural rather than unlucky. Five name an idea with no object in it at
    all: Visual Control, Label Everything, Weekly Audit. The rest need legible
    lettering in the picture, and the negative prompt suppresses lettering on
    purpose, because that suppression is what keeps garbled text off the deck.
    Asking the model for a readable label is asking it to break the rule that
    makes the deck safe.

    So these get a graphic hero, and it is a design decision rather than a
    fallback: card games have always drawn concept cards differently from
    object cards, and a reader can tell at a glance which kind they hold.

    It carries no sentence. The first version set the card's tagline large and
    printed it twice on the same card, because the tagline is already the
    subtitle four centimetres above. Every other text field is shown further
    down too. So the panel says the one thing nothing else on the card says
    visually: which of the six passes this card belongs to, as six marks with
    this card's own type colour, under the type name set as a monogram.

    It never pretends to be a photograph, which is the part that matters.
    """
    kind = (c.get("type") or "CARD").replace(" CARD", "").strip().upper()
    return (f'<div class="shot concept" style="--tc:{colour}">'
            f'<div class="cinner">'
            f'<div class="cbars" aria-hidden="true">'
            + "".join("<i></i>" for _ in range(6)) +
            f'</div>'
            f'<p class="ckind">{html.escape(kind)}</p>'
            f'</div></div>')


def back_html(c: dict) -> str:
    """One card back.

    The back is not decoration. On these cards it carries best practices, the
    Home Quest challenge, a fact, the next card, a progress tracker and the
    related path: on EE-001 that is more words than the front. A deck printed
    fronts only is half a product, and the corpus has every one of these
    fields on all 88 cards, so there is no reason to ship without them.

    Same conditional rule as the front. A card missing a field gets no empty
    box with a heading over nothing.
    """
    kind = (c.get("type") or "CARD").replace(" CARD", "").strip().title()
    colour = TYPE_COLOUR.get(kind, "#2B2622")
    e = html.escape

    def block(title, body, cls="bk"):
        return (f'<section class="{cls}"><h3>{e(title)}</h3>{body}</section>'
                if body else "")

    bp = c.get("best_practices") or []
    bp_html = ("<ul>" + "".join(f"<li>{e(x)}</li>" for x in bp) + "</ul>"
               if bp else "")

    hq = (c.get("home_quest_challenge") or "").strip()
    hq_html = f"<p>{e(hq)}</p>" if hq else ""

    dk = (c.get("did_you_know") or "").strip()
    dk_html = f"<p>{e(dk)}</p>" if dk else ""

    nc = c.get("next_card") or {}
    nc_html = ""
    if isinstance(nc, dict) and nc.get("id"):
        nc_html = (f'<p><b>{e(nc["id"])}</b> {e(nc.get("title", ""))}<br>'
                   f'<span class="sub">{e(nc.get("line", ""))}</span></p>')

    pt = c.get("progress_tracker") or []
    pt_html = ("<ul class=\"tick\">"
               + "".join(f"<li>{e(x)}</li>" for x in pt) + "</ul>"
               if pt else "")

    rp = c.get("related_path") or {}
    rows = []
    if isinstance(rp, dict):
        for k, v in rp.items():
            if not v:
                continue
            items = v if isinstance(v, list) else [v]
            rows.append(f'<div class="rp"><span>{e(k.replace("_", " "))}</span>'
                        f'{"".join(f"<i>{e(str(x))}</i>" for x in items)}</div>')
    rp_html = "".join(rows)

    foot = (c.get("footer_line") or "").strip()

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600&family=Inter:wght@400;600;700&family=Newsreader:wght@400;500&display=swap">
<style>
*{{box-sizing:border-box}}
html,body{{margin:0;padding:0}}
body{{width:{CARD_W}px;height:{CARD_H}px;background:#F7F2E9;color:#2B2622;
  font:400 15px/1.5 "Newsreader",Georgia,serif;
  display:flex;flex-direction:column;overflow:hidden;
  --tc:{colour}}}
.hd{{background:var(--tc);color:#F7F2E9;padding:15px 24px;display:flex;
  align-items:baseline;gap:12px;flex:0 0 auto}}
.hd b{{font:700 19px/1 "Inter",system-ui,sans-serif;letter-spacing:.06em}}
.hd span{{font:600 11.5px/1 "Inter",system-ui,sans-serif;letter-spacing:.18em;
  text-transform:uppercase;opacity:.85}}
.body{{flex:1 1 auto;padding:24px 24px 18px;display:flex;
  flex-direction:column;justify-content:space-between;gap:16px;
  overflow:hidden}}
h3{{margin:0 0 5px;font:700 10px/1 "Inter",system-ui,sans-serif;
  letter-spacing:.17em;text-transform:uppercase;color:var(--tc)}}
section{{margin:0}}
p{{margin:0}}
ul{{margin:0;padding-left:16px}}
li{{margin:0 0 3px}}
ul.tick{{list-style:none;padding:0;display:grid;grid-template-columns:1fr 1fr;
  gap:3px 12px}}
ul.tick li{{position:relative;padding-left:18px;font-size:13.5px}}
ul.tick li::before{{content:"";position:absolute;left:0;top:3px;width:10px;
  height:10px;border:1.5px solid var(--tc);border-radius:2px;opacity:.55}}
.sub{{color:#6A625A}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:13px 18px}}
.rp{{font:400 13px/1.5 "Inter",system-ui,sans-serif;margin:0 0 4px}}
.rp span{{font-weight:700;text-transform:uppercase;letter-spacing:.1em;
  font-size:9.5px;color:var(--tc);margin-right:6px}}
.rp i{{font-style:normal;color:#6A625A;margin-right:8px}}
.ft{{flex:0 0 auto;background:var(--tc);color:#F7F2E9;padding:12px 24px;
  font:600 11.5px/1.3 "Inter",system-ui,sans-serif;letter-spacing:.04em}}
</style></head><body>
  <div class="hd"><b>{e(c["id"])}</b><span>{e(kind)}</span></div>
  <div class="body">
    {block("Best practices", bp_html)}
    <div class="two">
      {block("Home Quest challenge", hq_html)}
      {block("Did you know", dk_html)}
    </div>
    <div class="two">
      {block("Next card", nc_html)}
      {block("Progress tracker", pt_html)}
    </div>
    {block("Related path", rp_html)}
  </div>
  <div class="ft">{e(foot) if foot else "6S SUCCESS"}</div>
</body></html>"""


def card_html(c: dict, hero_rel: str) -> str:
    """One card front.

    Every section is conditional. A card with no quick win simply has no quick
    win row, rather than an empty box with a heading over nothing. That
    matters because the transcription returns null for anything a card does
    not carry and UNREADABLE for anything it could not read, and neither
    should ever reach a printed card as a blank promise.
    """
    def esc(v):
        return html.escape(str(v).strip()) if v not in (None, "", "UNREADABLE") else ""

    cat = (c.get("type") or "").replace("CARD", "").strip().title()
    colour = TYPE_COLOUR.get(cat, TYPE_COLOUR.get(
        (c.get("type") or "").title().replace(" Card", ""), "#2B2622"))
    n = c.get("difficulty") or 0
    star_row = ("<span class='on'>&#9733;</span>" * n
                + "<span class='off'>&#9733;</span>" * (5 - n)) if n else ""

    six = esc(c.get("six_s") or c.get("Primary 6S"))
    title = esc(c.get("title"))
    tagline = esc(c.get("tagline"))
    obj = esc(c.get("objective"))
    if obj.lower() == title.lower():
        obj = ""                      # a box repeating the title is not a box
    lesson = esc(c.get("six_s_lesson"))
    quick = esc(c.get("quick_win"))
    action = esc(c.get("real_world_action"))
    tip = esc(c.get("pro_tip"))
    reset = esc(c.get("reset_time"))
    maint = esc(c.get("maintenance"))
    fam = c.get("family_friendly") or 0

    callouts = [x for x in (c.get("callouts") or [])
                if x and x != "UNREADABLE"]
    legend = ""
    if callouts:
        items = "".join(
            f'<li><i>{i}</i>{html.escape(str(t))}</li>'
            for i, t in enumerate(callouts, 1))
        legend = f'<ol class="legend">{items}</ol>'

    def cell(label, value):
        return (f'<div class="cell"><h3>{label}</h3><p>{value}</p></div>'
                if value else "")

    row1 = "".join([cell("Objective", obj), cell("Quick win", quick),
                    cell("Real world action", action)])
    row2 = "".join([cell("The 6S lesson", lesson), cell("Pro tip", tip)])

    foot_bits = []
    if reset:
        foot_bits.append(f'<span><b>Reset</b> {reset}</span>')
    if maint:
        foot_bits.append(f'<span><b>Upkeep</b> {maint}</span>')
    if fam:
        foot_bits.append('<span><b>Family</b> '
                         + "&#9733;" * fam + '</span>')
    if not foot_bits and six:
        foot_bits.append(f'<span class="s">{six}</span>')

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
  gap:13px;padding:15px 22px;font-family:"Inter",system-ui,sans-serif;
  flex:0 0 auto}}
.code{{font-weight:700;font-size:18px;font-variant-numeric:tabular-nums}}
.kind{{font-weight:600;font-size:11.5px;letter-spacing:.16em;
  text-transform:uppercase;opacity:.92}}
.diff{{margin-left:auto;font-size:14px;letter-spacing:1px;white-space:nowrap}}
.diff .off{{opacity:.34}}
.head{{padding:18px 24px 12px;flex:0 0 auto}}
h1{{font-family:"Fraunces",Georgia,serif;font-weight:700;font-size:40px;
  line-height:1.01;letter-spacing:-.024em;text-wrap:balance}}
.tag{{margin-top:7px;font-family:"Inter",system-ui,sans-serif;font-size:11.5px;
  font-weight:600;letter-spacing:.05em;text-transform:uppercase;color:#6A625A}}
.shot{{margin:0 24px;border-radius:12px;overflow:hidden;
  border:1px solid #E2D8C4;flex:1 1 auto;min-height:250px;background:#F2EADC}}
.shot img{{width:100%;height:100%;object-fit:cover;display:block}}
/* The concept hero. Deliberately not photographic: flat ground, one motif,
   one word. Centred as a group so the panel does not read as a picture that
   failed to load, which is what a single line pinned to the bottom looked
   like. */
.shot.concept{{display:flex;align-items:center;justify-content:center;
  background:color-mix(in srgb, var(--tc) 8%, #F7F2E9);
  border-color:color-mix(in srgb, var(--tc) 24%, #E2D8C4)}}
.cinner{{display:flex;flex-direction:column;align-items:center;gap:34px;
  width:100%;padding:0 34px}}
/* Big on purpose. At motif size it read as a picture that had failed to
   load; at this size it reads as the card's own graphic. */
.cbars{{display:flex;gap:14px;align-items:flex-end;height:330px;width:100%}}
.cbars i{{display:block;flex:1 1 0;background:var(--tc);border-radius:6px;
  opacity:.22}}
.cbars i:nth-child(1){{height:34%}} .cbars i:nth-child(2){{height:50%}}
.cbars i:nth-child(3){{height:65%}} .cbars i:nth-child(4){{height:79%}}
.cbars i:nth-child(5){{height:90%}} .cbars i:nth-child(6){{height:100%;opacity:.80}}
.ckind{{margin:0;font-family:"Inter",system-ui,sans-serif;font-weight:700;
  font-size:22px;letter-spacing:.32em;text-indent:.32em;color:var(--tc);
  opacity:.85}}
.legend{{margin:12px 24px 0;padding:0;list-style:none;display:grid;
  grid-template-columns:1fr 1fr;gap:4px 16px;flex:0 0 auto}}
.legend li{{font-family:"Inter",system-ui,sans-serif;font-size:10.5px;
  line-height:1.35;color:#584F46;display:flex;gap:6px;align-items:baseline}}
.legend i{{flex:0 0 15px;height:15px;border-radius:50%;background:{colour};
  color:#FBF7EF;font-style:normal;font-weight:700;font-size:9px;
  text-align:center;line-height:15px}}
.rows{{padding:13px 24px 0;display:flex;flex-direction:column;gap:9px;
  flex:0 0 auto}}
.row{{display:flex;gap:9px}}
.cell{{flex:1;border:1px solid #E2D8C4;background:#F7F2E9;border-radius:10px;
  padding:10px 12px}}
.cell h3{{font-family:"Inter",system-ui,sans-serif;font-size:8.5px;
  font-weight:700;letter-spacing:.14em;text-transform:uppercase;
  color:{colour};margin-bottom:4px}}
.cell p{{font-size:13px;line-height:1.35}}
.foot{{margin-top:auto;display:flex;align-items:center;gap:16px;
  padding:12px 24px 16px;font-family:"Inter",system-ui,sans-serif;
  font-size:10px;font-weight:500;letter-spacing:.06em;text-transform:uppercase;
  color:#8C8478;border-top:1px solid #E2D8C4;flex:0 0 auto}}
.foot b{{color:{colour};font-weight:700;letter-spacing:.12em}}
.foot .brand{{margin-left:auto;letter-spacing:.18em;font-weight:600}}
</style>
<div class="card">
  <div class="band">
    <span class="code">{esc(c.get('id'))}</span>
    <span class="kind">{esc(c.get('type'))}</span>
    <span class="diff">{star_row}</span>
  </div>
  <div class="head">
    <h1>{title}</h1>
    {f'<p class="tag">{tagline}</p>' if tagline else (f'<p class="tag">{six}</p>' if six else '')}
  </div>
  {hero_rel if hero_rel.startswith("<") else f'<div class="shot"><img src="{hero_rel}" alt=""></div>'}
  {legend}
  <div class="rows">
    {f'<div class="row">{row1}</div>' if row1 else ''}
    {f'<div class="row">{row2}</div>' if row2 else ''}
  </div>
  <div class="foot">{"".join(foot_bits)}<span class="brand">6S Success</span></div>
</div>
"""


def main() -> int:
    allc = cards()
    ok = approved_heroes()
    have, held = {}, []
    # Scan the entryway folder only. The glob used to sweep every folder under
    # build/heroes, which also holds entryway-legacy, where the same card codes
    # appear under longer filenames. Two files matching one card code, resolved
    # by whichever the glob returned last, is not a lookup, it is a coin toss.
    for f in sorted(glob.glob(os.path.join(HEROES, "entryway", "*.png"))):
        m = re.match(r"([A-Z]{2}-\d{3})", os.path.basename(f))
        if not m:
            continue
        if m.group(1) not in ok:
            held.append(m.group(1))
            continue
        have[m.group(1)] = f
    if held:
        print(f"  held back        {len(held)} hero(es) not approved in review, "
              f"so those cards are not rendered")

    if "--list" in sys.argv or len(sys.argv) == 1:
        print(f"  heroes available : {len(have)}")
        for code, f in sorted(have.items()):
            c = allc.get(code, {})
            ok = "ok" if c else "NO CARD DATA"
            print(f"    {code}  {c.get('title','?'):26} {ok}")
        missing = [c for c in have if c not in allc]
        if missing:
            print(f"\n  {len(missing)} heroes have no card data and cannot be "
                  f"rendered: {missing}")
        return 0

    # Every card in THIS deck, not every card the data files know about.
    # cards() merges sources and its richest one also carries the Mudroom
    # deck, so taking all of allc queued 92 cards from another room, none of
    # them reviewed. Caught by the count being 180 rather than 88. The deck's
    # membership is the transcribed corpus, so that is what defines it.
    corpus = json.load(io.open(os.path.join(ROOT, "build",
                                            "entryway-cardtext.json"),
                               encoding="utf-8"))
    want = [c["id"] for c in corpus["cards"]]
    others = sorted(set(allc) - set(want))
    if others:
        print(f"  {len(others)} card(s) in the data files belong to another "
              f"deck or have no transcribed text, and are not built here: "
              f"{others[:4]}")
    if "--card" in sys.argv:
        want = [sys.argv[sys.argv.index("--card") + 1].upper()]

    os.makedirs(OUT, exist_ok=True)
    made = []
    concept = 0
    for code in want:
        if code not in allc:
            print(f"  {code}: no card data, refusing to invent it")
            continue
        if code in have:
            rel = os.path.relpath(have[code], OUT).replace(os.sep, "/")
        else:
            # No approved photograph, so the card gets the designed panel
            # rather than being dropped from the deck. A deck missing twelve
            # of its 88 cards is not a deck.
            c = allc[code]
            kind = (c.get("type") or "").replace(" CARD", "").title()
            rel = concept_hero(c, TYPE_COLOUR.get(kind, "#2B2622"))
            concept += 1
        p = os.path.join(OUT, f"{code}.html")
        io.open(p, "w", encoding="utf-8", newline="").write(
            card_html(allc[code], rel))
        b = os.path.join(OUT, f"{code}-back.html")
        io.open(b, "w", encoding="utf-8", newline="").write(
            back_html(allc[code]))
        made.append((code, p))

    print(f"  wrote {len(made)} card fronts as HTML to build/card-fronts/")
    if concept:
        print(f"  {concept} of them use the designed concept panel because no "
              f"photograph passed review for that card")
    print(f"  card size {CARD_W}x{CARD_H} (2.5 by 3.5 inches at 300 dpi)")
    print(f"\n  These are HTML. Rendering them to PNG is the next step and "
          f"needs a\n  headless browser; ops/render_cards.py does that.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
