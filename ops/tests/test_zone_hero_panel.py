#!/usr/bin/env python3
"""
Prove the typographic zone-hero panel is well formed, responsive, honest, and
distinguishable from a photograph.

WHY THIS EXISTS
---------------
Three zones have a rejected photographic hero (home-office file-storage,
home-office printer-and-scanning-station, workshop material-rack). Until
2026-09-27 wire_zone_heroes' sweep removed their <figure> and left nothing, so
three pages shipped with no image while 111 carried one, and preflight's
page-art warning had no action available: the only fix on offer was a
photograph the local model cannot draw (LRN-0012).

panel_figure() fills the slot with the zone's own done_looks_like, the way
ops/video_zone.py already solves the same shortage for the films. Building it
produced three real defects in a row, each caught by a different check, and
each is pinned below:

  1. A fixed width="900" on the svg gave 926px of document on a 390px phone,
     i.e. sideways scroll on the page the figure was added to help. Caught by
     ops/audit_visual.py.
  2. An extra style attribute on the <figure> meant FIG no longer matched it,
     so FIG.sub() replaced nothing, the page was written back unchanged, the
     sweep still reported "(panel)", and three pages ended up holding a figure
     nothing in the pipeline could replace again.
  3. Counting the panel as "carries a photograph" made gate_image_coverage read
     114 photographs against 111 approved images, which would have been a false
     claim about the site.

Run:  python ops/tests/test_zone_hero_panel.py
"""
import glob
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import wire_zone_heroes as W                                   # noqa: E402

DONE = ("Hanging folders labelled by the question you would ask, tabs all in "
        "the same position, a closed fireproof box, and a full shred bag.")


def case_svg_is_valid_xml():
    out = W.panel_figure("Home Office", "The File Storage", DONE)
    svg = re.search(r"(<svg.*?</svg>)", out, re.S).group(1)
    ET.fromstring(svg)


def case_ampersands_and_brackets_do_not_break_it():
    """SVG is XML: one raw & in a zone name and the browser drops the graphic."""
    out = W.panel_figure("Kitchen", "Pots & Pans", "Lids & bases < 3 deep.")
    svg = re.search(r"(<svg.*?</svg>)", out, re.S).group(1)
    ET.fromstring(svg)


def case_no_fixed_width_on_the_svg():
    """Defect 1. A fixed width overflows a phone; the viewBox must do the work."""
    out = W.panel_figure("Workshop", "The Material Rack", DONE)
    tag = re.match(r"<figure[^>]*>\s*(<svg[^>]*>)", out).group(1)
    assert 'width="900"' not in tag, tag
    assert "viewBox=" in tag, tag
    assert "width:100%" in tag, tag


def case_figure_tag_matches_FIG():
    """Defect 2. If FIG cannot match its own output, the figure is unremovable."""
    out = W.panel_figure("Workshop", "The Material Rack", DONE)
    assert W.FIG.search(out), "FIG does not match the panel it will insert"


def case_FIG_matches_a_figure_carrying_attributes():
    """The stranding case itself: FIG must not be defeated by an attribute."""
    stranded = ('<figure class="zone-hero" id="zone-hero" style="margin:26px 0">'
                '<svg></svg></figure>')
    assert W.FIG.search(stranded), "an attribute on the figure strands it again"


def case_caption_does_not_imply_a_photograph():
    out = W.panel_figure("Workshop", "The Material Rack", DONE)
    low = out.lower()
    assert "no photograph" in low, "the caption must say there is no photograph"
    for claim in ("photograph of a real home", "illustration of the finished"):
        assert claim not in low, claim


def case_only_the_corpus_text_appears():
    """Nothing is written to fill the space."""
    out = W.panel_figure("Workshop", "The Material Rack", DONE)
    body = " ".join(re.findall(r'class="d">([^<]*)</text>', out))
    for word in DONE.replace(",", "").replace(".", "").split()[:8]:
        assert word in body, word


def case_the_three_real_pages_carry_a_panel():
    want = ["home-office-the-file-storage.html",
            "home-office-the-printer-and-scanning-station.html",
            "workshop-the-material-rack.html"]
    for name in want:
        fp = os.path.join(ROOT, "site", "zones", name)
        if not os.path.exists(fp):
            continue
        s = io.open(fp, encoding="utf-8", errors="replace").read()
        assert 'id="zone-hero"><svg' in s, name + " has no panel"
        ET.fromstring(re.search(r'(<svg xmlns.*?</svg>)', s, re.S).group(1))


def case_photographic_pages_are_untouched():
    """The 111 approved heroes must still be pictures, not panels."""
    panels = 0
    photos = 0
    for fp in glob.glob(os.path.join(ROOT, "site", "zones", "*.html")):
        s = io.open(fp, encoding="utf-8", errors="replace").read()
        if 'id="zone-hero"><svg' in s:
            panels += 1
        elif 'id="zone-hero"' in s:
            photos += 1
    assert photos >= 100, photos
    assert panels <= 6, panels


def case_room_panels_use_their_own_class():
    """A room panel must NOT answer to bare "room-lead".

    gate_pages_missing_art counts class="room-lead" to find chapters with no
    illustration. If a text panel took that name, all 11 unillustrated rooms
    would read as illustrated and the artwork gap OWNER-ACTIONS 1b tracks would
    disappear from the report. Two facts, two markers.
    """
    import xml.etree.ElementTree as _ET
    rooms = glob.glob(os.path.join(ROOT, "site", "rooms", "*.html"))
    rooms = [f for f in rooms if not f.endswith("index.html")]
    assert rooms, "no room pages found"
    panels, illustrated, bare = 0, 0, []
    for fp in rooms:
        s = io.open(fp, encoding="utf-8", errors="replace").read()
        if "room-lead-panel" in s:
            panels += 1
            _ET.fromstring(re.search(r'(<svg xmlns.*?</svg>)', s, re.S).group(1))
            assert "no illustration for this room yet" in s.lower(), fp
        elif 'class="room-lead"' in s:
            illustrated += 1
        else:
            bare.append(os.path.basename(fp))
    assert not bare, "room page(s) with no lead at all: %s" % bare
    assert panels >= 1 and illustrated >= 1, (panels, illustrated)


def case_no_room_page_is_imageless():
    rooms = [f for f in glob.glob(os.path.join(ROOT, "site", "rooms", "*.html"))
             if not f.endswith("index.html")]
    for fp in rooms:
        s = io.open(fp, encoding="utf-8", errors="replace").read()
        assert 'class="room-lead' in s, os.path.basename(fp)


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
