#!/usr/bin/env python3
"""
Static save-and-share cards for Pinterest and Instagram, one per zone.

WHY THIS EXISTS
----------------
GOALS.md names the constraint plainly: 52 visitors, 144 visits in 30 days,
one of them from a search engine. Every channel that could change that (YouTube, TikTok,
Reels) needs an account only Phil can create. GOALS.md also names the two
things that do not: "SEO, internal linking, structured data, page speed, and
the Pinterest and Instagram crops, none of which need an account to prepare."

Pinterest and Instagram feed are not video-first the way Shorts and Reels
are. A "save this" checklist card, sized correctly for each surface, is the
native format, and Pinterest in particular rewards exactly this: a
specific, useful, text-forward image someone would pin against "how do I
fix my mail zone."

WHY A NEW FILE INSTEAD OF EXTENDING video_zone.py
--------------------------------------------------
video_zone.py's CSS is tuned in fixed pixels for one canvas, 1080x1920 or
1920x1080 (--wide), a 9:16 or 16:9 frame. Pinterest is 2:3 (1000x1500) and
Instagram feed is 4:5 (1080x1350), both close to square, nothing like as
tall as a Reel. Reusing that CSS unmodified for these would be exactly the
auto-crop MEDIA-OPERATIONS-PLAN.md section 5 warns against: text sized and
padded for a portrait video frame, dropped onto a squatter canvas, either
overflowing or leaving dead space. This file composes its own layout, sized
in vw/vh so the same markup renders correctly at either target resolution
without a second hand-tuned stylesheet, and reuses only what is genuinely
shared: browser discovery, the zone list, and the brand fonts.

THE ZONE PICTURE, AND HOW THE CARD STILL FITS (added 2026-09-15)
-----------------------------------------------------------------
The first version was text only, with the bottom 40% of every card empty
cream. Pinterest is a picture feed. Each zone with an approved illustration
(the same verdicts the site and the app use: quest-data.js carries an img
stem only for approved zones, 106 of 114) now leads with that picture.

A picture and a four-item checklist compete for one canvas, so the card is
fitted in the browser, in this order, and the result is read back:
  1. drop the purpose line (the caption carries it);
  2. shrink the picture band, not below 22% of the height;
  3. shrink the checklist type, not below 2.2% of the height;
  3b. leave the last item for the zone page, one item at most and never
      fewer than three shown, with a "+ 1 more on the zone page" line;
  4. last resort: remove the picture and use the text-only layout.
The checklist is the zone's whole standard, split by done_items() without
losing a word (its docstring says how and why the old split was replaced).
With a picture, each checklist item shows its first sentence only, the card
template's own rule (trim at a sentence boundary, never shrink past legible).
The full wording stays on the zone page and in the caption.

Sizes are pixels computed from the canvas, not vh/vw. Headless Edge lays a
1000x1500 window out at 976x1408, so vh was 14.08px, not 15, and a DOM dump
(which is how the fit is verified) did not lay out like the screenshot.
Measured 2026-09-15. A card whose checklist still overflows fails the build.

Pictures make a PNG about 500 KB. These files are committed, so a card with
a picture is saved as a 256-colour PNG (about 220 KB), same name and size.

WHAT IT DOES NOT DO
--------------------
Post anywhere. That needs the account only Phil can create (same wall as
3.10 and epic 3). This prepares the asset so posting is a single step once
the account exists, per CLAUDE.md 0.5.

Run:  python ops/build_social_pins.py --list
      python ops/build_social_pins.py --zone "Landing Zone"
      python ops/build_social_pins.py --all
"""
from __future__ import annotations

import io
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))
import video_zone as VZ  # noqa: E402  (zones(), browser(), FONTS)
import build_mobile_corpus as BMC  # noqa: E402  (load_source(): approved zone pictures)

PIN_DIR = os.path.join(ROOT, "build", "social", "pinterest")
IG_DIR = os.path.join(ROOT, "build", "social", "instagram")

# 2:3, Pinterest's documented standard pin ratio.
PIN_W, PIN_H = 1000, 1500
# 4:5, Instagram's tallest allowed feed ratio, the most screen a feed post can claim.
IG_W, IG_H = 1080, 1350

