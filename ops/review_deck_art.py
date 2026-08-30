#!/usr/bin/env python3
"""
Look at every staged card sheet before it reaches the deck gallery.

WHY THIS EXISTS
---------------
ops/review_heroes.py exists because 114 generated zone photographs were wired
onto 114 live pages before anybody looked at one, and a spot check found a
garage tool wall rendered as sawhorses. That cycle's own retrospective
(RETRO-2026-08-30.md) named the next place the same failure was still
possible: "The card decks... run through generators with no equivalent gate."

ops/import_generated_art.py used to copy a finished card sheet straight into
the deck source folder and rebuild the gallery in the same run, checked only
by size, aspect ratio, flatness and a banded-edge proxy for baked-in text.
None of those can tell a correct card from a garbled or mismatched one, the
same gap the zone-hero verify() step had. This script is the human check that
sits between "the file looks like a card" and "the file is on the site."

HOW IT WORKS
------------
ops/import_generated_art.py --apply now stages sheets under
build/deck-review/<deck>/ instead of publishing them, and only promotes a
staged file to the real deck folder once it is marked "ok" here.

  --sheets   contact sheets of every staged, unjudged card, twelve to a page.
  --mark     records verdicts: --mark ok 1-6,9 or --mark no 7,8
  --status   staged, approved, rejected, unjudged.

Run:  python ops/review_deck_art.py --sheets
      python ops/review_deck_art.py --mark ok 1-6,9,11
      python ops/review_deck_art.py --status
Then: python ops/import_generated_art.py --apply    (promotes approved ones)
"""
from __future__ import annotations

import glob
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGE = os.path.join(ROOT, "build", "deck-review")
CONTACT = os.path.join(STAGE, "_contact")
INDEX = os.path.join(CONTACT, "index.json")
# Tracked in the repo, not under build/, which is gitignored. A verdict is a
# judgement somebody made by looking at a picture, not something a rebuild
# can reproduce, and losing it would silently drop back to "not reviewed."
VERDICTS = os.path.join(ROOT, "ops", "deck-art-verdicts.json")

COLS, ROWS, W = 4, 3, 320
# A card sheet is two portrait panels side by side with a white gutter, wider
# than it is tall but not by as much as it looks at first glance; this is
# import_generated_art.py's own SHEET_RATIO, kept in sync by hand since the
# two scripts serve different moments (import vs. review) and neither should
# import the other just to share one constant.
SHEET_RATIO = 1.42


def sha(rel: str) -> str:
    """Identity of the actual pixels, so a verdict cannot outlive its image."""
    return hashlib.sha256(io.open(os.path.join(STAGE, rel), "rb")
                           .read()).hexdigest()[:10]


def stems() -> list:
    """deck/filename for every staged sheet, sorted, contact dir excluded."""
    out = []
    for deck in sorted(os.listdir(STAGE)) if os.path.isdir(STAGE) else []:
        d = os.path.join(STAGE, deck)
        if deck.startswith("_") or not os.path.isdir(d):
            continue
        for f in sorted(glob.glob(os.path.join(d, "*"))):
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                out.append(f"{deck}/{os.path.basename(f)}")
    return out


def load(path: str) -> dict:
    return json.load(io.open(path, encoding="utf-8")) if os.path.exists(path) else {}


def save(path: str, d: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(d, io.open(path, "w", encoding="utf-8", newline=""), indent=1,
              sort_keys=True)


def verdict_of(rel: str, v: dict) -> str:
    """The recorded verdict, but only if it is about the image staged now."""
    rec = v.get(rel)
    if not isinstance(rec, dict):
        return ""
    return rec["verdict"] if rec.get("sha") == sha(rel) else ""


def sheets() -> int:
    from PIL import Image, ImageDraw
    os.makedirs(CONTACT, exist_ok=True)
    for old in glob.glob(os.path.join(CONTACT, "sheet-*.png")):
        os.remove(old)
    names = stems()
    if "--unjudged" in sys.argv:
        v = load(VERDICTS)
        names = [n for n in names if not verdict_of(n, v)]
        print(f"  {len(names)} unjudged, sheets cover only those")
    h, per, idx, n_sheets = round(W / SHEET_RATIO), COLS * ROWS, {}, 0
    for s in range(0, len(names), per):
        chunk = names[s:s + per]
        sheet = Image.new("RGB", (COLS * W, ROWS * (h + 22)), "white")
        d = ImageDraw.Draw(sheet)
        for i, rel in enumerate(chunk):
            im = Image.open(os.path.join(STAGE, rel)).convert("RGB")
            x, y = (i % COLS) * W, (i // COLS) * (h + 22)
            sheet.paste(im.resize((W, h), Image.LANCZOS), (x, y))
            idx[str(s + i + 1)] = rel
            d.text((x + 4, y + h + 5), f"{s + i + 1} {rel}", fill="black")
        n_sheets += 1
        sheet.save(os.path.join(CONTACT, f"sheet-{n_sheets:02d}.png"))
    save(INDEX, idx)
    print(f"  {len(names)} staged cards, {n_sheets} sheets in "
          f"build/deck-review/_contact")
    return 0


def expand(spec: str) -> list:
    out = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            out.extend(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    return out


def mark(verdict: str, spec: str) -> int:
    idx, v = load(INDEX), load(VERDICTS)
    if not idx:
        print("  no index. Run --sheets first.")
        return 1
    hit = 0
    for n in expand(spec):
        rel = idx.get(str(n))
        if not rel:
            print(f"  {n} is not in the index, skipped")
            continue
        v[rel] = {"verdict": verdict, "sha": sha(rel)}
        hit += 1
    save(VERDICTS, v)
    print(f"  marked {hit} as {verdict}")
    return status()


def status() -> int:
    v, names = load(VERDICTS), stems()
    ok = [s for s in names if verdict_of(s, v) == "ok"]
    no = [s for s in names if verdict_of(s, v) not in ("", "ok")]
    un = [s for s in names if not verdict_of(s, v)]
    print(f"  staged      {len(names)}")
    print(f"  approved    {len(ok)}")
    print(f"  rejected    {len(no)}")
    print(f"  unjudged    {len(un)}   (treated as rejected until looked at)")
    if names:
        print(f"  pass rate   {100 * len(ok) // max(len(names), 1)}%")
    print("\n  run ops/import_generated_art.py --apply to promote approved "
          "cards to the deck")
    return 0


def main() -> int:
    if "--sheets" in sys.argv:
        return sheets()
    if "--mark" in sys.argv:
        i = sys.argv.index("--mark")
        return mark(sys.argv[i + 1], sys.argv[i + 2])
    return status()


if __name__ == "__main__":
    raise SystemExit(main())
