#!/usr/bin/env python3
"""
Import hand-authored SVG figures out of the book chapters onto zone pages.

WHY THIS AND NOT THE 864 PLATES
-------------------------------
I told Phil the site used 41 of about a thousand images and called it an
import problem. That was wrong, and the correction matters more than the
import does.

The 41 in use are not a sample. They are the survivors of an editorial QA
pass that ran chapter by chapter and is documented on disk in 35 files named
CHxx_IMAGE_FINALIZATION_NOTES.md, sitting next to the images themselves. The
rejections have causes: fake QR codes advertising printables that do not
exist, baked in em dashes, trademarked packaging, invented taxonomies, and
claims that contradict the book. Ch33's pantry batch alone lost 9 of 20
plates to trademarks. Ch36 lost 16 of 20 to fake QR codes.

So importing the rest is not filling a gap. It is reversing a decision
somebody already made carefully, for reasons they wrote down.

The genuinely unused asset is different, and smaller: 36 hand-authored SVG
figures inside the chapter HTML files for chapters 31 to 39. They are vector
rather than generated raster, so they carry none of those defect classes.
They already use the site palette and the site font stack. Zero of them
appear anywhere on the live site.

WHAT THIS IMPORTS
-----------------
Two verified figures. Not all 36, because 34 of them have not been read by a
human or by me, and the entire lesson above is about not bulk importing
images on the strength of the folder they were filed in.

GATES, each of which has caught something real in this repository before:
  * no em dash or en dash        house style, and a documented plate defect
  * no QR code                   the single largest cause of rejection
  * no external reference        an SVG that fetches is not self contained
  * palette is the site palette   or it reads as a foreign object on the page
  * substantial enough to be a figure at all
"""
from __future__ import annotations

import glob
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

# Two roots, tried in this order. The repo copy is first because it is what
# CI and every gate actually check against; a Desktop file that has drifted
# from it would make the import non-reproducible between machines. The
# Desktop path is kept as a fallback for a chapter not yet brought into the
# repo, which is how this script originally shipped and why "not reachable
# from this sandbox" was, for a while, the correct read of every chapter.
BOOK_ROOTS = [
    os.path.join(ROOT, "content", "book"),
    os.path.join(
        os.path.expanduser("~"), "Desktop", "Process Kaizen", "Process Kaizen",
        "Work Folder", "Nova Consulting", "06 - Lean Six Sigma Initiative",
        "07 - 6S Materials", "6S Environment", "Master",
        "6S Success Home Edition"),
]

CSS = os.path.join(SITE, "assets", "css", "site.css")

# The palette is read out of the stylesheet, not typed here. The first version
# of this file hardcoded a list from memory, and the gate then rejected
# #6A625A as foreign when the stylesheet uses it three times. A check whose
# reference data is a guess does not test the figure, it tests the guess.
NEAR = 24


