#!/usr/bin/env python3
"""
Look at every generated image before any of them reaches a page.

WHY THIS EXISTS
---------------
The first batch of 114 zone heroes was wired onto all 114 zone pages without
anybody looking at them. A spot check of two found the garage hand tool wall
rendered as a room of sawhorses and the board game zone as a stack of moving
boxes. A full review of the first 24 put the pass rate near half.

Every one of those was about to be published under the caption "an
illustration of the finished state". That caption is a claim about the
picture, and for those images it was false. Fabricating evidence by
carelessness is still fabricating evidence, so the fix is not a better prompt
alone: it is that no image ships unless a person or a model with eyes has
looked at it and said so.

HOW IT WORKS
------------
  --sheets   builds numbered contact sheets, twelve images to a page, so 114
             images can be judged in ten looks instead of 114.
  --mark     records verdicts: --mark ok 1-6,9 or --mark no 7,8
  --status   what is approved, what is rejected, what nobody has judged.

ops/wire_zone_heroes.py wires only stems marked ok. Unjudged is treated as
rejected, because at the moment of wiring the two are indistinguishable.

Run:  python ops/review_heroes.py --sheets
      python ops/review_heroes.py --mark ok 1-6,9,11
      python ops/review_heroes.py --status
"""
from __future__ import annotations

import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEROES = os.path.join(ROOT, "build", "heroes", "zones")
REVIEW = os.path.join(ROOT, "build", "heroes", "review")
INDEX = os.path.join(REVIEW, "index.json")
VERDICTS = os.path.join(ROOT, "ops", "hero-verdicts.json")

COLS, ROWS, W = 4, 3, 320


def stems() -> list:
    return [os.path.basename(p)[:-4]
            for p in sorted(glob.glob(os.path.join(HEROES, "*.png")))]


def load(path: str) -> dict:
    return json.load(io.open(path, encoding="utf-8")) if os.path.exists(path) else {}


def save(path: str, d: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(d, io.open(path, "w", encoding="utf-8", newline=""), indent=1,
              sort_keys=True)


def sheets() -> int:
    from PIL import Image, ImageDraw
    os.makedirs(REVIEW, exist_ok=True)
    for old in glob.glob(os.path.join(REVIEW, "sheet-*.png")):
        os.remove(old)
    names, h, per, idx, n_sheets = stems(), round(W * 3 / 4), COLS * ROWS, {}, 0
    for s in range(0, len(names), per):
        chunk = names[s:s + per]
        sheet = Image.new("RGB", (COLS * W, ROWS * (h + 22)), "white")
        d = ImageDraw.Draw(sheet)
        for i, stem in enumerate(chunk):
            im = Image.open(os.path.join(HEROES, stem + ".png")).convert("RGB")
            x, y = (i % COLS) * W, (i // COLS) * (h + 22)
            sheet.paste(im.resize((W, h), Image.LANCZOS), (x, y))
            idx[str(s + i + 1)] = stem
            d.text((x + 4, y + h + 5), f"{s + i + 1}", fill="black")
        n_sheets += 1
        sheet.save(os.path.join(REVIEW, f"sheet-{n_sheets:02d}.png"))
    save(INDEX, idx)
    print(f"  {len(names)} images, {n_sheets} sheets in build/heroes/review")
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
        stem = idx.get(str(n))
        if not stem:
            print(f"  {n} is not in the index, skipped")
            continue
        v[stem] = verdict
        hit += 1
    save(VERDICTS, v)
    print(f"  marked {hit} as {verdict}")
    return status()


def status() -> int:
    v, names = load(VERDICTS), stems()
    ok = [s for s in names if v.get(s) == "ok"]
    no = [s for s in names if v.get(s) not in (None, "ok")]
    un = [s for s in names if s not in v]
    print(f"  images      {len(names)}")
    print(f"  approved    {len(ok)}")
    print(f"  rejected    {len(no)}")
    print(f"  unjudged    {len(un)}   (treated as rejected until looked at)")
    if names:
        print(f"  pass rate   {100 * len(ok) // max(len(names), 1)}%")
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
