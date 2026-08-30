#!/usr/bin/env python3
"""
Pick up generated card art from wherever Phil saved it, and file it correctly.

TWO DIFFERENT ARTEFACTS, WHICH IS THE WHOLE COMPLICATION
--------------------------------------------------------
A **card sheet** is a finished card: two portrait panels, front and back, side
by side with a white gutter, all the text and callout pins already on it. The
90 entryway cards are these. They get split into faces and published.

A **hero photograph** is just the picture: one landscape frame, about 4:3, with
no card furniture on it at all. The regeneration prompts produce these on
purpose, because generated text comes out garbled, so the title, the pins, the
difficulty stars and the info row are laid over the photo afterwards by the
card template layer.

Feeding a hero to the splitter would cut a photograph down the middle and
publish two halves of a room. They are told apart by shape and routed
differently: sheets to review before the deck, heroes to build/heroes to
wait for the template.

REVIEW BEFORE PUBLISH
----------------------
A sheet is not copied straight to the deck folder. It is staged under
build/deck-review/<deck>/ first. ops/review_heroes.py exists because 114
generated zone photos were wired onto live pages before anyone looked at
one; RETRO-2026-08-30.md named this pipeline as carrying the same risk with
no equivalent gate, since size/ratio/flatness/banded-edge checks can tell a
blank render from a photo but cannot tell a correct card from a garbled or
mismatched one. So --apply now does two things every time it runs: stage any
new drops, and promote any staged sheet that ops/review_deck_art.py has
marked "ok" (verdict must match the sha of the staged file, so a re-drop of
a different image at the same name is not published on an old approval).
An unjudged or rejected sheet just stays staged.

HOW A FILE IS MATCHED TO A CARD
-------------------------------
By card code in the filename, which is what the prompts ask for. Failing that,
by an exact match between the words in the filename and the words in a card's
name: "shoe_zone.png" is EM-005 Shoe Zone. Exact, not fuzzy. A near miss is
reported and left alone, because filing a picture against the wrong card puts
the wrong photograph on a product page and nobody would notice for weeks.

Run:  python ops/import_generated_art.py --check
      python ops/import_generated_art.py --apply
"""
from __future__ import annotations

import glob
import hashlib
import io
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESK = os.path.join(os.path.expanduser("~"), "Desktop")
STAGE = os.path.join(ROOT, "build", "deck-review")
VERDICTS = os.path.join(ROOT, "ops", "deck-art-verdicts.json")

# Every folder Phil actually saves into. The second predates this script and
# is the one he used, so watching only the folder this script invented would
# have silently missed five finished images.
DROPS = [
    os.path.join(DESK, "6S-Generated-Images"),
    os.path.join(DESK, "6S-Image-Prompts", "save-images-here"),
]

DECK_DIR = {
    "entryway": os.path.join(DESK, "6S-Success-Card-Decks", "Entryway Deck",
                             "card-images"),
    "mudroom": os.path.join(DESK, "6S-Success-Card-Decks", "Mud Room Deck",
                            "card-images"),
}
DECK_OF = {"E": "entryway", "M": "mudroom"}
HEROES = os.path.join(ROOT, "build", "heroes")

MIN_EDGE = 900
# A card sheet holds two portrait panels side by side, so it lands near 1.5.
# A hero is a single 4:3 frame, so it lands near 1.33. The gap is narrow but
# it is consistent, and the gutter check below confirms the call rather than
# trusting the ratio alone.
SHEET_RATIO = 1.42


def cards_index() -> dict:
    """code -> {deck, name}, from every card list this project holds."""
    out = {}
    for deck, f in (("mudroom", "mudroom-cards.json"),
                    ("entryway", "entryway-cards.json")):
        p = os.path.join(ROOT, "build", f)
        if os.path.exists(p):
            for c in json.load(io.open(p, encoding="utf-8")):
                out[c["ID"]] = {"deck": deck, "name": c.get("Card", "")}
    for deck, d in DECK_DIR.items():
        for f in glob.glob(os.path.join(d, "*")):
            m = re.match(r"([A-Z]{2}-\d{3})", os.path.basename(f))
            if m:
                out.setdefault(m.group(1), {"deck": deck, "name": ""})
    return out


