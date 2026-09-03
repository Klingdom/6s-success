#!/usr/bin/env python3
"""
The Zone Reset video: fully typographic, so all 114 zones are buildable.

WHY TYPOGRAPHIC RATHER THAN PHOTOGRAPHIC
----------------------------------------
109 of the 114 micro zones have no photograph and there is no stock library on
this machine. A photo led format would therefore reuse thirteen pictures
across a hundred and fourteen videos, which is precisely the generated filler
worth avoiding. A format built from type needs no imagery at all, so the
constraint chooses the format rather than limiting it.

The script comes from content/manual/source/content.json, which holds all 114
zones with their purpose, what done looks like, the six passes and the call.
Every word on screen is drawn from that file. Nothing is written to fill a
beat.

WHY CHROMIUM RATHER THAN LIBASS
-------------------------------
The brand's fonts are woff2 and libass cannot read them, nor draw a rounded
chip behind an active word. Beats are therefore composed as HTML in the site's
own type and screenshotted by headless Edge, which is the same engine that
already renders the card fronts.

Rendering every frame that way would mean 720 screenshots a video. Instead
each beat is one still and ffmpeg holds it, which matches the format anyway:
hard cuts, no fades, words that appear and stay.

Run:  python ops/video_zone.py --list
      python ops/video_zone.py --zone "Landing Zone"
"""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(ROOT, "build", "video",
                   "zones-16x9" if "--wide" in sys.argv else "zones")
FRAMES = os.path.join(ROOT, "build", "video", "_frames")

# Vertical is the default because Shorts, Reels and TikTok are where a two
# minute instructional clip actually gets watched. --wide renders the same
# beats at 1920x1080 for YouTube proper, into a separate directory so the two
# cuts never overwrite each other.
WIDE = "--wide" in sys.argv
W, H = (1920, 1080) if WIDE else (1080, 1920)
FPS = 30

INK, PAPER, ACCENT = "#2B2622", "#F7F2E9", "#BC4B2A"
DEEP, HONEY, LINE = "#22323C", "#DDA63A", "#E2D8C4"
SIX = [("Sort", "#BC4B2A"), ("Straighten", "#DDA63A"), ("Shine", "#4E7A57"),
       ("Safety", "#CB4B36"), ("Standardize", "#3C5A6B"), ("Sustain", "#6E5B8B")]


def browser() -> tuple:
    """Edge on Phil's own machine, the sandbox's pre-installed Chromium
    otherwise. Unlike the card and book pipelines, this one needs no Desktop
    source art at all: every word comes from content.json, already committed,
    and the brand fonts are already under site/assets/fonts. So the only
    reason this tool could not run in the cloud sandbox was that it never
    looked for a browser there, the same gap ops/browser.py's find_browser()
    was already written to close for the test suite.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import browser as B
    found = B.find_browser()
    if not found:
        raise SystemExit("no Chromium browser found")
    return found


def zones() -> list:
    d = json.load(io.open(CONTENT, encoding="utf-8"))
    rooms = d["rooms"] if isinstance(d, dict) and "rooms" in d else d
    return [(r["room"], z) for r in rooms for z in r["zones"]]


def _slug(t: str) -> str:
    return t.lower().replace(" ", "-").replace(",", "").replace("/", "-")


def zone_slug(room: str, zone: str) -> str:
    """The one filename stem every zone-video writer and reader must agree
    on. Room first, because zone names repeat across rooms (three pairs
    collide on the zone name alone): naming by zone alone gave 111 files
    for 114 zones, with the second of each colliding pair unrenderable.
    Previously reimplemented separately in video_narrated.py (behind a
    `hasattr(vz, "_slug")` check that was always False, since the original
    `_slug` only ever existed inside `if __name__ == "__main__":` and so
    was never a real module attribute on import) and a third time in
    render_all_narrated.py. All three agreed only because no current room
    or zone name contains "/" or ",": the same single-source-of-truth gap
    that caused the YouTube metadata slug mismatch (backlog 3.10).
    """
    return "%s--%s" % (_slug(room), _slug(zone))


FONTS = os.path.join(ROOT, "site", "assets", "fonts").replace(os.sep, "/")

SHELL = """<!doctype html><meta charset="utf-8"><style>
@font-face{{font-family:Fraunces;src:url('file:///{fonts}/Fraunces-600-normal.woff2')format('woff2');font-weight:600}}
@font-face{{font-family:Fraunces;src:url('file:///{fonts}/Fraunces-400-normal.woff2')format('woff2');font-weight:400}}
@font-face{{font-family:Inter;src:url('file:///{fonts}/Inter-600-normal.woff2')format('woff2');font-weight:600}}
@font-face{{font-family:Inter;src:url('file:///{fonts}/Inter-700-normal.woff2')format('woff2');font-weight:700}}
@font-face{{font-family:Newsreader;src:url('file:///{fonts}/Newsreader-400-italic.woff2')format('woff2');font-style:italic}}
*{{box-sizing:border-box;margin:0}}
html,body{{width:{w}px;height:{h}px;overflow:hidden}}
/* Centred in the safe stage rather than pinned to the top. Flex column with
   no justification left every beat hugging the ceiling with six hundred
   pixels of empty below it, which reads as a slide that failed to load. */
