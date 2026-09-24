#!/usr/bin/env python3
"""
Keep STRATEGY-MICROZONES.md's coverage numbers measured, not remembered.

WHY THIS EXISTS
---------------
That document's whole argument rests on one gap: the execution fields exist
for all 114 micro zones, while the three fields that differentiate the product
(capacity, variants, diagnosis) exist for far fewer. The gap is the strategy,
so the number IS the argument.

It was written by hand as "12 of 114, 10.5%". One room of authoring later it
was wrong, and it will be wrong again after each of the sixteen rooms still to
do. CLAUDE.md is explicit that a stale baseline in an operating document is a
defect in that document, and a strategy doc that overstates its own weakness
is the specific kind of wrong that gets acted on.

So the table and the headline percentage are regenerated from
content/manual/source/content.json between markers, and the prose around them
is left alone. Run it after authoring a room:

    python ops/build_microzone_coverage.py
"""
from __future__ import annotations

import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, "content", "manual", "source", "content.json")
DOC = os.path.join(ROOT, "STRATEGY-MICROZONES.md")

BEGIN = "<!-- COVERAGE:BEGIN -->"
END = "<!-- COVERAGE:END -->"

MOAT = ("capacity", "variants", "diagnosis")

BASE_FIELDS = ("passes", "shine_detail", "watch_for", "leave_behind",
               "the_call")


def _base_sub(field, value):
    """Sub-item count, per field, because the shapes genuinely differ.

    shine_detail is a DICT (a summary plus a surfaces list), not a list. A
    generic len() over it returns 4, the number of keys, and the first run of
    this generator duly published "456 surfaces" over a document that had
    correctly said 749 by hand. Understating your own asset in the strategy
    document that argues from the size of that asset is a bad trade for one
    saved branch, so the shapes are named here rather than assumed.
    """
    if field == "shine_detail":
        return len((value or {}).get("surfaces") or [])
    return len(value or [])


def _sub(field: str, value) -> int:
    if field == "diagnosis":
        return len((value or {}).get("frictions") or [])
    return len(value or [])


def measure() -> dict:
    d = json.load(io.open(CORPUS, encoding="utf-8"))
    zones = [(r.get("room"), z) for r in d["rooms"] for z in r.get("zones") or []]
    total = len(zones)

    have = {f: 0 for f in MOAT}
    sub = {f: 0 for f in MOAT}
    for _room, z in zones:
        for f in MOAT:
            if z.get(f):
                have[f] += 1
                sub[f] += _sub(f, z[f])

    base = {}
    for _room, z in zones:
        for f in BASE_FIELDS:
            if z.get(f):
                base.setdefault(f, [0, 0])
                base[f][0] += 1
                base[f][1] += _base_sub(f, z[f])

    # The headline percentage below is "zones with the full moat", not "zones
    # with any one moat field": today those two counts happen to be equal
    # (every zone that has been authored gets all three fields in the same
    # pass), but nothing enforces that, and have["diagnosis"] alone would
    # silently overstate coverage the day a zone gets diagnosis authored
    # ahead of capacity/variants. Counted directly here, the same all()
    # check rooms_done/rooms_open already use, so the two can never disagree.
    moat_complete = sum(1 for _room, z in zones if all(z.get(f) for f in MOAT))

    rooms_done, rooms_open = [], []
    for r in d["rooms"]:
        zs = r.get("zones") or []
        if not zs:
            continue
        n = sum(1 for z in zs if all(z.get(f) for f in MOAT))
        (rooms_done if n == len(zs) else rooms_open).append(
            (r.get("room"), n, len(zs)))

    return {"total": total, "have": have, "sub": sub, "base": base,
            "moat_complete": moat_complete,
            "rooms_done": rooms_done, "rooms_open": rooms_open}


def render(m: dict) -> str:
    t = m["total"]
    lab = {
        "passes": "the six S steps, per zone",
        "shine_detail": "a cleaning method per surface, with product and order",
        "watch_for": "what goes wrong here",
        "leave_behind": "the standard that stays, and its trigger",
        "the_call": "the judgement call this zone forces",
    }
    rows = ["| Field | Zones with it | Sub-items | What it is |",
            "|---|---|---|---|",
            "| purpose, done_looks_like, session, time_note | %d | - | "
            "what this place is for and when it is finished |" % t]
    for f in BASE_FIELDS:
        n, s = m["base"].get(f, (0, 0))
        rows.append("| %s | %d | **%d** | %s |" % (f, n, s, lab[f]))
    moat_lab = {
        "diagnosis": "symptom to branching question to root cause",
        "capacity": 'how much actually fits, and the test for "it does not"',
        "variants": "what to do when your home is not the assumed one",
    }
    for f in ("diagnosis", "capacity", "variants"):
        rows.append("| **%s** | **%d** | %d | %s |"
                    % (f, m["have"][f], m["sub"][f], moat_lab[f]))

    done = m["rooms_done"]
    n_done = m["moat_complete"]
    pct = 100.0 * n_done / t if t else 0.0

    lines = [BEGIN, ""]
    lines += rows
    lines.append("")
    lines.append(
        "**That split is the whole strategy.** The top block is complete and is already sold: the Print Pack ($19) "
        "carries the %d passes, the Micro Zone Manual ($29) carries the "
        "clean-and-shine steps. The bottom block is the differentiator and it "
        "exists for **%d of %d zones, %.1f%%**, across %d fully personalised "
        "%s: %s."
        % (m["base"].get("passes", (0, 0))[1], n_done, t, pct, len(done),
           "room" if len(done) == 1 else "rooms",
           ", ".join("%s (%d)" % (r, k) for r, _n, k in done) or "none"))
    partial = [x for x in m["rooms_open"] if x[1]]
    if partial:
        lines.append("")
        lines.append(
            "Part-authored, and therefore not shippable as a Room Plan: %s."
            % ", ".join("%s (%d of %d)" % (r, n, k) for r, n, k in partial))
    lines.append("")
    lines.append("<sub>Measured from `content/manual/source/content.json` by "
                 "`ops/build_microzone_coverage.py`. Do not hand-edit.</sub>")
    lines.append("")
    lines.append(END)
    return "\n".join(lines)


def main() -> int:
    m = measure()
    src = io.open(DOC, encoding="utf-8", newline="").read()
    crlf = "\r\n" in src
    flat = src.replace("\r\n", "\n")
    if BEGIN not in flat or END not in flat:
        print("  %s carries no COVERAGE markers; refusing to guess where the "
              "table goes. Add %s / %s around it."
              % (os.path.basename(DOC), BEGIN, END))
        return 1
    head, rest = flat.split(BEGIN, 1)
    _old, tail = rest.split(END, 1)
    out = head + render(m) + tail
    if crlf:
        out = out.replace("\n", "\r\n")
    io.open(DOC, "w", encoding="utf-8", newline="").write(out)
    print("  %s: %d of %d zones carry all three moat fields (%.1f%%), %d "
          "rooms complete"
          % (os.path.basename(DOC), m["moat_complete"], m["total"],
             100.0 * m["moat_complete"] / m["total"],
             len(m["rooms_done"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