def words(s: str) -> frozenset:
    return frozenset(w for w in re.split(r"[^a-z0-9]+", s.lower()) if w)


STOP = {"entryway", "mudroom", "png", "jpg", "jpeg", "webp", "card", "hero",
        "final", "v1", "v2", "copy"}


def resolve(base: str, cards: dict) -> tuple:
    """(code, how) or (None, why not)."""
    m = re.match(r"([A-Z]{2}-\d{3})", base)
    if m:
        return (m.group(1), "card code in the filename") if m.group(1) in cards \
            else (None, f"{m.group(1)} is not a card in any known deck")

    w = words(os.path.splitext(base)[0]) - STOP
    if not w:
        return None, "no card code and no usable words in the filename"

    hits = [c for c, v in cards.items()
            if v.get("name") and (words(v["name"]) - STOP) == w]
    if len(hits) == 1:
        return hits[0], f"name matches {cards[hits[0]]['name']!r}"
    if len(hits) > 1:
        return None, f"the name matches {len(hits)} cards: {sorted(hits)}"
    return None, ("no card code, and the words in the filename match no card "
                  "name exactly")


def classify(path: str) -> tuple:
    """(kind, why) where kind is 'hero', 'sheet' or None."""
    try:
        from PIL import Image
        import numpy as np
        im = Image.open(path)
        im.load()
    except Exception as e:                                    # noqa: BLE001
        return None, f"will not open as an image ({type(e).__name__})"

    w, h = im.size
    if min(w, h) < MIN_EDGE:
        return None, f"{w}x{h}, under the {MIN_EDGE}px minimum"
    if w < h:
        return None, (f"{w}x{h} is portrait. Both a hero and a card sheet are "
                      f"landscape, so this is something else")

    a = np.asarray(im.convert("L"), dtype=np.float32)
    if a.std() < 12:
        return None, (f"standard deviation {a.std():.1f}, a nearly flat image "
                      f"is a failed generation rather than a photograph")

    ratio = w / h
    if ratio >= SHEET_RATIO:
        # Confirm with the gutter a two panel sheet always has: a run of
        # near white columns down the middle. Without it, a wide photograph
        # would be cut in half and published as two halves of a room.
        col = a.mean(axis=0)
        mid = col[int(w * 0.44):int(w * 0.56)]
        if (mid > 245).sum() >= 6:
            return "sheet", ""
        return "hero", ""
    return "hero", ""


def hero_checks(path: str) -> tuple:
    from PIL import Image
    import numpy as np
    a = np.asarray(Image.open(path).convert("L"), dtype=np.float32)
    h = a.shape[0]
    rows = a.mean(axis=1)
    band = max(int(h * 0.10), 1)
    for name, strip in (("top", rows[:band]), ("bottom", rows[-band:])):
        if (strip.mean() < 42 or strip.mean() > 232) and \
                abs(strip.mean() - rows.mean()) > 70:
            return False, (f"a uniform {'dark' if strip.mean() < 128 else 'light'} "
                           f"band across the {name}, the shape a baked in "
                           f"title bar makes. Look at it before accepting")
    return True, ""


def staged_sha(path: str) -> str:
    return hashlib.sha256(io.open(path, "rb").read()).hexdigest()[:10]


def approved_staged() -> dict:
    """deck/filename -> verdict, but only for the file staged right now.

    Same rule as the zone-hero gate: the sha is checked, not just the
    verdict, so re-staging a different image under a name that was already
    approved does not publish something nobody has looked at.
    """
    if not os.path.exists(VERDICTS):
        return {}
    raw = json.load(io.open(VERDICTS, encoding="utf-8"))
    out = {}
    for rel, rec in raw.items():
        p = os.path.join(STAGE, rel)
        if not isinstance(rec, dict) or not os.path.exists(p):
            continue
        if rec.get("sha") == staged_sha(p):
            out[rel] = rec["verdict"]
    return out


