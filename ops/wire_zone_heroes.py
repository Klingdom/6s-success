#!/usr/bin/env python3
"""
Put each zone's hero photograph onto its zone page, web sized.

WHY THIS MATTERS MORE THAN IT SOUNDS
------------------------------------
The site audit's largest single content finding was that all 114 zone pages
are thorough and contain no image at all. Each is 1,200 to 1,600 words of
genuinely useful instruction with nothing to look at, which is why the action
and the offer arrive after a long read.

An image at the top answers "what am I aiming for" before the reader commits
to the text, and it is the same answer the page's own words give, because the
picture was generated from that zone's done_looks_like sentence.

WHAT IT DOES NOT DO
-------------------
It does not claim the picture is a photograph of a real home. Every image
carries a caption saying it shows the finished state, and the alt text
describes what is in it rather than asserting provenance. A generated image
presented as documentary evidence would be the same class of error as a
fabricated testimonial.

GENERATOR OWNERSHIP
-------------------
ops/build_zone_pages.py rewrites all 114 pages from scratch, so a hand added
image would be destroyed on the next build. This is chained into that
generator the same way the chapter figures are, and running it twice changes
nothing.

Run:  python ops/wire_zone_heroes.py --check
      python ops/wire_zone_heroes.py --apply
"""
from __future__ import annotations

import glob
import hashlib
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
HEROES = os.path.join(ROOT, "build", "heroes", "zones")
WEB = os.path.join(SITE, "assets", "zones")

# Committed, not gitignored, unlike HEROES. Holds the already-approved figure
# HTML for every zone that had one at the moment this fallback was written
# (2026-09-01), extracted from the committed pages themselves rather than
# regenerated, so an environment with no source PNGs can still re-wire a page
# a fresh build just stripped instead of shipping it text only. See the note
# on approved() above for how this was found and why a fallback exists at
# all. Regenerate with the snippet in that commit if a newly approved zone
# ever needs to survive a source-less rebuild too; this file does not grow on
# its own.
FALLBACK = os.path.join(ROOT, "ops", "hero-fallback.json")

# The zone heroes are generated at 768x576, so an "lg" of 1024 was upscaling
# every one of them by a third: a 94 KB file carrying no more detail than the
# 768 wide original, offered to wide screens by the srcset and used as the
# social preview for every zone page. Manufacturing pixels and then charging
# the visitor to download them.
#
# lg is now the source's own width. A variant wider than its source is not a
# larger picture, it is the same picture and a bigger file.
SIZES = {"lg": None, "md": 640, "sm": 320}

NAME_MAP = json.load(io.open(os.path.join(ROOT, "ops", "zone-name-map.json"),
                             encoding="utf-8"))

# A generated picture is only publishable if somebody has looked at it.
#
# The first batch of 114 was wired onto every zone page before anyone did, and
# a spot check found the garage hand tool wall was a room of sawhorses and the
# board game zone was a stack of moving boxes. Both would have gone live under
# a caption reading "an illustration of the finished state", which is a claim
# about the picture, and in those two cases it was false. That is the same
# class of error as a fabricated before and after, arrived at by carelessness
# rather than intent, which does not make it better.
#
# So the manifest is the gate. Only a stem marked "ok" is wired. An image
# nobody has judged is treated exactly like one that failed, because at the
# moment of wiring those two things are indistinguishable.
# Tracked in the repo, not under build/, which is gitignored. These are
# judgements somebody made by looking at 114 pictures, not something a
# rebuild can reproduce, and losing them would silently un-publish every
# approved image on the next checkout.
VERDICTS = os.path.join(ROOT, "ops", "hero-verdicts.json")