body{{background:{bg};color:{fg};font-family:Inter,Arial,sans-serif;
  display:flex;flex-direction:column;justify-content:center;
  padding:300px 84px 470px}}
.eyebrow{{font-size:34px;font-weight:700;letter-spacing:.18em;
  text-transform:uppercase;color:{eyebrow};margin-bottom:34px}}
h1{{font-family:Fraunces,Georgia,serif;font-weight:600;font-size:92px;
  line-height:1.06;letter-spacing:-.02em}}
h2{{font-family:Fraunces,Georgia,serif;font-weight:600;font-size:74px;
  line-height:1.08;letter-spacing:-.015em;margin-bottom:40px}}
.chip{{display:inline-block;background:{accent};color:{paper};
  border-radius:10px;padding:6px 14px}}
ul{{list-style:none;padding:0;display:flex;flex-direction:column;gap:26px}}
li{{font-size:46px;line-height:1.3;display:flex;gap:22px;align-items:flex-start}}
li b{{flex:0 0 54px;height:54px;border-radius:50%;background:{accent};
  color:{paper};font:700 28px/54px Inter;text-align:center}}
.band{{background:{honey};color:{ink};font-weight:700;font-size:46px;
  padding:26px 34px;border-radius:14px;letter-spacing:.02em}}
