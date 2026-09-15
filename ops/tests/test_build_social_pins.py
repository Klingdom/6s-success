#!/usr/bin/env python3
"""
Prove the Pinterest/Instagram cards say the zone's standard whole, use only
approved zone pictures, and cannot silently regress to the layout bugs they
were rebuilt to avoid.

ops/build_social_pins.py (rebuilt 2026-09-15) leads each card with the zone's
approved illustration, fits the checklist in the browser and fails the build
on overflow. The browser half is exercised by the build itself. This test
covers what can be checked without a browser, in a CI that has none:

  1. done_items() keeps every word of the standard and never returns the
     fragments the old comma split produced: the Landing Zone's four items
     exactly (the old split lost "one wallet and"), the shower caddy's list
     kept whole under its shared qualifier, "soles down" kept with its item,
     and no item that is a bare count ("One wash").
  2. approved_art() matches quest-data.js exactly, and every stem has its
     -lg.jpg on disk.
  3. A card with a picture uses that zone's own file, shows first sentences,
     keeps the full wording in a template for the text-only fallback, and
     embeds the fit script with its floors filled in.
  4. A zone without an approved picture gets no picture element.
  5. No vh or vw unit survives in either stylesheet. A DOM dump lays out at a
     different viewport than a screenshot, so a vh size would make the fit
     verdict describe a different card than the one saved.
  6. Every Pinterest description ends in its zone link, never carries a
     truncation mark, and every caption is within its platform's limit.

Run:  python ops/tests/test_build_social_pins.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import build_mobile_corpus as BMC  # noqa: E402
import build_social_pins as P  # noqa: E402
import video_zone as VZ  # noqa: E402


def zone(room, name):
    return next(z for r, z in VZ.zones() if r == room and z["zone"] == name)


def words(text):
    return re.findall(r"[a-z0-9']+", text.lower())


def main() -> int:
    fails = []

    # 1. the split
    landing = P.done_items(zone("Entryway", "Landing Zone"))
    want = ["One tray holding keys and sunglasses", "One wallet and one phone per adult",
            "A single upright folder with fewer than ten sheets of paper standing in it",
            "Bare surface on both sides of the tray"]
    if landing != want:
        fails.append("Landing Zone items changed: %r" % landing)
    shower = P.done_items(zone("Primary Bathroom", "Shower or Tub"))
    if not shower or shower[0] != "One shampoo, one conditioner, one wash, and one bar per person in the caddy":
        fails.append("shower caddy list was split apart: %r" % shower[:2])
    shoes = P.done_items(zone("Entryway", "Shoe and Boot Zone"))
    if "Two pairs per person on the rack, soles down" not in shoes:
        fails.append("a trailing modifier left its item: %r" % shoes[:2])
    count_only = re.compile(r"^(one|two|three|a|an|no)[ ][a-z]+$", re.I)
    lost, bare = [], []
    for r, z in VZ.zones():
        items = P.done_items(z)
        raw = words(str(z.get("done_looks_like") or ""))
        got = words(" ".join(items))
        if got != [w for w in raw if w != "and"] and got != raw:
            if sorted(set(raw) - set(got) - {"and"}):
                lost.append("%s / %s" % (r, z["zone"]))
        bare += ["%s / %s: %r" % (r, z["zone"], i) for i in items if count_only.match(i)]
    if lost:
        fails.append("done_items dropped words of the standard for %d zone(s): %r" % (len(lost), lost[:3]))
    if bare:
        fails.append("bare count items: %r" % bare[:3])

    # 2. approvals
    src = BMC.load_source()
    approved = {(r["room"], z["zone"]): z["img"] for r in src["rooms"] for z in r["zones"] if z.get("img")}
    art = P.approved_art()
    if art != approved:
        fails.append("approved_art() differs from quest-data.js img stems")
    if len(art) < 100:
        fails.append("expected about 106 approved pictures, got %d" % len(art))
    missing = [s for s in art.values() if not os.path.exists(os.path.join(P.ZONE_ART, s + "-lg.jpg"))]
    if missing:
        fails.append("approved stems with no -lg.jpg: %r" % missing[:3])

    # 3. a picture card
    r, z = "Entryway", zone("Entryway", "Landing Zone")
    stem = art.get((r, z["zone"]))
    if not stem:
        fails.append("Landing Zone has no approved picture to test with")
    else:
        doc = P.card_html(r, z, P.PIN_W, P.PIN_H, stem, "pinterest")
        if ("/site/assets/zones/%s-lg.jpg" % stem) not in doc:
            fails.append("picture card does not use its own zone picture")
        if '<html class="has-art">' not in doc:
            fails.append("picture card lacks the has-art class its type sizes hang on")
        shown = re.search(r"<ul>(.*?)</ul>", doc, re.S).group(1)
        kept = re.search(r'<template id="full-items">(.*?)</template>', doc, re.S)
        if not kept:
            fails.append("picture card has no full-items template for the fallback")
        for item in P.done_items(z):
            if P.first_sentence(item) not in shown:
                fails.append("shown checklist is missing %r" % P.first_sentence(item)[:40])
            if kept and item not in kept.group(1):
                fails.append("fallback template lost %r" % item[:40])
        if "%(" in doc or "data-fit" not in doc or "dropTrailing(3, 1)" not in doc:
            fails.append("fit script not embedded, or its placeholders not filled")
        if "0.22*H" not in doc or "0.022*H" not in doc:
            fails.append("fit script floors are not ART_FLOOR/TYPE_FLOOR")
        if re.search(r"[0-9]vh|[0-9]vw", doc.split("</style>", 1)[0]):
            fails.append("a vh/vw unit survived in the picture card stylesheet")

    # 4. and 5. a text-only card
    no_art = next(((rr, zz) for rr, zz in VZ.zones() if (rr, zz["zone"]) not in art), None)
    if no_art is None:
        fails.append("no zone without an approved picture to test with")
    else:
        doc2 = P.card_html(no_art[0], no_art[1], P.IG_W, P.IG_H, None, "instagram")
        # The fit script names .art and full-items itself, so look for elements.
        if '<div class="art">' in doc2 or "/site/assets/zones/" in doc2 or '<template id="full-items">' in doc2:
            fails.append("a zone with no approved picture got a picture")
        if re.search(r"[0-9]vh|[0-9]vw", doc2.split("</style>", 1)[0]):
            fails.append("a vh/vw unit survived in the text-only stylesheet")

    # 6. captions: the link is never cut. With whole checklist items, the old
    # 490-character cut landed inside the closing link line on 15 zones and
    # removed the URL (found 2026-09-15). The checklist must give way instead.
    import build_social_captions as SC
    cut, dots, over = [], [], []
    for rr, zz in VZ.zones():
        cap = SC.build_one(rr, zz)
        desc = cap["pinterest"]["description"]
        if not desc.endswith(cap["url"]):
            cut.append("%s / %s" % (rr, zz["zone"]))
        if "..." in desc:
            dots.append("%s / %s" % (rr, zz["zone"]))
        if len(desc) > 500 or len(cap["pinterest"]["title"]) > 100 or len(cap["instagram"]["caption"]) > 2200:
            over.append("%s / %s" % (rr, zz["zone"]))
    if cut:
        fails.append("pin descriptions that do not end in their zone link: %r" % cut[:3])
    if dots:
        fails.append("pin descriptions carrying a truncation mark: %r" % dots[:3])
    if over:
        fails.append("captions over a platform limit: %r" % over[:3])

    if P.first_sentence("Stops... or spreads. Then more") != "Stops... or spreads":
        fails.append("first_sentence cut at an ellipsis")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: social pins, whole standards (no fragments, no lost words), %d approved pictures, "
          "picture/text-only/fallback/unit checks pass" % len(art))
    return 0


if __name__ == "__main__":
    sys.exit(main())
