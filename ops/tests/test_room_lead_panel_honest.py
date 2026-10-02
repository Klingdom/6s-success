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


def case_no_room_page_carries_a_panel_any_more():
    """The panels this file was written about are gone, and that is the win.

    Updated 2026-10-01. This case used to assert that at least five rooms
    carried a lead panel, which was true of eleven of them and was the whole
    reason the file exists. It is now true of none: every one of those eleven
    leads on the book's own hand-drawn zone map instead
    (ops/import_room_diagrams.py), because rendering garage.html and reading it
    showed the panel's text was the same paragraph as the "Start here." callout
    further down the same page, and the lede said it a third time.

    The assertion is inverted rather than deleted, so this file records what
    happened instead of quietly passing on an empty set. The honesty rules the
    other cases check are still live, because the three ZONE panels still use
    panel_figure(), and case_the_zone_panel_still_says_what_done_looks_like
    exercises the function directly.
    """
    panels = _panels()
    assert not panels, (
        "%d room page(s) are back on the typographic panel: %s. If that is "
        "deliberate, say why here; if it is a regression, the diagram manifest "
        "ops/room-diagrams.json is probably missing or unreadable."
        % (len(panels), [n for n, _, _ in panels]))


def case_every_room_leads_on_real_artwork():
    """And what replaced the panels has to be honest about what it is."""
    import glob as _glob
    rooms = [f for f in _glob.glob(os.path.join(ROOT, "site", "rooms", "*.html"))
             if not f.endswith("index.html")]
    assert len(rooms) >= 20, len(rooms)
    diagrams = 0
    for fp in rooms:
        h = io.open(fp, encoding="utf-8", errors="replace").read()
        assert 'class="room-lead' in h, "no lead figure at all: %s" % fp
        if "room-lead-diagram" in h:
            diagrams += 1
            # It is a drawing. The site's standard (ops/wire_zone_heroes.py)
            # is that a figure must never let a reader assume a photograph of
            # a real home exists when it does not.
            assert "not a photograph of a real home" in h.lower(), fp
    assert diagrams >= 10, diagrams


# The cases below iterate whatever room panels exist. That is an empty set
# today, by design, so each one is a guard against the panel coming back in a
# dishonest shape rather than a check that runs every time. The live coverage
# for panel_figure() itself is case_the_zone_panel_still_says_what_done_looks
# _like and case_an_empty_zone_drops_the_separator, which call it directly,
# plus ops/tests/test_zone_hero_panel.py against the three real zone panels.


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


def case_the_lead_quotes_the_books_own_words():
    """Nothing invented: the text under the lead must come from the source.

    Was case_the_panel_quotes_the_rooms_own_words, which checked the panel
    text against content.json. The panels are gone, so that case had become
    vacuous (it asserted it had checked at least five rooms and was checking
    none). Repointed at what carries the claim now: the diagram caption, which
    must be the book chapter's own figcaption and not something written here
    to fill the slot.
    """
    manifest_path = os.path.join(ROOT, "ops", "room-diagrams.json")
    if not os.path.exists(manifest_path):
        print("  (skipped: ops/room-diagrams.json not present)")
        return
    manifest = json.loads(io.open(manifest_path, encoding="utf-8").read())
    assert len(manifest) >= 10, len(manifest)
    checked = 0
    for room, entry in sorted(manifest.items()):
        chapter = entry["chapter"]
        src = glob.glob(os.path.join(ROOT, "content", "book",
                                     "*Chapter-%d" % chapter,
                                     "chapter_%d_final.html" % chapter))
        assert src, "no source chapter for %s" % room
        book = io.open(src[0], encoding="utf-8", errors="replace").read()
        flat_book = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", book))
        probe = " ".join(entry["caption"].split()[:8])
        assert len(probe) > 20, (room, probe)
        assert probe in flat_book, (
            "%s: the caption shipped on the room page is not in chapter %d, "
            "so it was written somewhere other than the book: %r"
            % (room, chapter, probe))
        checked += 1
    assert checked >= 10, checked


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
