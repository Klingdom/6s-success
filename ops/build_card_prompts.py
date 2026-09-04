#!/usr/bin/env python3
"""
Write one self-contained image prompt per card, for any deck.

WHY SELF-CONTAINED MATTERS MORE THAN ANYTHING ELSE HERE
-------------------------------------------------------
The Entryway deck's 90 images look like one deck. The chapter plates, made
the same way but across many chats, drifted into two visibly different halves
and had to be swept later. The difference was not the model. It was that a
prompt saying "same style as before" means nothing in a fresh session, and
every fresh session drifts a little further.

So every prompt this writes carries the entire frozen style prefix inside it.
A prompt can be pasted into a brand new chat, on its own, months from now, and
produce something that belongs with the rest. They are longer for it. That is
the whole point.

WHAT ELSE IS BAKED IN
---------------------
The negative list is not generic. Every item on it is a defect that actually
got artwork rejected on this project: text and lettering baked into the
picture, fake QR codes advertising printables that do not exist, brand names
on packaging, and people, who date an image and raise a likeness question.

Each prompt states its output filename, so a generated image drops straight
into the pipeline with no renaming and no guessing which card it was for.

Run:  python ops/build_card_prompts.py --deck mudroom
      python ops/build_card_prompts.py --deck entryway --only-missing
"""
from __future__ import annotations

import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

from generate_card_art import style_prefix, STYLE_SRC, NEGATIVE     # noqa: E402

DESK = os.path.join(os.path.expanduser("~"), "Desktop", "6S-Success-Card-Decks")

DECKS = {
    "entryway": {
        "room": "Entryway",
        "images": os.path.join(DESK, "Entryway Deck", "card-images"),
        # Extracted from Entryway-Deck-CopySpec.md. Only the 36 micro zone,
        # problem and tool cards are specified there; the other 54 have
        # artwork already and their copy lives elsewhere, so they are not
        # reachable from here and do not need to be.
        "cards": os.path.join(ROOT, "build", "entryway-cards.json"),
    },
    "mudroom": {
        "room": "Mudroom",
        "images": os.path.join(DESK, "Mud Room Deck", "card-images"),
        "cards": os.path.join(ROOT, "build", "mudroom-cards.json"),
    },
    # The Kitchen deck is generated, not transcribed, so its card file lives
    # in the repository and its art lives in the repository too. Nothing about
    # it is on the Desktop, so the Desktop guard below does not apply to it:
    # there is no already-illustrated count to protect, because there are
    # zero images and the whole point of this run is to produce the queue
    # that fills that folder the moment image billing is enabled.
    "kitchen": {
        "room": "Kitchen",
        "images": os.path.join(ROOT, "build", "heroes", "kitchen"),
        "cards": os.path.join(ROOT, "ops", "cardtext", "kitchen-deck.json"),
        "desktop_sources": False,
    },
}

