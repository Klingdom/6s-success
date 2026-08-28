#!/usr/bin/env python3
"""
Write every card art prompt that is actually needed, into one file.

WHY ONE FILE
------------
Per card files are useful to a script and useless to a person. Phil is
generating these by hand, so what he needs is one document he can work down
from top to bottom without opening 92 things.

WHY 92 AND NOT 180
------------------
The entryway deck already has all 90 of its images. Reprinting prompts for
art that exists would bury the real work list in noise. So this carries:

    the mudroom deck        88 cards with no art yet
    the entryway deck        4 cards its own copy spec flags for regeneration

The four are not arbitrary. EP-005 and ET-007 have brand names visible in the
artwork, which the negative list forbids and which is a real legal exposure on
a product page. EM-005 and EM-006 are marked REGEN in the spec.

THE HANDOFF
-----------
Every prompt states the exact filename to save. Drop the file into
Desktop/6S-Generated-Images and run ops/import_generated_art.py, which
checks it, files it into the right deck, splits front from back, rebuilds the
gallery and re-fingerprints. Nothing to rename, no folder to choose.

Run:  python ops/build_all_prompts.py
"""
from __future__ import annotations

import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

from build_card_prompts import DECKS, prompt_for, slug, existing   # noqa: E402
from generate_card_art import style_prefix                          # noqa: E402

OUT = os.path.join(ROOT, "build", "prompts", "ALL-PROMPTS.md")

# Entryway cards the deck's own copy spec flags as needing new art, and the
# reason, so nobody has to go and look it up.
ENTRYWAY_REGEN = {
    "EM-005": "marked REGEN in the copy spec",
    "EM-006": "marked REGEN in the copy spec",
    "EP-005": "a brand name is visible in the current artwork",
    "ET-007": "a brand name is visible in the current artwork",
}

HOWTO = """\
# 6S Success card art prompts

Every prompt that is actually needed, in one place.

## How to use this

1. Copy one prompt below, the whole thing, into your image tool.
2. Save the result with the exact filename the prompt gives you.
3. Put the file in `Desktop\\6S-Generated-Images\\`.
4. From the repository, run `python ops/import_generated_art.py --apply`.

Step four checks the image, files it into the right deck, splits the front
from the back, rebuilds the gallery and re-fingerprints the assets. There is
nothing to rename and no folder to choose. Anything that fails a check moves
to `_rejected` with the reason printed, and never reaches the site.

## Two rules that matter more than they look

**Paste the whole prompt, including the long opening paragraph, every time.**
It repeats on every card on purpose. A prompt that says "same style as
before" means nothing in a fresh session, and that is exactly how this
project's book plates drifted into two visibly different halves that had to
be swept later.

**The image must contain no text at all.** Not a title, not a label, not a
sign in the background. The card template lays the title, the callout pins,
the difficulty stars and the info row over the photograph afterwards. That is
why the existing cards have no garbled lettering on them, and generated text
cannot be removed later.

## What is in here, and what is not

The entryway deck already has all 90 of its images, so it appears here only
for the four cards its own copy spec flags for regeneration. Everything else
below is the mudroom deck, whose writing is complete and whose art is not.
"""


def load(deck: str) -> list:
    p = DECKS[deck].get("cards")
    if not p or not os.path.exists(p):
        return []
    return json.load(io.open(p, encoding="utf-8"))


def main() -> int:
    prefix, sig = style_prefix()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)

    plan = []

    mud = load("mudroom")
    have_mud = existing(DECKS["mudroom"]["images"])
    plan.append(("Mudroom", "mudroom",
                 [c for c in mud if c["ID"] not in have_mud], mud, have_mud))

    ent = load("entryway")
    regen = [c for c in ent if c["ID"] in ENTRYWAY_REGEN]
    plan.append(("Entryway", "entryway", regen, ent,
                 existing(DECKS["entryway"]["images"])))

    parts = [HOWTO, "", f"Style hash `{sig}`. "
             f"{sum(len(t) for _, _, t, _, _ in plan)} prompts below.", ""]

    for room, deck, todo, allc, have in plan:
        if not todo:
            continue
        parts += ["---", "", f"# {room} deck", ""]
        if deck == "entryway":
            parts += [f"{len(allc)} cards in the spec, all 90 illustrated. "
                      f"These {len(todo)} need replacing.", ""]
        else:
            parts += [f"{len(allc)} cards written, {len(have)} illustrated, "
                      f"{len(todo)} below.", ""]

        for c in todo:
            fn = f"{c['ID']}-{room}-{slug(c['Card'])}.png"
            parts += [f"## {c['ID']}  {c['Card']}", ""]
            if c["ID"] in ENTRYWAY_REGEN:
                parts += [f"> Replacing existing art: "
                          f"{ENTRYWAY_REGEN[c['ID']]}.", ""]
            parts += [
                f"Type: {c.get('Category', '')} &nbsp;&nbsp; "
                f"6S: {c.get('Primary 6S', '')}".replace("&nbsp;", " "),
                "",
                f"**Save as:** `{fn}`",
                "",
                "```text",
                prompt_for(c, room, prefix),
                "```",
                "",
            ]

    io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(parts))

    body = io.open(OUT, encoding="utf-8").read()
    n = body.count("**Save as:**")
    want = sum(len(t) for _, _, t, _, _ in plan)
    assert n == want, f"wrote {n} prompts, expected {want}"
    assert "same style as before" not in body.lower().replace(
        'says "same style as\nbefore"', ""), "a prompt leans on another image"

    # Every prompt must name a file the importer can route. A prompt whose
    # filename does not start with a known card code is a dead end.
    import re
    names = re.findall(r"\*\*Save as:\*\* `([^`]+)`", body)
    bad = [f for f in names if not re.match(r"^[A-Z]{2}-\d{3}-", f)]
    assert not bad, f"filenames the importer cannot route: {bad[:3]}"
    assert len(set(names)) == len(names), "two prompts name the same file"

    print(f"  style hash   {sig}")
    for room, deck, todo, allc, have in plan:
        print(f"  {room:10} {len(allc):>3} cards, {len(have):>3} illustrated, "
              f"{len(todo):>3} prompts written")
    print()
    print(f"  ONE FILE     build/prompts/ALL-PROMPTS.md")
    print(f"               {want} prompts, {os.path.getsize(OUT)//1024} KB")
    print(f"  drop images  {os.path.join(os.path.expanduser('~'), 'Desktop', '6S-Generated-Images')}")
    print(f"  then run     python ops/import_generated_art.py --apply")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