ZONE_ART = os.path.join(ROOT, "site", "assets", "zones")
ART_FRACTION = {"pinterest": 0.36, "instagram": 0.31}   # starting band height
ART_FLOOR, TYPE_FLOOR = 0.22, 0.022                     # fractions of canvas height

INK, PAPER, ACCENT = "#2B2622", "#F7F2E9", "#BC4B2A"
HONEY, FOOTER = "#DDA63A", "#8C8478"

# vw/vh throughout, not px: the same markup renders correctly at 1000x1500
# and 1080x1350 without a second hand-tuned stylesheet, and stays correct if
# a third surface (e.g. Facebook's 1:1) ever needs the same card.
SHELL = """<!doctype html><meta charset="utf-8"><style>
@font-face{{font-family:Fraunces;src:url('file:///{fonts}/Fraunces-600-normal.woff2')format('woff2');font-weight:600}}
@font-face{{font-family:Inter;src:url('file:///{fonts}/Inter-600-normal.woff2')format('woff2');font-weight:600}}
@font-face{{font-family:Inter;src:url('file:///{fonts}/Inter-700-normal.woff2')format('woff2');font-weight:700}}
*{{box-sizing:border-box;margin:0}}
html,body{{width:{w}px;height:{h}px;overflow:hidden}}
/* The footer is pinned to an absolute bottom offset rather than pushed
   there by flex growth: a flex child's default min-height is its own
   content size, so with one to four checklist items of varying length,
   flex:1 growth on the list could not reliably shrink below its content
   and silently pushed the footer past the canvas edge, clipped by
   overflow:hidden. Caught by reading the actual rendered PNG, not the
   clean exit code, the same gap cycle 8 paid for on the book cover. */
body{{position:relative;background:{paper};color:{ink};
  font-family:Inter,Arial,sans-serif;padding:6vh 7vw 15vh}}
.eyebrow{{font-size:2.6vh;font-weight:700;letter-spacing:.16em;
  text-transform:uppercase;color:{accent};margin-bottom:1.6vh}}
h1{{font-family:Fraunces,Georgia,serif;font-weight:600;font-size:6.4vh;
  line-height:1.05;letter-spacing:-.01em;margin-bottom:.6vh}}
.sub{{font-size:2.5vh;line-height:1.35;color:#5b544a;margin-bottom:3.4vh}}
.bar{{height:.7vh;width:9vh;background:{honey};border-radius:99px;margin-bottom:3vh}}
ul{{list-style:none;padding:0;display:flex;flex-direction:column;gap:2.4vh}}
li{{font-size:2.9vh;line-height:1.3;display:flex;gap:1.6vh;align-items:flex-start}}
li b{{flex:0 0 4.2vh;height:4.2vh;border-radius:50%;background:{accent};
  color:{paper};font:700 2vh/4.2vh Inter;text-align:center}}
.foot{{position:absolute;left:7vw;right:7vw;bottom:8vh;
  display:flex;align-items:center;justify-content:space-between;
  padding-top:3vh;border-top:.15vh solid #e2d8c4}}
.brand{{font:700 2.2vh/1.4 Inter;letter-spacing:.02em}}
.cta{{font:600 2vh/1.4 Inter;color:{accent}}}
</style><body>{body}</body>"""


_SENTENCE = re.compile(r"(?<=[^.][.!?])[ ]+(?=[A-Z])")
_COUNT = re.compile(r"^(one|a|an|no|each|every|two|three|four|five|six|a single|only|nothing|all|both)[ ]", re.I)