.spine{{display:flex;gap:10px;margin-bottom:56px}}
.spine i{{flex:1;height:12px;border-radius:99px;background:#ffffff22}}
.instr{{font-family:Fraunces,Georgia,serif;font-weight:600;font-size:62px;
  line-height:1.16;letter-spacing:-.012em}}
.std{{font-family:Newsreader,Georgia,serif;font-style:italic;font-size:56px;
  line-height:1.3}}
.rule{{height:5px;background:{honey};width:180px;margin:0 0 40px}}
.trig{{font:700 44px/1.35 Inter;letter-spacing:.01em}}
.foot{{position:absolute;left:84px;bottom:360px;font:600 30px/1 Inter;letter-spacing:.18em;
  text-transform:uppercase;color:{footer}}}
</style><body>{body}</body>"""


def shot(exe: str, extra_args: list, html: str, png: str) -> None:
    with tempfile.TemporaryDirectory() as prof:
        f = png.replace(".png", ".html")
        io.open(f, "w", encoding="utf-8", newline="").write(html)
        subprocess.run([exe, "--headless=new", "--disable-gpu",
                        "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--user-data-dir={prof}", f"--window-size={W},{H}",
                        "--virtual-time-budget=6000", f"--screenshot={png}",
                        *extra_args,
                        "file:///" + os.path.abspath(f).replace(os.sep, "/")],
                       capture_output=True, timeout=90)
        os.remove(f)


def page(body: str, dark: bool = False) -> str:
    return SHELL.format(
        fonts=FONTS, w=W, h=H,
        bg=DEEP if dark else PAPER, fg=PAPER if dark else INK,
        eyebrow=HONEY if dark else ACCENT, accent=ACCENT, paper=PAPER,
        ink=INK, honey=HONEY, footer="#ffffff55" if dark else "#8C8478",
        body=body)


def spine(active: int) -> str:
    bars = "".join(
        f'<i style="background:{c if i <= active else "#00000018"}"></i>'
        for i, (_n, c) in enumerate(SIX))
    return f'<div class="spine">{bars}</div>'


def words(text: str, upto: int) -> str:
    """Words appear and stay. The active one takes the chip."""
    ws = text.split()
    out = []
    for i, w in enumerate(ws):
        if i < upto:
            out.append(w)
        elif i == upto:
            out.append(f'<span class="chip">{w}</span>')
        else:
            break
    return " ".join(out)


def beats(room: str, z: dict) -> list:
    """(seconds, html, dark). Every word comes from content.json."""
    name = z["zone"]
    # The real shapes in content.json, checked rather than assumed. My first
    # version treated done_looks_like as a list and the_call as a string; the
    # first is one sentence and the second is a dict with a title and a text.
    purpose = str(z.get("purpose") or "").strip()
    session = str(z.get("session") or "").strip()

    # One long sentence of clauses. Split it into the two to four things a
    # person can actually check, because a wall of text is not a video beat.
    raw = str(z.get("done_looks_like") or "").strip().rstrip(".")
    parts = [c.strip() for c in re.split(r",(?![^(]*\))| and (?=\w+ \w+)", raw)
             if c.strip()]
    done = [c[0].upper() + c[1:] for c in parts if len(c.split()) >= 3][:4]

    call_d = z.get("the_call") or {}
    if isinstance(call_d, dict):
        call_title = str(call_d.get("title") or "").strip().strip("'\"")
        call = str(call_d.get("text") or "").strip().strip("'\"")
    else:
        call_title, call = "", str(call_d).strip()
    passes = z.get("passes") or {}

    out = []
    # The hook is the zone's own purpose, which is a specific claim about a
    # specific place rather than a generic promise.
    out.append((3.2, page(
        f'<p class="eyebrow">{room}</p><h1>{name}</h1>'
        f'<p style="font-size:46px;line-height:1.35;margin-top:44px;'
        f'color:#ffffffcc">{purpose}</p>'
        f'<p class="foot">6S Success</p>', dark=True), True))

    if done:
        items = "".join(f"<li><b>{i+1}</b><span>{d}</span></li>"
                        for i, d in enumerate(done))
        out.append((4.6, page(
            f'<p class="eyebrow">What done looks like</p>'
            f'<ul>{items}</ul><p class="foot">6S Success</p>'), False))

    if session:
        out.append((2.2, page(
            f'<p class="eyebrow">One session</p>'
            f'<h2>{name}</h2><p class="band">{session}</p>'
            f'<p class="foot">6S Success</p>'), False))

    # Three passes, in method order, each with the six S spine filling in.
    order = ["sort", "straighten", "shine", "safety", "standardize", "sustain"]
    shown = 0
    for i, key in enumerate(order):
        text = passes.get(key)
        if not text or shown >= 3:
            continue
        text = text.strip()
        if len(text.split()) > 26:
            text = " ".join(text.split()[:26]) + "."
        label = SIX[i][0]
        # Two stills per pass so the words build rather than appear at once.
        half = max(1, len(text.split()) // 2)
        for upto, secs in ((half, 1.9), (len(text.split()), 2.1)):
            out.append((secs, page(
                f'{spine(i)}<p class="eyebrow">{label}</p>'
                f'<p class="instr">{words(text, upto)}</p>'
                f'<p class="foot">6S Success</p>'), False))
        shown += 1

    if call:
        out.append((3.4, page(
            f'<div class="rule"></div><p class="eyebrow">The call</p>'
            f'<p class="std">{call}</p><p class="foot">6S Success</p>',
            dark=True), True))

    out.append((2.4, page(
        f'<h2>{name}</h2>'
        f'<p class="trig">The full reset, free at<br>6s-success.com</p>'
        f'<p class="foot">6S Success</p>', dark=True), True))
    return out


def build(room: str, z: dict, out_path: str) -> str:
    exe, extra_args = browser()
    os.makedirs(FRAMES, exist_ok=True)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    bs = beats(room, z)
    listing, pngs = [], []
    for i, (secs, html, _dark) in enumerate(bs):
        png = os.path.join(FRAMES, f"b{i:03d}.png")
        shot(exe, extra_args, html, png)
        if not os.path.exists(png):
            raise SystemExit(f"beat {i} did not render")
        pngs.append(png)
        listing.append(f"file '{png.replace(os.sep, '/')}'\nduration {secs}")
    listing.append(f"file '{pngs[-1].replace(os.sep, '/')}'")

    lst = os.path.join(FRAMES, "list.txt")
    io.open(lst, "w", encoding="utf-8", newline="").write("\n".join(listing))

    # A silent audio track, because some platforms flag a missing stream.
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
           "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
           "-vf", f"scale={W}:{H},fps={FPS},format=yuv420p",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-c:a", "aac", "-b:a", "96k", "-shortest",
           "-movflags", "+faststart", out_path]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit("ffmpeg failed:\n" + p.stderr[-1200:])
    for f in pngs:
        os.remove(f)
    return out_path


if __name__ == "__main__":
    zs = zones()
    if "--list" in sys.argv or "--list-all" in sys.argv:
        print(f"  {len(zs)} zones")
        # --list shows a preview. A caller that needs to drive every zone must
        # ask for every zone, because a truncated list that announces the full
        # count reads as complete and is not.
        show = zs if "--list-all" in sys.argv else zs[:6]
        for r, z in show:
            print(f"    {r:18} {z['zone']}")
        if len(show) < len(zs):
            print(f"    ... {len(zs) - len(show)} more, use --list-all")
        raise SystemExit(0)

    want = sys.argv[sys.argv.index("--zone") + 1] if "--zone" in sys.argv else None
    # Falling back to zs[0] on an unmatched name was a silent wrong answer:
    # a batch that passed a malformed name rendered the Landing Zone 114 times
    # and every call returned zero, so it reported 114 successes and produced
    # one file. A name that matches nothing is an error, not a default.
    if want is None:
        hit = zs[0]
    else:
        room_want = (sys.argv[sys.argv.index("--room") + 1]
                     if "--room" in sys.argv else None)
        cands = [(r, z) for r, z in zs if z["zone"] == want
                 and (room_want is None or r == room_want)]
        if len(cands) > 1:
            raise SystemExit(
                "%r exists in %s. Pass --room to say which."
                % (want, " and ".join(r for r, _ in cands)))
        hit = cands[0] if cands else None
        if hit is None:
            raise SystemExit(
                "no zone named %r. %d zones are available; run --list-all"
                % (want, len(zs)))
    # Room first, because zone names repeat across rooms. Three pairs collide
    # on the zone name alone: Dresser Drawers in Primary and Kids Bedroom,
    # Shower or Tub and Toilet Area in Primary and Guest Bathroom. Naming by
    # zone alone gave 111 files for 114 zones, so three rooms were showing
    # another room's video, and the second of each pair could never be
    # rendered at all because --zone matches the first.
    slug = zone_slug(hit[0], hit[1]["zone"])
    out = os.path.join(OUT, f"{slug}.mp4")
    build(hit[0], hit[1], out)

    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import video as V
    d = V.probe(out)
    print(f"  {hit[0]} / {hit[1]['zone']}")
    print(f"  {d.get('width')}x{d.get('height')} "
          f"{float(d.get('duration', 0)):.1f}s "
          f"{int(d.get('size', 0))//1024} KB")
    print(f"  problems: {V.verify(out, float(d.get('duration', 0))) or 'none'}")
