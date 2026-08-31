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
    """
    if not os.path.exists(VERDICTS):
        return {}
    raw = json.load(io.open(VERDICTS, encoding="utf-8"))
    out = {}
    for stem, rec in raw.items():
        png = os.path.join(HEROES, stem + ".png")
        if not isinstance(rec, dict) or not os.path.exists(png):
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


def figure(stem: str, meta: dict, prefix: str = "../",
           display: str | None = None) -> str:
    zone = display or meta.get("zone", "")
    room = meta.get("room", "")
    subject = meta.get("subject", "")
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
    body = re.sub(r"^(zone|area|station)[ ,]*", "", body, flags=re.I)
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
    alt = f"{zone} in the {room}, finished: {body}."
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
    if have and not ps:
        print("  nothing approved yet, so no page gets a picture")
        return 0
    if not apply_it:
        for _p, m, page, _d in ps[:5]:
            print(f"    {m['zone'][:30]:32} -> {os.path.basename(page)}")
        print("\n  --check only, nothing written")
        return 0

    wired, skipped = 0, 0
    for png, meta, page, display in ps:
        stem = os.path.splitext(os.path.basename(png))[0]
        derivatives(png, stem)
        s = io.open(page, encoding="utf-8").read()
        if 'id="zone-hero"' in s:
            skipped += 1
            continue
        # Directly after the intro, before the long instruction, because the
        # point is to answer "what am I aiming for" before the reading starts.
        m = re.search(r"(</p>)(\s*<(?:section|h2|div class=\"card))", s, re.S)
        if not m:
            skipped += 1
            continue
        s = s[:m.end(1)] + figure(stem, meta, display=display) + s[m.end(1):]
        io.open(page, "w", encoding="utf-8", newline="").write(s)
        wired += 1

    print(f"  wired {wired}, already present {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--apply" in sys.argv))