def approved() -> dict:
    """Stems whose approval is about the picture currently on disk.

    The sha is checked, not just the verdict. Regenerating a zone produces a
    different image at the same path, and an approval that carried over would
    publish something nobody has looked at while counting it as reviewed.

    That check needs the source PNG, which lives under build/heroes/zones/,
    gitignored on purpose because it is only ever produced on Phil's own
    machine during a review session. Found 2026-09-01: a plain rebuild of
    the site in any environment without that folder, this cloud sandbox
    included, made every stem fail the sha check with nothing to hash
    against, so this function returned an empty dict, `_og_image()` in
    build_zone_pages.py silently fell back to the generic room-map picture
    for all 110 previously approved zones, and the same regeneration wiped
    the hero figure off every one of those pages, because nothing else in
    the pipeline knew they had ever been approved. This is the same shape
    of defect `gate_image_coverage` in preflight.py was already fixed for
    in a prior cycle (6.8): "cannot verify freshness here" is not the same
    claim as "not approved", and treating them the same silently unpublished
    110 real, reviewed images. Mirrors that gate's own fallback: when no
    source PNGs exist to re-hash against, trust the committed verdict by
    name instead of failing every stem closed.
    """
    if not os.path.exists(VERDICTS):
        return {}
    raw = json.load(io.open(VERDICTS, encoding="utf-8"))
    have_sources = bool(glob.glob(os.path.join(HEROES, "*.png")))
    out = {}
    for stem, rec in raw.items():
        if not isinstance(rec, dict):
            continue
        if not have_sources:
            out[stem] = rec["verdict"]
            continue
        png = os.path.join(HEROES, stem + ".png")
        if not os.path.exists(png):
            continue
        got = hashlib.sha256(io.open(png, "rb").read()).hexdigest()[:10]
        if rec.get("sha") == got:
            out[stem] = rec["verdict"]
    return out


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def pairs() -> list:
    """(hero png, meta, target page). Reviewed and approved images only."""
    ok = approved()
    out = []
    for png in sorted(glob.glob(os.path.join(HEROES, "*.png"))):
        mj = png.replace(".png", ".json")
        if not os.path.exists(mj):
            continue
        if ok.get(os.path.basename(png)[:-4]) != "ok":
            continue
        meta = json.load(io.open(mj, encoding="utf-8"))
        room, zone = meta.get("room"), meta.get("zone")
        if not room or not zone:
            continue
        # ops/zone-name-map.json is what build_zone_pages.py uses to name
        # these files, so it is the only correct source. Fuzzy matching on the
        # zone name matched 101 of 114 and silently dropped 13, because the
        # display names differ on purpose: Landing Zone is published as The
        # Landing Spot, and Nightstand Left as Your Own Nightstand. Guessing a
        # filename convention is how thirteen pages quietly get no picture.
        display = NAME_MAP.get(f"{room}|{zone}")
        if not display:
            continue
        hit = os.path.join(SITE, "zones",
                           f"{slug(room)}-{slug(display)}.html")
        if os.path.exists(hit):
            out.append((png, meta, hit, display))
    return out


def derivatives(png: str, stem: str) -> dict:
    from PIL import Image
    os.makedirs(WEB, exist_ok=True)
    im = Image.open(png).convert("RGB")
    made = {}
    for tag, want in SIZES.items():
        # None means "the source's own width", and any fixed width larger than
        # the source is clamped to it for the same reason.
        w = min(want, im.width) if want else im.width
        h = round(im.height * w / im.width)
        small = im.resize((w, h), Image.LANCZOS)
        for ext, kw in (("webp", dict(quality=80, method=6)),
                        ("jpg", dict(quality=80, optimize=True,
                                     progressive=True))):
            p = os.path.join(WEB, f"{stem}-{tag}.{ext}")
            small.save(p, **kw)
            made[f"{tag}.{ext}"] = p
    return made


def _srcset(stem: str, prefix: str) -> str:
    """The widths that exist, at the widths they really are.

    Two faults here at once. The 320 wide variant was generated for all 114
    zones and never named in any srcset, so every phone fetched the 640 one.
    And the largest was advertised as 1024w when the file is 768 wide, because
    it was being upscaled, so a browser choosing by width was told a number
    that was not true of the bytes it received.

    sizes said 680px while the real slot is about 1100px on a desktop, which
    made the browser pick a candidate for a box roughly a third narrower than
    the one it was filling.
    """
    from PIL import Image
    parts = []
    for tag in ("sm", "md", "lg"):
        f = os.path.join(WEB, f"{stem}-{tag}.webp")
        if not os.path.exists(f):
            continue
        w = Image.open(f).width
        parts.append((w, f"{prefix}assets/zones/{stem}-{tag}.webp {w}w"))
    # Deduplicate by width: on a 768 wide source, md and lg can collapse to
    # the same size, and offering one width twice tells a browser nothing.
    seen, out = set(), []
    for w, part in sorted(parts):
        if w in seen:
            continue
        seen.add(w)
        out.append(part)
    return ", ".join(out)