def done_items(z: dict) -> list:
    """The zone's finished standard as checkable items, every word kept.

    Rewritten 2026-09-15. The previous split cut at every comma and at " and ",
    which chopped lists apart and lost words: "one wallet and one phone per
    adult" became "One phone per adult", "the salt. The kettle" was welded
    into one item, and 76 of the items across 114 zones read as fragments. It
    also kept only the first four items, which dropped standards such as "The
    cabinet strapped to a wall stud".

    Now: a standard written as several sentences gives one item per sentence.
    A standard written as one sentence is a comma list, split at top-level
    commas, where a short part that starts a count ("one wash") joins the part
    after it, since it shares that part's qualifier ("one bar per person in
    the caddy"), and a short part that does not ("soles down") belongs to the
    part before it. No cap: the card decides how many fit.
    """
    raw = str(z.get("done_looks_like") or "").strip()
    sents = [s.strip().rstrip(".") for s in _SENTENCE.split(raw) if s.strip()]
    if len(sents) > 1:
        out = sents
    else:
        parts = [re.sub(r"^and ", "", p.strip())
                 for p in re.split(r",(?![^(]*[)])", sents[0] if sents else "")]
        out, carry = [], ""
        for p in parts:
            if not p:
                continue
            short = len(p.split()) < 3
            if short and _COUNT.match(p):
                carry = (carry + ", " if carry else "") + p
                continue
            if short and out and not carry:
                out[-1] = out[-1] + ", " + p
                continue
            out.append((carry + ", " + p) if carry else p)
            carry = ""
        if carry:
            if out:
                out[-1] = out[-1] + ", " + carry
            else:
                out.append(carry)
    return [o[0].upper() + o[1:] for o in out if o]


_SENT = re.compile(r"(?<=[^.][.!?])[ ]+")
_UNIT = re.compile(r"([0-9]*[.]?[0-9]+)(vh|vw)")


def first_sentence(text: str) -> str:
    """The item's first sentence. Not split at an ellipsis."""
    return _SENT.split(text.strip())[0].rstrip(".")


def approved_art() -> dict:
    """{(room, zone): image stem} for zones with an approved illustration.

    quest-data.js is the published record of which pictures passed review; it
    carries an img stem only for those. Reusing it means a withdrawn picture
    leaves the pins the next time they are built, as it leaves the site.
    """
    src = BMC.load_source()
    return {(r["room"], z["zone"]): z["img"]
            for r in src["rooms"] for z in r["zones"] if z.get("img")}


def to_px(css: str, w: int, h: int) -> str:
    """vh and vw as pixels of the canvas itself (see the docstring for why)."""
    def one(m):
        base = h if m.group(2) == "vh" else w
        return "%gpx" % round(float(m.group(1)) * base / 100, 1)
    return _UNIT.sub(one, css)


FIT_JS = io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "social_pin_fit.js"), encoding="utf-8").read()


def card_html(room: str, z: dict, w: int, h: int, art: str = None,
              surface: str = "pinterest") -> str:
    """One card. art is an approved image stem, or None for the text-only card."""
    name = z["zone"]
    purpose = str(z.get("purpose") or "").strip()
    items = done_items(z)
    full = "".join(f"<li><b>{i+1}</b><span>{d}</span></li>" for i, d in enumerate(items))
    shown = full
    picture, template = "", ""
    # The "+ N more" line the fit script adds when it leaves trailing items
    # for the zone page. Indented to sit under the item text, not the numbers.
    extra = ("li.more{display:block;white-space:nowrap;font-size:%gpx;font-weight:600;color:%s;padding-left:%gpx}"
             % (round(2.2 * h / 100, 1), ACCENT, round(5.8 * h / 100, 1)))
    if art:
        shown = "".join(f"<li><b>{i+1}</b><span>{first_sentence(d)}</span></li>"
                        for i, d in enumerate(items))
        template = f'<template id="full-items">{full}</template>'
        src = "file:///" + os.path.join(ZONE_ART, art + "-lg.jpg").replace(os.sep, "/")
        picture = f'<div class="art"><img src="{src}" alt=""></div>'
        extra += (".art{width:100%%;height:%dpx;border-radius:%dpx;overflow:hidden;"
                 "margin-bottom:%dpx;background:#e9e1d2}"
                 ".art img{width:100%%;height:100%%;object-fit:cover;display:block}"
                 ".has-art li{font-size:%gpx}.has-art .eyebrow{font-size:%gpx}"
                 % (round(ART_FRACTION[surface] * h), round(0.014 * h), round(0.034 * h),
                    round(2.6 * h / 100, 1), round(2.3 * h / 100, 1)))
    body = (
        picture +
        f'<p class="eyebrow">{room} &middot; free zone reset</p>'
        f'<h1>{name}</h1>'
        f'<div class="bar"></div>'
        f'<p class="sub">{purpose}</p>'
        f'<ul>{shown}</ul>' + template +
        f'<div class="foot"><span class="brand">6S Success</span>'
        f'<span class="cta">6s-success.com</span></div>'
        + FIT_JS % {"h": h, "art_floor": ART_FLOOR, "type_floor": TYPE_FLOOR}
    )
    doc = SHELL.format(fonts=VZ.FONTS, w=w, h=h, paper=PAPER, ink=INK,
                       accent=ACCENT, honey=HONEY, footer=FOOTER, body="@@BODY@@")
    head, tail = doc.split("</style>", 1)
    doc = to_px(head, w, h) + extra + "</style>" + tail.replace("@@BODY@@", body)
    if art:
        doc = doc.replace("<!doctype html>", '<!doctype html><html class="has-art">', 1)
    return doc