def promote() -> None:
    """Publish every staged sheet somebody has already marked "ok".

    Runs on every --apply regardless of whether anything new was found in
    DROPS this time, because a sheet staged and approved in a prior run must
    still reach the deck the next time this is run, not only the run that
    happened to also see a new file. A sheet nobody has judged, or one
    rejected, is left staged: unjudged and rejected are indistinguishable at
    the moment of publishing, the same rule as the zone-hero gate.
    """
    approved = approved_staged()
    touched, promoted = set(), 0
    for rel, verdict in approved.items():
        if verdict != "ok":
            continue
        deck, base = rel.split("/", 1)
        if deck not in DECK_DIR:
            continue
        shutil.copy2(os.path.join(STAGE, rel), os.path.join(DECK_DIR[deck], base))
        touched.add(deck)
        promoted += 1

    staged_total = sum(len(glob.glob(os.path.join(STAGE, d, "*")))
                       for d in DECK_DIR if os.path.isdir(os.path.join(STAGE, d)))
    awaiting = staged_total - promoted
    print(f"  {promoted} approved card(s) promoted to the deck")
    if awaiting:
        print(f"  {awaiting} staged card(s) still awaiting review: run "
              f"ops/review_deck_art.py --sheets")

    if touched:
        sys.path.insert(0, os.path.join(ROOT, "ops"))
        import split_deck_cards
        import build_deck_gallery
        for d in sorted(touched):
            split_deck_cards.main(True, d)
        build_deck_gallery.main()
        os.system(f'"{sys.executable}" '
                  f'"{os.path.join(ROOT, "ops", "fingerprint_assets.py")}" '
                  f'>nul 2>&1')
        print("  galleries rebuilt and assets re-fingerprinted")


def main(apply_it: bool) -> int:
    cards = cards_index()
    found = []
    for d in DROPS:
        if os.path.isdir(d):
            found += [f for f in glob.glob(os.path.join(d, "*"))
                      if os.path.isfile(f)
                      and f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]

    for d in DROPS:
        print(f"  watching  {d}"
              + ("" if os.path.isdir(d) else "   (does not exist)"))
    print(f"  cards known {len(cards)}   files found {len(found)}\n")
    if not found:
        print("  nothing new to import")
        if apply_it:
            promote()
        return 0

    heroes, sheets, skip = [], [], []
    for f in sorted(found):
        base = os.path.basename(f)
        code, how = resolve(base, cards)
        if not code:
            skip.append((base, how))
            continue
        kind, why = classify(f)
        if not kind:
            skip.append((base, why))
            continue
        if kind == "hero":
            ok, why2 = hero_checks(f)
            if not ok:
                skip.append((base, why2))
                continue
        deck = cards[code].get("deck") or DECK_OF.get(code[0])
        (heroes if kind == "hero" else sheets).append((f, code, deck, how))

    for base, why in skip:
        print(f"    skip   {base[:36]:38} {why}")
    for f, code, deck, how in heroes:
        print(f"    HERO   {os.path.basename(f)[:36]:38} {code}  {deck}   ({how})")
    for f, code, deck, how in sheets:
        print(f"    SHEET  {os.path.basename(f)[:36]:38} {code}  {deck}   ({how})")

    if not apply_it:
        print(f"\n  would take {len(heroes)} heroes and {len(sheets)} card "
              f"sheets, skip {len(skip)}. --check only, nothing moved.")
        return 0

    for f, code, deck, _ in heroes:
        out = os.path.join(HEROES, deck)
        os.makedirs(out, exist_ok=True)
        name = cards[code].get("name") or ""
        stem = f"{code}" + (f"-{re.sub(r'[^A-Za-z0-9]+', '-', name).strip('-')}"
                            if name else "")
        shutil.copy2(f, os.path.join(out, stem + os.path.splitext(f)[1].lower()))

    for f, code, deck, _ in sheets:
        out = os.path.join(STAGE, deck)
        os.makedirs(out, exist_ok=True)
        shutil.copy2(f, os.path.join(out, os.path.basename(f)))

    print(f"\n  {len(heroes)} hero photographs -> build/heroes/")
    print(f"  {len(sheets)} card sheets staged for review -> build/deck-review/")
    promote()

    if heroes:
        print(f"\n  The heroes are photographs, not finished cards. They are "
              f"held in\n  build/heroes/ until the card template layer lays "
              f"the title, the\n  callout pins, the stars and the info row "
              f"over them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--apply" in sys.argv))