# Per-image alt text written by somebody who opened the file and described
# what is in it. Anything absent from this table gets the generic honest
# sentence in figure(), which is correct rather than detailed.
#
# Add an entry only after looking at the image. Never copy from the
# generation subject: doing that is the exact defect this table exists to
# undo.
ALT_VERIFIED = {
    "entryway--landing-zone":
        "A close view of a wooden tray on a table holding a folded wallet, a "
        "set of keys, a pen and a bottle opener, and nothing else.",
    "entryway--door-mat-and-immediate-floor":
        "A coir mat on bare wood floor just inside a front door, a planted "
        "basket to one side, nothing else on the floor.",
    "garage--hand-tool-wall-and-cabinets":
        "A pegboard wall of hand tools, saws, pliers, hammers and "
        "screwdrivers hung in rows above a low cabinet.",
    "hall-closet--paper-and-household-backstock":
        "Two shelves of household backstock: stacked packs of paper towels "
        "and rolls of toilet paper with folded cloths between them.",
    "guest-bedroom--guest-welcome-and-work-surface":
        "A guest room with a made bed beside a clear built-in desk, a small "
        "task lamp on it and a chair pulled up to it.",
    "kids-bedroom--clothing-closet":
        "An open child's wardrobe with clothes hung by type, dresses "
        "together and jackets together, folded stacks on the shelves above.",
    "kids-bedroom--school-and-activity-launch-zone":
        "A child's bedroom wall with a red backpack hanging on a hook at "
        "child height and low shelves of books and toys beneath it.",
    "kids-bedroom--study-desk":
        "A child's desk, empty except for a task lamp and a cup of pens.",
    "primary-bedroom--primary-closet":
        "A wide open wardrobe of shirts and jackets on matching hangers, "
        "grouped by type and then graded by colour along the rail.",
    "workshop--safety-and-ppe-station":
        "Three sets of ear defenders and a blue work jacket hanging on hooks "
        "on a plywood workshop wall.",
    "workshop--finishing-and-chemical-zone":
        "A close view of paint tins stacked several high on a workshop shelf.",
    "pantry--dry-goods-shelves":
        "Long open pantry shelves down one wall, jars and tins on the upper "
        "shelves and woven baskets on the lower ones.",
    "laundry-room--folding-surface":
        "A laundry room with a front-loading washer and dryer under a clear "
        "run of counter, one stack of folded white towels on it.",
    "patio-or-deck--outdoor-dining-zone":
        "An outdoor dining table under two open parasols, six chairs pushed "
        "in, the tabletop otherwise clear.",
    "patio-or-deck--garden-and-plant-care-zone":
        "A planted wall on a deck: herbs and flowers in pots along the boards "
        "with garden hand tools hanging on the wall behind them.",
}


