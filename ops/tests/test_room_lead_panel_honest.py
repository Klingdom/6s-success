#!/usr/bin/env python3
"""
Prove the room lead panel tells the truth about itself, and does not repeat
the lede it sits beside.

WHY THIS EXISTS
---------------
11 of 20 rooms have no chapter illustration (owner-gated on image generation)
and carry a typographic panel instead. That panel was built by reusing
panel_figure(), which exists for ZONE heroes, and it was handed the room's
intro. Three things followed, found 2026-09-30:

  - The eyebrow read "WHAT DONE LOOKS LIKE" and the accessible name said
    "what done looks like, in words", while the text shown was the room's
    PROBLEM. "The garage takes what every other room in the house evicts" is
    the opposite of done. A label that contradicts its own content is worse
    than no label, and a screen reader got the contradiction verbatim.
  - The room intro is ALSO the page lede, immediately beside the panel, so
    those pages opened by saying the same two sentences twice.
  - With zone empty, the accessible name was "Garage / : what done looks
    like, in words", a dangling separator announced on 11 pages.

The panel now carries the room's first tip, which is the room's own words, is
not the lede, and answers what CLAUDE.md section 0.7 P2 calls "what to do
first". Rooms with no tips fall back to the intro under a truthful label.

A note on verifying this: the first check written for it grepped whole pages
for "what done looks like" and reported all 11 still broken. They were fixed;
the phrase legitimately appears in every room page's meta description ("with
what done looks like for each"). So these cases read the PANEL, not the page.

Run:  python ops/tests/test_room_lead_panel_honest.py
"""
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import wire_zone_heroes as W                                   # noqa: E402

PANEL = "room-lead-panel"


def _panels():
    """(room, panel html) for every room page carrying a lead panel."""
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "site", "rooms", "*.html"))):
        name = os.path.basename(f)[:-len(".html")]
        if name == "index":
            continue
        h = io.open(f, encoding="utf-8", errors="replace").read()
        i = h.find(PANEL)
        if i < 0:
            continue
        out.append((name, h[i:i + 2000], h))
    return out


def case_some_rooms_actually_carry_a_panel():
    """A test that passes because it found nothing would be worthless."""
    assert len(_panels()) >= 5, len(_panels())


def case_no_panel_claims_to_show_what_done_looks_like():
    for name, panel, _ in _panels():
        m = re.search(r'aria-label="([^"]*)"', panel)
        assert m, name
        assert "what done looks like" not in m.group(1).lower(), (name, m.group(1))


def case_no_panel_has_a_dangling_separator_in_its_name():
    for name, panel, _ in _panels():
        m = re.search(r'aria-label="([^"]*)"', panel)
        assert " / :" not in m.group(1), (name, m.group(1))


def case_the_eyebrow_matches_the_accessible_name():
    for name, panel, _ in _panels():
        eye = re.search(r'class="l">([^<]*)<', panel)
        aria = re.search(r'aria-label="([^"]*)"', panel)
        assert eye and aria, name
        first = eye.group(1).split(",")[0].strip().lower()
        assert first in aria.group(1).lower(), (name, eye.group(1), aria.group(1))


def case_the_panel_does_not_repeat_the_page_lede():
    """The defect: intro as prose AND as type, one above the other."""
    for name, panel, page in _panels():
        lede = re.search(r'<p class="lede">(.*?)</p>', page, re.S)
        if not lede:
            continue
        words = re.sub(r"<[^>]+>", " ", lede.group(1))
        words = re.sub(r"\s+", " ", words).strip()
        # A distinctive run from the lede must not also be inside the panel.
        probe = " ".join(words.split()[:7])
        if len(probe) < 20:
            continue
        flat = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", panel))
        assert probe.lower() not in flat.lower(), (name, probe)


def case_the_panel_quotes_the_rooms_own_words():
    """Nothing invented: the text must come from the corpus."""
    corpus = json.loads(io.open(
        os.path.join(ROOT, "content", "manual", "source", "content.json"),
        encoding="utf-8").read())
    by_slug = {}
    for r in corpus["rooms"]:
        slug = re.sub(r"[^a-z0-9]+", "-", r["room"].lower()).strip("-")
        by_slug[slug] = r
    checked = 0
    for name, panel, _ in _panels():
        room = by_slug.get(name)
        if not room:
            continue
        flat = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", panel))
        tips = room.get("tips") or []
        source = (tips[0].get("text") if tips and isinstance(tips[0], dict)
                  else None) or room.get("intro") or ""
        probe = " ".join(re.sub(r"\s+", " ", source).split()[:6])
        if len(probe) < 20:
            continue
        assert probe.lower() in flat.lower(), (name, probe)
        checked += 1
    assert checked >= 5, checked


def case_the_zone_panel_still_says_what_done_looks_like():
    """The default must not have been changed for zones, where it is true."""
    svg = W.panel_figure("Kitchen", "The Cooking Zone", "Burners wiped.")
    assert "WHAT DONE LOOKS LIKE" in svg
    assert 'Kitchen / The Cooking Zone: what done looks like' in svg


def case_an_empty_zone_drops_the_separator():
    svg = W.panel_figure("Garage", "", "Start at the bench.",
                         label="WHERE TO START", aria="where to start")
    m = re.search(r'aria-label="([^"]*)"', svg)
    assert m.group(1) == "Garage: where to start.", m.group(1)


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