def shot(exe: str, extra_args: list, html: str, png: str, w: int, h: int) -> None:
    with tempfile.TemporaryDirectory() as prof:
        f = png.replace(".png", ".html")
        io.open(f, "w", encoding="utf-8", newline="").write(html)
        subprocess.run([exe, "--headless=new", "--disable-gpu",
                        "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--user-data-dir={prof}", f"--window-size={w},{h}",
                        "--virtual-time-budget=8000", "--allow-file-access-from-files",
                        f"--screenshot={png}",
                        *extra_args,
                        "file:///" + os.path.abspath(f).replace(os.sep, "/")],
                       capture_output=True, timeout=90)
        os.remove(f)


def measure(exe: str, extra_args: list, html: str, png: str, w: int, h: int) -> tuple:
    """(verdict, steps) as the page's own fit script recorded them.

    A separate --dump-dom run of the same document. It lays out identically to
    the screenshot only because every size is in pixels (see the docstring).
    No verdict attribute means nothing was measured, and is reported as such.
    """
    with tempfile.TemporaryDirectory() as prof:
        f = png.replace(".png", ".measure.html")
        io.open(f, "w", encoding="utf-8", newline="").write(html)
        dom = subprocess.run([exe, "--headless=new", "--disable-gpu",
                              "--hide-scrollbars", "--force-device-scale-factor=1",
                              f"--user-data-dir={prof}", f"--window-size={w},{h}",
                              "--virtual-time-budget=8000", "--allow-file-access-from-files",
                              "--dump-dom", *extra_args,
                              "file:///" + os.path.abspath(f).replace(os.sep, "/")],
                             capture_output=True, timeout=90, text=True,
                             encoding="utf-8", errors="replace").stdout
        os.remove(f)
    fit = re.search(r'data-fit="([^"]+)"', dom or "")
    steps = re.search(r'data-steps="([^"]*)"', dom or "")
    return (fit.group(1) if fit else "not measured", steps.group(1) if steps else "")


def palette_png(png: str) -> bool:
    """Re-save a picture card as a 256-colour PNG, same name and size.

    Pillow is imported here and only here: build_social_captions.py imports
    this module in CI, where Pillow is not a dependency. Returns False, leaving
    the full-colour file in place, if Pillow is missing.
    """
    try:
        from PIL import Image
    except ImportError:
        return False
    im = Image.open(png).convert("RGB")
    im.quantize(colors=256, method=Image.Quantize.MEDIANCUT,
                dither=Image.Dither.FLOYDSTEINBERG).save(png, optimize=True)
    return True


def png_dims(path: str) -> tuple:
    """Read the actual pixel size out of the PNG IHDR chunk. No Pillow: this
    project deliberately keeps ops/requirements.txt to pymupdf alone, since
    preflight runs beside Stripe and SMTP credentials in CI (see 6.40's own
    note). A clean screenshot exit code is not proof of a correct canvas, the
    same lesson cycle 8 paid for on the book cover; this is how that gets
    checked without a new dependency.
    """
    with open(path, "rb") as fh:
        head = fh.read(33)
    if head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        return (0, 0)
    w, h = int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")
    return (w, h)