def figure(stem: str, meta: dict, prefix: str = "../",
           display: str | None = None) -> str:
    zone = display or meta.get("zone", "")
    room = meta.get("room", "")
    subject = meta.get("subject", "")

    # WHY THIS NO LONGER READS OUT THE GENERATION SUBJECT.
    #
    # The alt was built from meta["subject"], which is the prompt: the thing
    # we ASKED the model for. It was then published as a description of the
    # picture the model returned. Those are not the same claim, and on most
    # of the 110 wired heroes they are not the same fact either. Checked by
    # opening the files:
    #
    #   entryway--shoe-and-boot-zone      alt: "boots standing in the tray"
    #                                     file: eight pairs loose on carpet,
    #                                     no tray anywhere in frame.
    #   garage--sports-and-recreation     alt: "bikes on wall hooks with bare
    #                                     floor beneath them"
    #                                     file: three bikes on the floor.
    #   hall-closet--cleaning-equipment   alt: "a vacuum, a broom and a mop
    #                                     inside an open closet"
    #                                     file: one vacuum on a rug, no
    #                                     broom, no mop, no closet.
    #   workshop--safety-and-ppe-station  alt: "safety glasses and a dust mask
    #                                     beside a first aid box"
    #                                     file: three sets of ear defenders
    #                                     and a jacket. On a safety page.
    #   guest-bedroom--guest-dresser      alt: "two drawers open showing
    #                                     folded clothes"
    #                                     file: every drawer shut.
    #
    # The same slicing also produced sentence fragments a screen reader reads
    # as whole sentences: "...a picture label on the drawer front. Socks."
    # and "...with its opening date written on it, or gone. Pasta."
    #
    # This is the failure class the module docstring above already warns
    # about, where the garage tool wall came back as sawhorses, but the
    # review that catches that one is looking for a picture of the WRONG
    # THING. It does not catch a picture of the right thing that simply does
    # not contain the detail the prompt asked for, and that is the common
    # case: the model drew a tidy room and left out the tray, the labels and
    # the dates.
    #
    # So the alt now states only what has been verified true of these images
    # as a class: which zone, which room, that it is an illustration, and
    # that the space is in order. A description somebody has actually looked
    # at goes in ALT_VERIFIED and overrides this. A prompt is not evidence
    # about its own output.
    #
    # `body` below is still computed because other callers read it; it is no
    # longer spoken as a description of the picture.
    # The alt text describes the picture. It does not claim it is a real room.
    # The generation subject ends in the style and material tail the model
    # needs ("warm wood and painted wall, daylight") and a screen reader does
    # not, so it is cut here. Read aloud, prompt syntax is noise.
    body = re.sub(r",\s*warm wood and painted wall.*$", "",
                  subject.split(":", 1)[-1].strip()).rstrip(" ,.")

    # The generation subject opens with the zone noun and closes with the room,
    # because that is what the model needed. Read aloud after a sentence that
    # already names both, it says each of them twice: "The Shoe and Boot Zone
    # in the Entryway, finished: shoe and boot zone, soles down, ..., in an
    # entryway." A screen reader user heard the room and the zone twice before
    # reaching anything useful. Both ends are trimmed here.
    # Trim against the GENERATION name, which is what the subject actually
    # opens with. Comparing against the published display name did nothing,
    # because "The Shoes and Boots" and "shoe and boot zone" share no prefix.
    gen = (meta.get("zone") or "").lower().strip()
    for cand in (gen, gen.rstrip("s"), gen.replace(" zone", ""),
                 gen.replace(" zone", "").rstrip("s")):
        if cand and body.lower().startswith(cand):
            body = body[len(cand):].lstrip(" ,")
            break
    # A truncated match left the tail of the noun behind: trimming 14
    # characters of "shoe and boot zone" left the word "zone" sitting at the
    # front of the sentence. Match the whole phrase or match nothing.
    body = re.sub(r"^(zone|area|station)\b[ ,]*", "", body, flags=re.I)
    body = re.sub(r",?\s*(in|on) an? [^,]*$", "", body).rstrip(" ,.")

    # The zone is named the way the page names it. figure() was using the
    # generation side name while the h1 uses the published one, so the picture
    # and the heading disagreed: "The Shoes and Boots" above "The Shoe and
    # Boot Zone".
    # The published name verbatim, with no article bolted on. Some carry one
    # already ("The Shoes and Boots") and some are possessive ("Your Own
    # Nightstand"), so any prefix is wrong for half of them: the first
    # attempt produced "The The Shoes and Boots" and "The Your Own
    # Nightstand" on the same run.
    # The generic form names the subject and stops. It does not describe the
    # contents, because nobody has looked at these 92 files one by one, and it
    # does not repeat "an illustration of the finished state", because the
    # figcaption directly below says exactly that and a screen reader reads
    # both. Short and true beats detailed and invented.
    alt = ALT_VERIFIED.get(stem) or f"{zone} in the {room}, illustrated."
    b = f"{prefix}assets/zones/{stem}"
    srcset = _srcset(stem, prefix)
    return (
        f'\n<figure class="zone-hero" id="zone-hero">\n'
        f'  <picture>\n'
        f'    <source type="image/webp" srcset="{srcset}" '
        f'sizes="(max-width:720px) 92vw, 1100px">\n'
        f'    <img src="{b}-md.jpg" alt="{alt}" width="640" height="480" '
        f'loading="eager" fetchpriority="high" decoding="async">\n'
        f'  </picture>\n'
        f'  <figcaption>An illustration '
        f'of the finished state, not a photograph of a real home.</figcaption>\n'
        f'</figure>\n')


def fallback_wire(apply_it: bool) -> int:
    """Re-insert an already-approved hero this environment cannot regenerate.

    Only runs when build/heroes/zones/ has no source PNGs at all, meaning
    pairs() has nothing to iterate over, which on every checkout but Phil's
    own machine is every run. Restores the exact figure markup FALLBACK
    recorded, so a page a plain rebuild just stripped gets its picture back
    without inventing new alt text or guessing a room/zone match.
    """
    if not os.path.exists(FALLBACK):
        return 0
    entries = json.load(io.open(FALLBACK, encoding="utf-8"))
    ok = approved()
    wired, skipped, stale = 0, 0, 0
    for fname, e in entries.items():
        page = os.path.join(SITE, "zones", fname)
        if not os.path.exists(page):
            continue
        if ok.get(e["stem"]) != "ok":
            # Approval was withdrawn since this fallback was written; do not
            # resurrect a picture that was later rejected.
            stale += 1
            continue
        s = io.open(page, encoding="utf-8").read()
        if 'id="zone-hero"' in s:
            skipped += 1
            continue
        if not apply_it:
            wired += 1
            continue
        m = re.search(r"(</p>)(\s*<(?:section|h2|div class=\"card))", s, re.S)
        if not m:
            skipped += 1
            continue
        s = s[:m.end(1)] + e["figure_html"] + s[m.end(1):]
        io.open(page, "w", encoding="utf-8", newline="").write(s)
        wired += 1
    if stale:
        print(f"  fallback: {stale} preserved hero(es) skipped, no longer "
              f"approved")
    print(f"  fallback: restored {wired}, already present {skipped}")
    return wired