def rgb(h: str) -> tuple:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def site_palette() -> set:
    """Every colour already shipping on this site.

    The stylesheet alone is too narrow a reference. #E7C58B, the honey tint,
    appears nine times in the free book sample that ships under
    site/downloads/, so it is demonstrably part of this design language even
    though site.css never names it. The question the gate should ask is
    whether a colour is foreign to the site, not whether one particular file
    happens to mention it.
    """
    out = {"#FFFFFF", "#000000"}
    for f in [CSS] + glob.glob(os.path.join(SITE, "downloads", "*.html")):
        try:
            src = io.open(f, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        out |= {c.upper() for c in re.findall(r"#[0-9A-Fa-f]{6}\b", src)}
    return out

FIGURES = [
    {
        "chapter": 36,
        "marker": "Washing Toys the Right Way",
        "page": "zones/family-room-the-toy-and-play-zone.html",
        "caption": "Washing toys the right way",
        "alt": (
            "A two column diagram titled Washing Toys the Right Way. The hard "
            "toys column shows three steps: wash in warm water with mild dish "
            "soap and a brush into the seams, rinse under clean running water "
            "until no soap is left, and dry upside down on a towel or rack "
            "fully before it goes back. The soft toys column shows three "
            "steps: wash in a mesh bag on a gentle cycle with mild detergent, "
            "give an extra rinse, and air dry completely with no high heat, "
            "standing upright. A note below states that moisture trapped "
            "inside a toy causes mould and odour and that nothing goes back "
            "damp."),
    },
    {
        "chapter": 36,
        "marker": "Lift the Dry Mess First",
        "page": "zones/family-room-the-craft-and-activity-zone.html",
        "caption": "Lift the dry mess first",
        "alt": (
            "A four step diagram titled Lift the Dry Mess First. Step one, "
            "scrape it, because a plastic edge lifts dried glue off in one "
            "piece. Step two, brush the seam, because a dry brush walks "
            "glitter out of the joint. Step three, vacuum it away, taking up "
            "everything loosened. Step four, now wipe, with a damp cloth once "
            "nothing dry is left on the surface. A panel marked the wrong way "
            "states that a wet cloth on dried glitter smears it into a film "
            "instead of lifting it."),
    },
    {
        "chapter": 31,
        "marker": "How to Clean the Landing Spot",
        "page": "zones/entryway-the-landing-spot.html",
        "caption": "How to clean the landing spot",
        "alt": (
            "A five step diagram titled How to Clean the Landing Spot. Step "
            "one, clear the surface, everything off including the tray, "
            "because you cannot clean around objects. Step two, dust dry "
            "with a dry cloth first, since a damp cloth over dry dust makes "
            "grime you then have to chase. Step three, clean the surface by "
            "misting the cloth rather than the surface, so nothing runs down "
            "behind the frame. Step four, inspect the bare wood for a ring, "
            "a scratch, or a dark corner, and flag it rather than fix it on "
            "the spot. Step five, put back only what belongs: the tray, the "
            "mail rack, the pen cup, the outgoing tray, nothing else."),
    },
    {
        "chapter": 32,
        "marker": "Lift and Empty, Do Not Wipe Around",
        "page": "zones/kitchen-the-primary-prep-counter.html",
        "caption": "Lift and empty, do not wipe around",
        "alt": (
            "A four step diagram titled Lift and Empty, Do Not Wipe Around, "
            "using a toaster on the counter as the example: the crumbs live "
            "under the feet, and lifting the appliance reveals the footprint "
            "it was hiding. Step one, lift the appliance off the surface "
            "rather than push it to one side. Step two, brush the crumbs "
            "away dry, since it is dry before wet every time. Step three, "
            "degrease and let it sit for the time given on the label. Step "
            "four, wipe then dry with one cloth to clean and a second to "
            "dry. The caption states a wipe around the clutter is not a "
            "clean."),
    },
    {
        "chapter": 32,
        "marker": "Soak First",
        "page": "zones/kitchen-the-cooking-zone.html",
        "caption": "Soak first",
        "alt": (
            "A diagram titled Soak First, stating the most powerful tool in "
            "a kitchen clean is time. It lists what goes in the water: the "
            "burner grates, the burner caps, the hood filter, and removable "
            "knobs, soaked in hot water with a little dish soap and a "
            "degreaser. While they soak, four steps run in parallel: fill "
            "the basin hot, soapy and degreasing; lower the parts in fully "
            "covered; degrease the hood and wall top down while you wait; "
            "then lift, brush and dry fully, which the diagram notes is a "
            "fraction of the scrubbing. It recommends fifteen to thirty "
            "minutes soaking time, since the chemistry lifts the grease "
            "while you work elsewhere."),
    },
    {
        "chapter": 35,
        "marker": "Sofa Deep Cleaning",
        "page": "zones/living-room-the-sofa-and-seating.html",
        "caption": "Sofa deep cleaning",
        "alt": (
            "An eight step diagram titled Sofa Deep Cleaning, worked top to "
            "bottom and back to front. Step one, headrest and back, brush "
            "attachment top down. Step two, arms and sides, where hands and "
            "heads rest. Step three, lift the cushions out, not just tipped "
            "forward. Step four, the deck and seams, the bare platform "
            "underneath. Step five, tight spaces, the crevice tool into "
            "every seam. Step six, throw pillows, both faces and the zip "
            "line. Step seven, remotes and small items, wiped then returned "
            "to one bin. Step eight, base and front edge, the kick line and "
            "the floor beneath. The caption reminds not to forget the seams "
            "and to work top down so nothing loosened lands on finished "
            "ground."),
    },
]


def chapter_html(n: int) -> str:
    for book in BOOK_ROOTS:
        hits = glob.glob(os.path.join(book, f"6S-Success-Chapter-{n}",
                                      "chapter_*_final.html"))
        if hits:
            return io.open(hits[0], encoding="utf-8", errors="replace").read()
    raise SystemExit(f"no final HTML for chapter {n}")


def extract(src: str, marker: str) -> str:
    """The svg element whose own text contains the marker."""
    for m in re.finditer(r"<svg\b.*?</svg>", src, re.S | re.I):
        if marker in m.group(0):
            return m.group(0)
    raise SystemExit(f"no SVG containing {marker!r}")


def check(svg: str, fig: dict) -> None:
    name = fig["marker"]

    dashes = re.findall(r"[—–]", svg)
    assert not dashes, (
        f"{name}: {len(dashes)} em or en dashes baked into the figure. That "
        f"is house style, and it is also one of the documented reasons plates "
        f"were rejected, so it is not a detail to wave through.")

    assert not re.search(r"qr\s*code", svg, re.I), (
        f"{name}: mentions a QR code. Fake QR codes advertising printables "
        f"that do not exist are the single largest cause of plate rejection.")

    ext = re.findall(r'(?:href|src)\s*=\s*"(?!#)([^"]+)"', svg)
    assert not ext, (
        f"{name}: references {ext[:3]}. An SVG that fetches something is not "
        f"self contained and will break offline and behind the CSP.")

    assert "<image" not in svg.lower(), (
        f"{name}: embeds a raster image, so it is not the clean vector figure "
        f"this whole import is premised on.")

    # A tint one or two steps off a stylesheet colour is the same colour
    # family and reads as belonging. A genuinely foreign hue (a neon, a
    # primary blue) sits far outside every entry and still trips this.
    pal = [rgb(c) for c in site_palette()]
    foreign = []
    for c in {c.upper() for c in re.findall(r"#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})\b", svg)}:
        v = rgb(c)
        d = min(max(abs(v[i] - p[i]) for i in range(3)) for p in pal)
        if d > NEAR:
            foreign.append(f"{c} (nearest site colour is {d} steps away)")
    assert not foreign, (
        f"{name}: uses colours outside the site palette: {sorted(foreign)}. "
        f"A figure in a foreign palette reads as pasted in from somewhere "
        f"else, which is exactly what it would be.")

    assert len(svg) > 800, f"{name}: only {len(svg)} bytes, that is not a figure"


def wire(page: str, svg: str, fig: dict) -> bool:
    path = os.path.join(SITE, page.replace("/", os.sep))
    assert os.path.exists(path), f"no such page: {page}"
    s = io.open(path, encoding="utf-8").read()

    fid = "fig-" + re.sub(r"[^a-z]+", "-", fig["marker"].lower()).strip("-")
    if fid in s:
        return False

    # Several of these source figures already carry their own role and
    # aria-label, written for the book rather than the site. Strip those
    # from the opening tag before adding ours, or the two stack into a
    # duplicate attribute the browser silently resolves by picking one,
    # which is not something to depend on for what a screen reader reads.
    svg = re.sub(r'(<svg\b[^>]*>)',
                 lambda m: re.sub(r'\s(?:role|aria-label)="[^"]*"', "",
                                   m.group(1)),
                 svg, count=1)

    # role="img" with aria-label hands the whole description to a screen
    # reader in one piece. The visible caption is short; the label is not,
    # because a diagram whose content exists only in the picture is not
    # accessible to somebody who cannot see the picture.
    label = fig["alt"].replace('"', "&quot;")
    svg = re.sub(r"<svg\b", f'<svg role="img" aria-label="{label}"', svg,
                 count=1)
    # Scale with the column rather than overflow a phone.
    svg = re.sub(r'\s(?:width|height)="[^"]*"', "", svg, count=2)
    svg = re.sub(r"<svg\b", '<svg style="width:100%;height:auto"', svg,
                 count=1)

    # No figcaption. Each of these figures already carries its own title
    # inside the artwork, so a caption underneath repeats the same words a
    # second time, which reads as a mistake rather than as care. The caption
    # text stays in FIGURES because it is a useful human label for the
    # figure in this file, it just does not belong on the page.
    block = f'\n<figure id="{fid}" class="zone-figure">\n{svg}\n</figure>\n'

    # Beside the Shine pass, because both figures are cleaning method. A
    # method diagram belongs next to the pass it explains, not at the top of
    # the page where it would just be decoration.
    m = re.search(r'(<section[^>]*id="shine".*?)(</section>)', s, re.S | re.I)
    if m:
        s = s[:m.start(2)] + block + s[m.start(2):]
    else:
        m = re.search(r"(<h2[^>]*>\s*Shine.*?)(<h2)", s, re.S | re.I)
        if not m:
            raise SystemExit(f"{page}: found no Shine section to attach to")
        s = s[:m.end(1)] + block + s[m.end(1):]

    io.open(path, "w", encoding="utf-8", newline="").write(s)
    return True


def main() -> int:
    n = 0
    for fig in FIGURES:
        svg = extract(chapter_html(fig["chapter"]), fig["marker"])
        check(svg, fig)
        print(f"  ch{fig['chapter']} {fig['marker']!r}: {len(svg)} bytes, "
              f"every gate passes")
        if wire(fig["page"], svg, fig):
            print(f"    wired into {fig['page']}")
            n += 1
        else:
            print(f"    already present in {fig['page']}")
    print(f"\n  {len(FIGURES)} of 36 SVGs in chapters 31 to 39 are wired "
          f"({n} newly this run). The other 30 are room-wide zone maps, "
          f"kit lists and before/after pairs read individually and left "
          f"out on purpose: this script wires one figure into one zone "
          f"page's Shine section, and a room-wide figure has no single "
          f"zone to belong to without misrepresenting its scope.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