# What the illustration should show, per card type. A card type is a promise
# about what the picture is doing, and without this every prompt produces the
# same tidy room from a slightly different angle.
FRAMING = {
    "Room": ("A wide establishing view of the whole {room}, in its settled "
             "state. This is the room's title card, so it should read as the "
             "whole space rather than one corner of it."),
    "Micro Zone": ("A close, straight-on view of one specific area: {card}. "
                   "It is in its finished, working state, with six to eight "
                   "clearly separable elements a numbered callout could point "
                   "at. Nothing is hidden behind anything else."),
    "Problem": ("The same kind of area, but showing the problem honestly: "
                "{card}. Believably lived in rather than staged as a disaster. "
                "It should look like a real Tuesday, not a hoarding scene."),
    "Tool": ("A single physical intervention, {card}, photographed close and "
             "generic. It is the type of object, never a branded product."),
    "Habit": ("A small repeated action in progress, {card}, shown by its "
              "traces and its setup rather than by a person doing it."),
    "Skill": ("A quiet illustration of the underlying idea, {card}, shown "
              "through an arranged space rather than through symbols."),
    "Upgrade": ("The same kind of area after a real improvement, {card}. "
                "Better than the baseline in a way somebody would notice, "
                "without becoming a showroom."),
    "Event": ("The {room} during a specific moment that tests it: {card}. "
              "The pressure should be visible in the objects."),
    "Win / Reward": ("A calm, satisfying view of the {room} holding its "
                     "standard: {card}. Warm and earned, not triumphant."),
    # The Kitchen deck's types. A Zone card and a Friction card are the same
    # place photographed twice, once working and once not, and that pairing
    # is most of what the deck teaches, so the two framings are written to be
    # deliberately comparable rather than independently pretty.
    "Zone": ("A close, straight-on view of one specific area of the {room}: "
             "{card}, in its finished working state. Every numbered callout "
             "listed below has to be a separate visible object that a pin "
             "could point at, with nothing hidden behind anything else."),
    "Friction": ("The same kind of area, showing the problem honestly: "
                 "{card}. Believably lived in, the way a real Tuesday looks, "
                 "not staged as a disaster and not secretly tidy."),
    "Root Cause": ("A single quiet illustration of one idea, {card}, shown "
                   "through one arrangement of ordinary objects rather than "
                   "through symbols. One idea, one object group, no room "
                   "tour."),
    "Action": ("The finished state this action produces: {card}. The result "
               "after the work, never the work itself and never a person "
               "doing it."),
    "Standard": ("The zone holding its standard, calm and ordinary, with a "
                 "generous area of visually quiet surface across the lower "
                 "half of the frame because write-on lines are printed over "
                 "it: {card}."),
}
FRAMING["Win"] = FRAMING["Win / Reward"]


def require_desktop_sources(images_dir: str, needed: bool = True) -> None:
    """Both the frozen Style Bible and the already-illustrated count live only
    on Phil's Desktop. Neither is reachable from a cloud sandbox, and silently
    substituting a fallback style or an empty already-have set produces a
    plausible-looking but wrong file: a different style hash than the one
    every existing card was actually generated against, and prompts asking
    to redo cards that already have real art. Refuse rather than guess, the
    same rule import_chapter_svgs.py already follows for its own Desktop-only
    source.

    A deck whose art folder lives in the repository does not have that
    problem, so it declares desktop_sources False and only the frozen style
    file is required. The style file is never optional: generating against a
    substituted style is how a deck ends up looking like two decks, and that
    has already happened once here.
    """
    if not needed:
        os.makedirs(images_dir, exist_ok=True)
        if not os.path.exists(STYLE_SRC):
            raise SystemExit(
                "cannot write card prompts here: the frozen Style Bible is "
                f"missing at {STYLE_SRC}. Generating against a substituted "
                "style produces a deck that does not match the one already "
                "shipped. Run this on the machine that holds it.")
        return
    missing = [p for p in (STYLE_SRC, images_dir) if not os.path.exists(p)]
    if missing:
        raise SystemExit(
            "cannot write card prompts here: missing " + ", ".join(missing) +
            ". The frozen style and the already-illustrated count both live "
            "only on Phil's Desktop; run this on that machine.")


def slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")


def existing(images_dir: str) -> set:
    out = set()
    for f in glob.glob(os.path.join(images_dir, "*")):
        m = re.match(r"([A-Z]{2}-\d{3})", os.path.basename(f))
        if m:
            out.add(m.group(1))
    return out


