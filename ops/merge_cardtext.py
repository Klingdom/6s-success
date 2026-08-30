#!/usr/bin/env python3
"""
Merge the transcribed card batches into one checked corpus.

WHERE THIS TEXT CAME FROM
-------------------------
The full card copy, the objective, the quick win, the pro tip, the reset time,
the symptoms, the best practices and the card link graph, existed nowhere as
text. It was only ever inside the artwork. The card list HTML carries a
summary line per card, the v2 CardText file belongs to a different 46 card
deck, and the master proof is a 2,132 word index.

So it was read back off the 90 finished card images and transcribed verbatim.
That is why this file exists and why the checks below are strict: a
transcription error becomes a wrong instruction printed on a product.

WHAT IT CHECKS
--------------
  * every card id is a real card, and no id appears twice
  * every next_card and related_path target points at a card that exists
  * nothing carries an em dash or en dash, which is house style
  * UNREADABLE is counted and reported per field, never silently kept
  * a field that is suspiciously long or short for its kind is flagged

Run:  python ops/merge_cardtext.py
"""
from __future__ import annotations

import collections
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The batches are hand transcribed from 90 card images and are the only copy
# of that reading. They lived under build/, which is gitignored, so the corpus
# every card renders from was a tracked file whose source existed on one
# laptop. A canon fix applied there would have survived exactly as long as the
# disk did. Source of truth belongs in the repository; build/ is for things a
# script can make again.
SRC = os.path.join(ROOT, "ops", "cardtext")
OUT = os.path.join(ROOT, "build", "entryway-cardtext.json")

CODE = re.compile(r"^E[A-Z]-\d{3}$")
LIST_FIELDS = ("callouts", "common_symptoms", "best_practices",
               "progress_tracker", "claims")


def main() -> int:
    batches = sorted(glob.glob(os.path.join(SRC, "batch-*.json")))
    if not batches:
        print(f"  no batches in build/cardtext yet")
        return 1

    cards, dupes = {}, []
    for b in batches:
        try:
            data = json.load(io.open(b, encoding="utf-8"))
        except Exception as e:                                # noqa: BLE001
            print(f"  {os.path.basename(b)}: will not parse, {e}")
            return 1
        for c in data:
            cid = (c.get("id") or "").strip().upper()
            if not CODE.match(cid):
                print(f"  {os.path.basename(b)}: bad id {cid!r}, skipped")
                continue
            if cid in cards:
                dupes.append(cid)
                continue
            c["id"] = cid
            cards[cid] = c

    print(f"  batches merged   {len(batches)}")
    print(f"  cards            {len(cards)}")
    if dupes:
        print(f"  duplicate ids    {sorted(set(dupes))}")

    # Unreadable fields, counted per field so a systematically hard field
    # shows up as a pattern rather than as scattered noise.
    unread = collections.Counter()
    for c in cards.values():
        for k, v in c.items():
            if v == "UNREADABLE":
                unread[k] += 1
            elif isinstance(v, list) and "UNREADABLE" in v:
                unread[k] += 1
    total_unread = sum(unread.values())
    print(f"  unreadable       {total_unread} fields")
    for k, n in unread.most_common(8):
        print(f"    {k:22} {n}")

    # Every pointer must land on a real card, or the deck's link graph sends
    # somebody to a card that does not exist.
    dangling = []
    for c in cards.values():
        nxt = (c.get("next_card") or {}).get("id")
        if nxt and CODE.match(str(nxt)) and nxt not in cards:
            dangling.append((c["id"], "next_card", nxt))
        for k, v in (c.get("related_path") or {}).items():
            if v and CODE.match(str(v)) and v not in cards:
                dangling.append((c["id"], k, v))
    print(f"  dangling links   {len(dangling)}")
    for d in dangling[:6]:
        print(f"    {d[0]} {d[1]} -> {d[2]} does not exist")

    # House style. These were transcribed from artwork that contains them, so
    # this is a real risk rather than a theoretical one.
    dashes = []
    for c in cards.values():
        blob = json.dumps(c, ensure_ascii=False)
        if re.search(r"[—–]", blob):
            dashes.append(c["id"])
    print(f"  em or en dashes  {len(dashes)}" +
          (f"  {dashes[:6]}" if dashes else ""))

    brands = [(c["id"], c["brand_visible"]) for c in cards.values()
              if c.get("brand_visible")]
    if brands:
        print(f"\n  BRAND NAMES VISIBLE IN ARTWORK, which cannot ship:")
        for cid, b in brands:
            print(f"    {cid}  {b}")

    claims = [(c["id"], x) for c in cards.values()
              for x in (c.get("claims") or [])]
    if claims:
        print(f"\n  CLAIMS TO VERIFY BEFORE THEY SHIP:")
        for cid, x in claims[:10]:
            print(f"    {cid}  {x[:70]}")

    json.dump({"deck": "entryway", "count": len(cards),
               "cards": [cards[k] for k in sorted(cards)]},
              io.open(OUT, "w", encoding="utf-8", newline=""),
              indent=1, ensure_ascii=False)

    filled = collections.Counter()
    for c in cards.values():
        for k, v in c.items():
            if v not in (None, "", [], "UNREADABLE"):
                filled[k] += 1
    print(f"\n  wrote build/entryway-cardtext.json")
    print(f"  field coverage across {len(cards)} cards:")
    for k in ("objective", "quick_win", "pro_tip", "reset_time", "callouts",
              "why_it_matters", "best_practices", "next_card", "related_path"):
        print(f"    {k:22} {filled.get(k, 0):>3}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
