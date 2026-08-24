#!/usr/bin/env python3
"""
Write ready-to-paste image prompts, prioritised so nobody generates 228 pictures.

THE PROBLEM THIS SOLVES
-----------------------
Zero of the 114 zone pages carry an image. Eleven of the twenty rooms have no
photography at all. Fixing that properly would be 228 before-and-after pairs,
which is weeks of somebody sitting at a chat window, and most of those images
would sit on pages nobody has visited yet.

So this does not generate a prompt per zone. It ranks, and it says why.

WHY PROMPTS RATHER THAN GENERATED IMAGES
----------------------------------------
No image generation tool is available in this environment. That is the honest
reason, and it is worth stating plainly rather than dressing up: the pictures
have to be made somewhere else and brought back. What can be done here is make
that trip as short and as repeatable as possible, which means every prompt is
self contained, carries its own style anchor, and names the exact filename the
result should be saved as.

WHY THERE ARE FEWER SAFETY DRAWINGS THAN THERE WERE
---------------------------------------------------
This file used to generate a bespoke safety illustration prompt for every zone
that carries a hazard, which is all 114 of them. Counted against content.json,
those 114 zones contain exactly FIVE distinct hazard categories. Five drawn SVG
icons in ops/hazard_icons.py now cover all 251 hazard entries, deterministically
and with no generation cost, so the per-zone safety prompt was removed.

WHY EACH PROMPT REPEATS THE WHOLE STYLE
---------------------------------------
A chat model drifts. Ten images into a session the outlines thicken, the palette
warms, and image eleven no longer sits beside image one. The fix that works is
a fresh chat per image with the entire style restated, which is wasteful of
tokens and cheap compared to regenerating a set that no longer matches. So the
anchor below is repeated verbatim in every single prompt, on purpose.

Run:  python ops/build_image_prompts.py
      python ops/build_image_prompts.py --tier 1
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(ROOT, "content", "images", "prompts")
INTAKE = "content/images/intake"

# Frozen. Changing any of this invalidates every image already made, so it is
# stated once, versioned, and repeated verbatim into every prompt below.
STYLE_VERSION = "v2"

PALETTE = ("paper #F7F2E9, panel #FBF7EF, ink #2B2622, terracotta #BC4B2A, "
           "honey #DDA63A, slate #3C5A6B, green #6E8B5B, spark #CB4B36")

PHOTO_ANCHOR = f"""STYLE ANCHOR, {STYLE_VERSION}, follow exactly and do not
interpret loosely. A photograph taken on an ordinary phone camera by the person
who lives here, not a DSLR and not a real-estate listing shot: flatter
perspective, framed slightly closer or slightly higher than a stylist would
choose, focus deep enough that the whole zone reads clearly rather than a
shallow blurred background. Standing or kneeling height, the way a person
actually reaches this spot. Available daylight from whatever window is actually
there, uneven the way real daylight is, no fill flash, no visible light shafts,
no lens flare. Materials read as real: oak, painted drywall, waxed cotton,
brushed steel, worn rubber, not a glossy showroom finish. Warm and slightly
used, sitting in this palette and no other colour story: {PALETTE}. Include one
or two small honest imperfections: a scuff on the trim, a worn patch on a mat, a
mismatched hanger, a chipped mug, a faint fingerprint mark near a switch.
Include one small specific household detail that makes this one particular
family's house rather than a display home: a pet bed, a child's height marks on
a doorframe, a sticker on a drawer front, a slightly bent blind slat. Nothing in
the frame coordinates on purpose. Hangers, containers and furniture are the
ordinary mismatched mix a household actually owns, not a matched set.
AVOID: DSLR product photography, shallow depth of field with a blurred or creamy
background, centered or symmetrical composition, staged or fan arranged clutter,
colour coordinated wardrobes or accessories, glossy advertising sheen, neon or
saturated plastic colours, any colour story other than the palette above, fake
grime, theatrical mess, cold blue light, lens flare or visible light shafts,
phone screens or any on screen interface of any kind, readable text or logos of
any kind, any person, any hand, any limb or body part, a spotless unworn
surface, showroom emptiness."""

LINE_ANCHOR = f"""STYLE ANCHOR, {STYLE_VERSION}, follow exactly and do not
interpret loosely. Warm hand-drawn editorial spot illustration: roughly 3px ink
outline of even weight, flat fills with no gradients, gently rounded forms,
generous negative space. Flat panel-cream background. Palette strictly:
{PALETTE}, with spark #CB4B36 reserved exclusively for a hazard or a point of
friction and used nowhere else. Feels like a thoughtful instructional book.
AVOID: photorealism, shading, gradients, drop shadows, comic action lines,
glossy 3D rendering, harsh or varying outline weight, busy texture, cartoon
faces, readable text or labels of any kind."""


def esc_slug(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (t or "").lower()).strip("-")


def load() -> list:
    d = json.load(io.open(SRC, encoding="utf-8"))
    return d["rooms"]


# TIER 0 is the only number that matters, and the first version of this file got
# it wrong. Ranking by room produced 93 "priority" prompts, which is not a
# priority, it is a second backlog. At one fresh chat per image that is most of
# a week of somebody's evenings, spent on pages that currently receive no
# visitors at all.
#
# So tier 0 is nine images: three before-and-after pairs and three safety
# drawings, chosen because each one earns its place on a page that already
# exists and is already linked from the free products.
#
#   the entryway drop zone   the free deck is built around it, and it is the
#                            zone the whole method opens with
#   the kitchen prep counter the most searched surface in the house
#   the garage workbench     the strongest before-and-after in the catalogue,
#                            and the one that proves the method on a hard room
#
# Nine is a single evening. If those nine change how the site reads, the case
# for the next thirty is made with evidence rather than by ranking rooms in a
# spreadsheet.
TIER0 = [
    ("Entryway", "Landing Zone"),
    ("Kitchen", "Primary Prep Counter"),
    ("Garage", "Primary Workbench"),
]

# Tier 1 is the next expansion, not a starting point. Rooms the free products
# already cover, plus the rooms whose pages carry the most searchable intent.
TIER1_ROOMS = ["Entryway", "Kitchen", "Garage", "Pantry", "Primary Bathroom"]


def zone_prompts(room: dict, zone: dict, tier: int) -> list:
    """A before and an after for one zone, plus one illustration where the zone
    has a hazard worth drawing."""
    rs, zs = esc_slug(room["room"]), esc_slug(zone["zone"])
    purpose = " ".join((zone.get("purpose") or "").split())
    done = " ".join((zone.get("done_looks_like") or "").split())
    sort_pass = " ".join(((zone.get("passes") or {}).get("sort") or "").split())

    out = []
    out.append({
        "file": f"{rs}--{zs}--before.jpg",
        "kind": "photograph",
        "tier": tier,
        "prompt": (
            f"A photograph of this exact subject: {purpose}\n\n"
            f"Show it BEFORE any work, in the honest state described here: "
            f"{sort_pass[:400]}\n\n"
            "The clutter must be the ordinary kind that accumulates in a home "
            "where people are busy, never theatrical and never filthy. A viewer "
            "should recognise their own house and feel understood rather than "
            "judged.\n\n" + PHOTO_ANCHOR)
    })
    out.append({
        "file": f"{rs}--{zs}--after.jpg",
        "kind": "photograph",
        "tier": tier,
        "prompt": (
            f"A photograph of this exact subject: {purpose}\n\n"
            "MATCHED PAIR: identical camera position, height, framing, lens and "
            f"light to the before image named {rs}--{zs}--before.jpg. Only the "
            "state of the zone changes. This is the whole point of the pair, so "
            "if the angle moves the image is unusable.\n\n"
            f"Show it AFTER, in exactly this finished state: {done[:400]}\n\n"
            "Calm and uncrowded, not sterile and not showroom-empty. It still "
            "has to look like somebody lives there.\n\n" + PHOTO_ANCHOR)
    })

    # The safety illustration used to be generated here, one per zone. Five
    # coded icons in ops/hazard_icons.py now cover all 114 zones, so this
    # returns photographs only and the image programme shrank by a third.
    return out


def main() -> int:
    want_tier = None
    if "--tier" in sys.argv:
        want_tier = int(sys.argv[sys.argv.index("--tier") + 1])

    rooms = load()
    items = []
    for r in rooms:
        for z in r["zones"]:
            if (r["room"], z["zone"]) in TIER0:
                tier = 0
            elif r["room"] in TIER1_ROOMS:
                tier = 1
            else:
                tier = 2
            items.extend(zone_prompts(r, z, tier))

    if want_tier:
        items = [i for i in items if i["tier"] == want_tier]

    os.makedirs(OUT, exist_ok=True)

    by_tier = {}
    for i in items:
        by_tier.setdefault(i["tier"], []).append(i)

    for tier, group in sorted(by_tier.items()):
        path = os.path.join(OUT, f"tier-{tier}-prompts.md")
        head = ("# Start here: nine images" if tier == 0
                else f"# Image prompts, tier {tier}")
        note = ("**This is the whole first batch.** Nine images, one evening. "
                "Everything in tier 1 and tier 2 is a backlog to draw from "
                "later, and only worth starting once these nine have shown "
                "whether they change anything."
                if tier == 0 else
                "A backlog, not a to-do list. Take from it when a specific page "
                "needs a specific picture.")
        L = [head, "",
             f"{len(group)} images. Style anchor {STYLE_VERSION}.", "",
             note, "",
             "## How to run these",
             "",
             "1. **One image per fresh chat.** Not a batch. A chat model drifts, "
             "and by the tenth image in a session the outlines have thickened "
             "and the palette has warmed. A fresh chat per image is the only "
             "thing that reliably stops it.",
             "2. Paste one prompt block, whole, including the style anchor. The "
             "anchor is repeated in every prompt on purpose.",
             "3. Save the result under the exact filename given. The filename is "
             f"how it gets wired in; anything else will not be found.",
             f"4. Drop the files into `{INTAKE}/` and tell Claude. The wiring is "
             "automatic from there.",
             "",
             "**Before and after pairs must be generated back to back in the "
             "same chat**, because the after prompt refers to the before image. "
             "That is the one exception to the fresh-chat rule, and it exists "
             "because a pair whose camera moved is worthless.",
             "",
             "---",
             ""]
        for i, item in enumerate(group, 1):
            L += [f"## {i}. `{item['file']}`", "",
                  f"*{item['kind']}*", "", "```", item["prompt"], "```", "",
                  "---", ""]
        io.open(path, "w", encoding="utf-8", newline="").write("\n".join(L))
        photos = sum(1 for x in group if x["kind"] == "photograph")
        print(f"  {os.path.relpath(path, ROOT)}")
        print(f"    {len(group)} prompts, {photos} photographs, "
              f"{len(group) - photos} line drawings")

    os.makedirs(os.path.join(ROOT, INTAKE), exist_ok=True)

    # Every prompt has to carry its anchor or the set drifts, and drift is only
    # visible once a dozen images already exist.
    for item in items:
        anchor = PHOTO_ANCHOR if item["kind"] == "photograph" else LINE_ANCHOR
        assert anchor in item["prompt"], f"{item['file']} lost its style anchor"
        assert STYLE_VERSION in item["prompt"], f"{item['file']} is unversioned"
    print(f"  checked: all {len(items)} prompts carry the {STYLE_VERSION} anchor")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