def build_one(room: str, z: dict, art_map: dict = None) -> dict:
    """Render both surfaces for one zone. Returns {surface: (path, steps)}."""
    exe, extra_args = VZ.browser()
    os.makedirs(PIN_DIR, exist_ok=True)
    os.makedirs(IG_DIR, exist_ok=True)
    art_map = approved_art() if art_map is None else art_map
    art = art_map.get((room, z["zone"]))
    if art and not os.path.exists(os.path.join(ZONE_ART, art + "-lg.jpg")):
        raise SystemExit(f"approved picture {art}-lg.jpg is missing for {room}/{z['zone']}")
    slug = f"{VZ.zone_slug(room, z['zone'])}.png"
    out = {}
    for label, w, h, d in (("pinterest", PIN_W, PIN_H, PIN_DIR),
                            ("instagram", IG_W, IG_H, IG_DIR)):
        png = os.path.join(d, slug)
        html = card_html(room, z, w, h, art, label)
        verdict, steps = measure(exe, extra_args, html, png, w, h)
        if verdict != "ok":
            raise SystemExit(f"{label} card for {room}/{z['zone']} did not fit: "
                              f"{verdict} ({steps})")
        shot(exe, extra_args, html, png, w, h)
        if not os.path.exists(png):
            raise SystemExit(f"{label} card did not render for {room}/{z['zone']}")
        if art and "picture removed" not in steps and not palette_png(png):
            steps += ", full colour (Pillow missing)"
        got = png_dims(png)
        if got != (w, h):
            raise SystemExit(f"{label} card for {room}/{z['zone']} rendered at "
                              f"{got}, not the required {(w, h)}")
        out[label] = (png, steps)
    return out


if __name__ == "__main__":
    zs = VZ.zones()
    if "--list" in sys.argv or "--list-all" in sys.argv:
        print(f"  {len(zs)} zones")
        show = zs if "--list-all" in sys.argv else zs[:6]
        for r, z in show:
            print(f"    {r:18} {z['zone']}")
        if len(show) < len(zs):
            print(f"    ... {len(zs) - len(show)} more, use --list-all")
        raise SystemExit(0)

    if "--all" in sys.argv:
        done, failed, removed, left = 0, [], [], []
        art_map = approved_art()
        for r, z in zs:
            try:
                res = build_one(r, z, art_map)
                removed += [f"{r} / {z['zone']} ({k})" for k, (_, st) in res.items()
                            if "picture removed" in st]
                left += [f"{r} / {z['zone']} ({k}: {st.split(' item(s)')[0].split(', ')[-1]})"
                         for k, (_, st) in res.items() if "left for the zone page" in st]
                done += 1
            except SystemExit as e:
                failed.append(f"{r} / {z['zone']}: {e}")
        print(f"  {done}/{len(zs)} zones built for both surfaces")
        with_art = sum(1 for r, z in zs if (r, z["zone"]) in art_map)
        print(f"  {with_art} zones have an approved picture; "
              f"{len(zs) - with_art} are text only")
        if removed:
            print(f"  {len(removed)} card(s) fell back to text only, checklist too long:")
            for x in removed:
                print(f"    {x}")
        if left:
            print(f"  {len(left)} card(s) show '+ N more' and leave trailing items for the zone page:")
            for x in left:
                print(f"    {x}")
        if failed:
            print("  failed:")
            for f in failed:
                print(f"    {f}")
            raise SystemExit(1)
        raise SystemExit(0)

    want = sys.argv[sys.argv.index("--zone") + 1] if "--zone" in sys.argv else None
    if want is None:
        raise SystemExit("pass --zone NAME, --list, or --all")
    room_want = sys.argv[sys.argv.index("--room") + 1] if "--room" in sys.argv else None
    cands = [(r, z) for r, z in zs if z["zone"] == want
             and (room_want is None or r == room_want)]
    if len(cands) > 1:
        raise SystemExit("%r exists in %s. Pass --room to say which."
                          % (want, " and ".join(r for r, _ in cands)))
    if not cands:
        raise SystemExit("no zone named %r. %d zones are available; run --list-all"
                          % (want, len(zs)))
    r, z = cands[0]
    paths = build_one(r, z)
    for label, (p, steps) in paths.items():
        w, h = png_dims(p)
        print(f"  {label}: {p} ({w}x{h}, {os.path.getsize(p)//1024} KB) {steps}")