def load_cards(deck: str) -> list:
    """Both card file shapes, normalised to the one this file already speaks.

    The transcribed decks are a bare list with title-case keys. The generated
    Kitchen deck is an object with a cards array and lowercase keys, and it
    carries a hand written art record per card: the subject, the things that
    must be visible, and the test that rejects the image. That record is the
    reason the Kitchen prompts can name specific countable objects where the
    Entryway prompts could only describe a mood, and it is why EM-003 shipped
    six callouts over a photograph containing none of them.
    """
    spec = DECKS[deck]
    if not (spec["cards"] and os.path.exists(spec["cards"])):
        raise SystemExit(f"no card data for {deck}")
    raw = json.load(io.open(spec["cards"], encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    out = []
    for c in raw["cards"]:
        art = c.get("art") or {}
        out.append({
            "ID": c["id"],
            "Card": c["title"],
            "Category": (c["type"].replace(" CARD", "").title()
                         .replace("Root Cause", "Root Cause")),
            "Primary 6S": c.get("six_s", ""),
            "Objective / Behavior": c.get("objective", ""),
            "Canonical text": (c.get("tagline") or "").rstrip("."),
            "art_subject": art.get("subject", ""),
            "art_must_show": art.get("must_show", []),
            "art_must_kind": art.get("must_show_kind", "condition"),
            "art_accept": art.get("accept_test", ""),
        })
    return out


def prompt_for(c: dict, room: str, prefix: str) -> str:
    cat = c.get("Category", "").strip()
    frame = FRAMING.get(cat, FRAMING["Micro Zone"]).format(
        room=room, card=c.get("Card", ""))
    obj = c.get("Objective / Behavior", "").strip().rstrip(".")
    canon = c.get("Canonical text", "").strip()

    # The frozen house look names the entryway, because it was written for
    # that deck. Left alone it asks for "a real modern home entryway" on every
    # mudroom card. The room word is the one thing in the prefix allowed to
    # vary, and it varies by substitution so the rest stays identical.
    house = (prefix.replace("entryway", room.lower())
             if room.lower() != "entryway" else prefix)

    # The subject line is the part that stops a prompt producing a nice
    # picture of the wrong thing. Where a card carries a hand written subject
    # it goes in first and in full, because "a key station" is a phrase and
    # "a small dish holding keys, a row of four hooks, a shallow tray" is a
    # list the model can actually draw and a reviewer can actually count.
    subject = c.get("art_subject", "").strip()
    must = [m for m in c.get("art_must_show", []) if m]
    accept = c.get("art_accept", "").strip()
    subject_block = ""
    if subject:
        subject_block = f"SUBJECT, IN FULL. {subject}.\n\n"
    # Only a zone or room card carries a list of things to count. Everywhere
    # else must_show is a condition the picture has to satisfy, and handing a
    # sentence to a model under the heading "objects in the frame" asks it to
    # draw the sentence, which is how lettering gets into an image that
    # explicitly forbade lettering.
    must_block = ""
    if must and c.get("art_must_kind") == "objects":
        must_block = ("EVERY ONE OF THESE HAS TO BE A SEPARATE VISIBLE "
                      "OBJECT IN THE FRAME.\n"
                      + "\n".join(f"  - {m}" for m in must) + "\n\n")
    accept_block = ""
    if accept:
        accept_block = f"HOW THIS IMAGE WILL BE JUDGED. {accept}\n\n"

    return (
        f"{house}\n\n"
        f"SCENE. {frame}\n\n"
        f"{subject_block}"
        f"{must_block}"
        f"WHAT THE PICTURE HAS TO COMMUNICATE. {obj}. "
        f"The idea behind it: {canon}\n\n"
        f"{accept_block}"
        f"COMPOSITION. Landscape, about 3:2, matching the existing card "
        f"heroes at 1536 by 1024. Even, warm, indirect daylight with no "
        f"harsh shadow. Shot straight on at standing eye level. Keep the "
        f"lower left and a strip across the top visually simple, because the "
        f"card template lays the title, the callout pins and the info row "
        f"over them afterwards.\n\n"
        f"MUST NOT CONTAIN. {NEGATIVE}. No seasonal decoration unless the card "
        f"is explicitly about a season. Nothing that would date the image."
    )


def main() -> int:
    deck = "mudroom"
    if "--deck" in sys.argv:
        deck = sys.argv[sys.argv.index("--deck") + 1].lower()
    if deck not in DECKS:
        raise SystemExit(f"unknown deck {deck}, know: {list(DECKS)}")

    spec = DECKS[deck]
    require_desktop_sources(spec["images"],
                            needed=spec.get("desktop_sources", True))
    cards = load_cards(deck)
    prefix, sig = style_prefix()
    have = existing(spec["images"])
    only_missing = "--only-missing" in sys.argv

    todo = [c for c in cards if not (only_missing and c["ID"] in have)]

    out_dir = os.path.join(ROOT, "build", "prompts", deck)
    os.makedirs(out_dir, exist_ok=True)

    written, index = 0, []
    for c in todo:
        fn = f"{c['ID']}-{spec['room']}-{slug(c['Card'])}.png"
        body = prompt_for(c, spec["room"], prefix)
        six = (c.get("Primary 6S") or "").strip()
        header = (
            f"CARD {c['ID']}  {c['Card']}\n"
            f"deck {deck}   type {c.get('Category','')}   "
            + (f"6S {six}   " if six else "")
            + f"style {sig}\n"
            f"save the result as: {fn}\n"
            f"{'-' * 70}\n\n")
        path = os.path.join(out_dir, f"{c['ID']}.txt")
        io.open(path, "w", encoding="utf-8", newline="").write(header + body + "\n")
        index.append({"id": c["ID"], "card": c["Card"],
                      "type": c.get("Category", ""), "file": fn,
                      "have_image": c["ID"] in have})
        written += 1

    # One file holding everything, for pasting a batch into a chat session.
    allp = []
    for c in todo:
        fn = f"{c['ID']}-{spec['room']}-{slug(c['Card'])}.png"
        allp.append(f"### {c['ID']}  {c['Card']}  ->  {fn}\n\n"
                    + prompt_for(c, spec["room"], prefix))
    io.open(os.path.join(out_dir, "ALL.md"), "w", encoding="utf-8",
            newline="").write(
        f"# {spec['room']} deck image prompts\n\n"
        f"Style hash `{sig}`. Every prompt below is self contained: paste any "
        f"one of them into a fresh chat, on its own, and it will produce "
        f"something that belongs with the rest of the deck. Do not shorten "
        f"them by referring back to an earlier image, which is exactly how a "
        f"deck drifts into looking like two decks.\n\n"
        + "\n\n---\n\n".join(allp) + "\n")

    json.dump({"deck": deck, "style_hash": sig, "cards": index},
              io.open(os.path.join(out_dir, "index.json"), "w",
                      encoding="utf-8", newline=""), indent=1,
              ensure_ascii=False)

    # A prompt that leans on a previous image is the failure this exists to
    # prevent, so it is a hard error rather than a note.
    lazy = []
    for c in todo:
        b = prompt_for(c, spec["room"], prefix)
        if re.search(r"same (style|as before)|as above|previous image|like the last",
                     b, re.I):
            lazy.append(c["ID"])
    assert not lazy, f"prompts referring to another image: {lazy[:4]}"

    # Naming the wrong room is the same class of silent error as reading the
    # wrong style bible, so it is checked rather than trusted.
    wrong_room = []
    for c in todo:
        b = prompt_for(c, spec["room"], prefix).lower()
        for other in (r["room"].lower() for k, r in DECKS.items() if k != deck):
            if other in b:
                wrong_room.append((c["ID"], other))
    assert not wrong_room, (
        f"prompts naming a room other than {spec['room']}: {wrong_room[:4]}. "
        f"The frozen prefix carries a room word and it has to be "
        f"substituted, not inherited.")

    lens = [len(prompt_for(c, spec["room"], prefix)) for c in todo]
    print(f"  deck        {deck} ({spec['room']})")
    print(f"  style hash  {sig}")
    print(f"  cards       {len(cards)} total, {len(have)} already have art")
    print(f"  written     {written} prompts to build/prompts/{deck}/")
    print(f"  length      {min(lens)} to {max(lens)} characters, "
          f"average {sum(lens)//len(lens)}")
    print(f"  every prompt is self contained and names its output file")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
