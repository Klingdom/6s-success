#!/usr/bin/env python3
"""
Static save-and-share cards for Pinterest and Instagram, one per zone.

WHY THIS EXISTS
----------------
GOALS.md names the constraint plainly: 47 sessions in 30 days, one of them
from a search engine. Every channel that could change that (YouTube, TikTok,
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

PIN_DIR = os.path.join(ROOT, "build", "social", "pinterest")
IG_DIR = os.path.join(ROOT, "build", "social", "instagram")

# 2:3, Pinterest's documented standard pin ratio.
PIN_W, PIN_H = 1000, 1500
# 4:5, Instagram's tallest allowed feed ratio, the most screen a feed post can claim.
IG_W, IG_H = 1080, 1350

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


def done_items(z: dict) -> list:
    """Same split video_zone.py's beats() already proved correct against the
    real content.json shapes: one long sentence of clauses into two to four
    checkable things, not a wall of text on a card meant to be read at a
    glance while scrolling.
    """
    raw = str(z.get("done_looks_like") or "").strip().rstrip(".")
    parts = [c.strip() for c in re.split(r",(?![^(]*\))| and (?=\w+ \w+)", raw)
             if c.strip()]
    return [c[0].upper() + c[1:] for c in parts if len(c.split()) >= 3][:4]


def card_html(room: str, z: dict, w: int, h: int) -> str:
    name = z["zone"]
    purpose = str(z.get("purpose") or "").strip()
    items = done_items(z)
    li = "".join(f"<li><b>{i+1}</b><span>{d}</span></li>" for i, d in enumerate(items))
    body = (
        f'<p class="eyebrow">{room} &middot; free zone reset</p>'
        f'<h1>{name}</h1>'
        f'<div class="bar"></div>'
        f'<p class="sub">{purpose}</p>'
        f'<ul>{li}</ul>'
        f'<div class="foot"><span class="brand">6S Success</span>'
        f'<span class="cta">6s-success.com</span></div>'
    )
    return SHELL.format(fonts=VZ.FONTS, w=w, h=h, paper=PAPER, ink=INK,
                         accent=ACCENT, honey=HONEY, footer=FOOTER, body=body)


def shot(exe: str, extra_args: list, html: str, png: str, w: int, h: int) -> None:
    with tempfile.TemporaryDirectory() as prof:
        f = png.replace(".png", ".html")
        io.open(f, "w", encoding="utf-8", newline="").write(html)
        subprocess.run([exe, "--headless=new", "--disable-gpu",
                        "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--user-data-dir={prof}", f"--window-size={w},{h}",
                        "--virtual-time-budget=6000", f"--screenshot={png}",
                        *extra_args,
                        "file:///" + os.path.abspath(f).replace(os.sep, "/")],
                       capture_output=True, timeout=90)
        os.remove(f)


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


def build_one(room: str, z: dict) -> dict:
    exe, extra_args = VZ.browser()
    os.makedirs(PIN_DIR, exist_ok=True)
    os.makedirs(IG_DIR, exist_ok=True)
    slug = f"{VZ.zone_slug(room, z['zone'])}.png"
    out = {}
    for label, w, h, d in (("pinterest", PIN_W, PIN_H, PIN_DIR),
                            ("instagram", IG_W, IG_H, IG_DIR)):
        png = os.path.join(d, slug)
        shot(exe, extra_args, card_html(room, z, w, h), png, w, h)
        if not os.path.exists(png):
            raise SystemExit(f"{label} card did not render for {room}/{z['zone']}")
        got = png_dims(png)
        if got != (w, h):
            raise SystemExit(f"{label} card for {room}/{z['zone']} rendered at "
                              f"{got}, not the required {(w, h)}")
        out[label] = png
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
        done, failed = 0, []
        for r, z in zs:
            try:
                build_one(r, z)
                done += 1
            except SystemExit as e:
                failed.append(f"{r} / {z['zone']}: {e}")
        print(f"  {done}/{len(zs)} zones built for both surfaces")
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
    for label, p in paths.items():
        w, h = png_dims(p)
        print(f"  {label}: {p} ({w}x{h}, {os.path.getsize(p)//1024} KB)")