def main(apply_it: bool) -> int:
    ps = pairs()
    have = len(glob.glob(os.path.join(HEROES, "*.png")))
    print(f"  heroes generated  {have}")
    print(f"  matched to a page {len(ps)}")
    ok = approved()
    print(f"  reviewed and ok   {sum(1 for v in ok.values() if v == 'ok')}")
    held = have - sum(1 for v in ok.values() if v == "ok")
    if held > 0:
        print(f"  held back         {held} not reviewed or not good enough, "
              f"so those pages stay text only")
    if not have:
        # No source pictures in this environment at all, the normal state of
        # every checkout but Phil's own machine. Restore what was already
        # approved instead of reporting nothing to wire.
        fallback_wire(apply_it)
        return 0
    if have and not ps:
        print("  nothing approved yet, so no page gets a picture")
        return 0
    if not apply_it:
        for _p, m, page, _d in ps[:5]:
            print(f"    {m['zone'][:30]:32} -> {os.path.basename(page)}")
        print("\n  --check only, nothing written")
        return 0

    # INSERT-ONLY WAS A ONE WAY DOOR, IN BOTH DIRECTIONS.
    #
    # This loop skipped any page that already carried a zone-hero and printed
    # "already present". That made the tool unable to change its own output,
    # with two consequences, neither visible from its own report.
    #
    # Forwards: a correction to the alt text could never reach a wired page.
    # The 110-page alt fix above would have written nothing at all.
    #
    # Backwards, and worse: setting a verdict to "no" in hero-verdicts.json
    # did nothing to a page that was already wired. Approval could be
    # withdrawn and the picture stayed live, so the review gate this module's
    # docstring describes only ever governed images that had not shipped yet.
    # Three heroes were withdrawn on 2026-09-04, a lab analyser standing in
    # for a home printer, an empty room on the family hook page and a
    # malformed cot, and all three would have stayed on the site.
    #
    # Now idempotent: an existing figure is replaced by the current one, and
    # the sweep below removes the figure from any page whose hero is no
    # longer approved. Running twice changes nothing; running after a change
    # applies it.
    FIG = re.compile(
        '\n?<figure class="zone-hero" id="zone-hero">.*?</figure>\n?',
        re.S)

    wired, updated, unchanged, skipped = 0, 0, 0, 0
    for png, meta, page, display in ps:
        stem = os.path.splitext(os.path.basename(png))[0]
        derivatives(png, stem)
        s = io.open(page, encoding="utf-8").read()
        fig = figure(stem, meta, display=display)
        if 'id="zone-hero"' in s:
            s2 = FIG.sub(lambda _m: fig, s, count=1)
            if s2 == s:
                unchanged += 1
            else:
                io.open(page, "w", encoding="utf-8", newline="").write(s2)
                updated += 1
            continue
        # Directly after the intro, before the long instruction, because the
        # point is to answer "what am I aiming for" before the reading starts.
        m = re.search(r"(</p>)(\s*<(?:section|h2|div class=\"card))", s, re.S)
        if not m:
            skipped += 1
            continue
        s = s[:m.end(1)] + fig + s[m.end(1):]
        io.open(page, "w", encoding="utf-8", newline="").write(s)
        wired += 1

    # Any page still carrying a hero that is no longer in the approved set.
    keep = {os.path.basename(page) for _p, _m, page, _d in ps}
    pulled = []
    for page in sorted(glob.glob(os.path.join(SITE, "zones", "*.html"))):
        if os.path.basename(page) in keep:
            continue
        s = io.open(page, encoding="utf-8").read()
        if 'id="zone-hero"' not in s:
            continue
        io.open(page, "w", encoding="utf-8",
                newline="").write(FIG.sub("", s, count=1))
        pulled.append(os.path.basename(page))

    print(f"  wired {wired}, alt or markup updated {updated}, "
          f"unchanged {unchanged}, no insertion point {skipped}")
    for name in pulled:
        print(f"  PULLED hero from {name}: no longer approved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--apply" in sys.argv))
