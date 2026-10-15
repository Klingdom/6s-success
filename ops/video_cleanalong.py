#!/usr/bin/env python3
"""Clean-along zone video: what a micro zone is, before and after, then one
pausable step per surface and item, from the zone's own shine_detail.

WHY THIS EXISTS (Phil, 2026-10-14: "those videos kind of suck")
------------------------------------------------------------------
The published format (ops/video_zone.py + ops/video_narrated.py) reads the
six passes aloud as paragraphs over text slides. It never used the richest
thing the corpus holds for a viewer standing in the room: shine_detail, which
names every surface and item in the zone (the mirror, the switch plate, the
tray, the charging cable, the floor behind the legs) with an exact method for
each. Phil asked for three things, and this is built around them:

  1. Explain micro zones.        -> opening beats: what one is, where this one sits
  2. Before and after pictures.  -> a before/after beat, ONLY from a real pair
  3. Simple, pausable steps on   -> one slide per surface; the whole method sits
     how to clean each area and     on screen as short numbered sub-steps for the
     each item in it                full time it is spoken, so pausing on any
                                    frame shows the complete step. YouTube
                                    chapters are written for every step.

BEFORE AND AFTER: WHAT THIS WILL NOT DO
----------------------------------------
CLAUDE.md section 8 forbids fake before/after results. There is no "before"
image anywhere in this repository, and the local image model cannot draw the
micro zone reliably (LEARNINGS.md LRN-0012). So the before/after beat renders
only when a pair exists at

    build/before-after/<page-slug>/before.(jpg|png)
    build/before-after/<page-slug>/after.(jpg|png)
    build/before-after/<page-slug>/source.txt   "real" or "illustration"

and it prints the source on screen: "Real photos" or "Illustration, not a real
home". With no pair, the beat is left out and the build says so. It is never
filled with the single finished-state hero dressed up as a result.

Every instruction word comes from content.json. The only authored copy is the
micro zone definition, which is the site's own (articles/what-is-a-micro-zone).

    python ops/video_cleanalong.py --zone "Landing Zone" --room Entryway
    python ops/video_cleanalong.py --zone "Landing Zone" --room Entryway --frames
        (--frames renders the slides to PNG only: no voice, no video)
"""
from __future__ import annotations

import html as H
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))
import video_zone as vz            # noqa: E402

# This cut is always YouTube 16:9, never the vertical default. video_zone
# decides WIDE/W/H from "--wide" in sys.argv, but only once, at its own
# import time; appending to sys.argv here used to rely on this module
# importing video_zone before anything else does, in whatever process runs
# it. In a shared process (pytest collects every ops/tests/*.py into one
# interpreter) an earlier narrow import of video_zone caches WIDE=False
# first, so appending "--wide" afterward does nothing, and vz.page()/
# vz.shot() silently render portrait frames into a video this module then
# stretches to 1920x1080. Proved directly: importing video_zone narrow,
# then video_cleanalong, left WIDE False. Setting the module's own
# attributes here works regardless of who imported video_zone first, and
# leaves sys.argv untouched for every other module in the same process.
vz.WIDE = True
vz.W, vz.H = 1920, 1080

OUT = os.path.join(ROOT, "build", "video", "cleanalong")
WORK = os.path.join(ROOT, "build", "video", "_cleanalong")
PAIRS = os.path.join(ROOT, "build", "before-after")
NAME_MAP = json.load(io.open(os.path.join(ROOT, "ops", "zone-name-map.json"),
                             encoding="utf-8"))
TAIL = 0.6
PAUSE_HOLD = 1.6   # extra silent seconds on each step, a beat to start working


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", (t or "").lower()).strip("-")


def display(room, zone):
    return NAME_MAP.get(f"{room}|{zone}", zone)


def page_slug(room, zone):
    return "%s-%s" % (slug(room), slug(display(room, zone)))


def e(t):
    return H.escape(str(t or ""), quote=False)


def sentences(text):
    """Sentences, then each compound sentence split at ', then' and ';' so a
    sub-step carries one action. Words are kept; only the joint changes."""
    out = []
    for p in re.split(r"(?<=[.!?])\s+(?=[A-Z])", (text or "").strip()):
        p = p.strip()
        if not p:
            continue
        for q in re.split(r",\s+then\s+|;\s+", p):
            q = q.strip().rstrip(",")
            if not q:
                continue
            q = q[:1].upper() + q[1:]
            if q[-1] not in ".!?":
                q += "."
            out.append(q)
    return out


def cap(t):
    t = (t or "").strip()
    return t[:1].upper() + t[1:]


CSS = """<style>
body{justify-content:flex-start!important;padding:70px 110px 90px!important}
.top{display:flex;justify-content:space-between;align-items:center;
  font:700 26px/1 Inter;letter-spacing:.16em;text-transform:uppercase;
  color:#8C8478;margin-bottom:34px}
.top .n{color:#BC4B2A}
.dots{display:flex;gap:8px;margin-bottom:38px}
.dots i{flex:1;height:10px;border-radius:99px;background:#00000014}
.dots i.d{background:#BC4B2A}
.dots i.c{background:#DDA63A}
.t{font-family:Fraunces,Georgia,serif;font-weight:600;font-size:66px;
  line-height:1.08;letter-spacing:-.015em;margin-bottom:34px}
ol{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:20px}
ol li{display:flex;gap:22px;align-items:flex-start;font-size:var(--fs,38px);line-height:1.32}
ol li b{flex:0 0 52px;height:52px;border-radius:50%;background:#2B2622;color:#F7F2E9;
  font:700 26px/52px Inter;text-align:center;margin-top:2px}
.pause{position:absolute;left:110px;right:110px;bottom:56px;display:flex;
  align-items:center;gap:18px;font:700 30px/1 Inter;color:#2B2622;
  background:#DDA63A;border-radius:14px;padding:20px 26px}
.pause s{display:inline-block;width:26px;height:30px;border-left:9px solid #2B2622;
  border-right:9px solid #2B2622;text-decoration:none;flex:0 0 26px}
.cols{columns:2;column-gap:70px}
.cols li{break-inside:avoid;margin-bottom:20px}
.ba{display:flex;gap:40px;margin-top:10px}
.ba figure{flex:1;margin:0}
.ba img{width:100%;height:600px;object-fit:cover;border-radius:18px}
.ba figcaption{font:700 30px/1 Inter;letter-spacing:.14em;text-transform:uppercase;
  margin-top:16px;color:#BC4B2A}
.src{font:600 26px/1.3 Inter;color:#8C8478;margin-top:22px}
.zl{display:flex;flex-wrap:wrap;gap:14px;margin-top:38px}
.zl span{font-size:28px;font-weight:600;padding:11px 19px;border-radius:999px;
  border:2px solid #C9BFAE;opacity:.75}
.zl span.on{background:#BC4B2A;border-color:#BC4B2A;color:#F7F2E9;opacity:1}
.big{font-family:Fraunces,Georgia,serif;font-weight:600;font-size:92px;line-height:1.05}
.lede{font-family:Newsreader,Georgia,serif;font-style:italic;font-size:48px;line-height:1.3;margin-top:30px}
</style>"""


def frame(body, dark=False):
    return vz.page(CSS + body, dark=dark)


def topbar(room, name, right):
    return ('<div class="top"><span>%s &middot; %s</span><span class="n">%s</span></div>'
            % (e(room), e(name), right))


def dots(n, k):
    return '<div class="dots">%s</div>' % "".join(
        '<i class="%s"></i>' % ("d" if i < k else "c" if i == k else "")
        for i in range(n))


def find_pair(ps):
    d = os.path.join(PAIRS, ps)
    if not os.path.isdir(d):
        return None
    def pick(stem):
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            p = os.path.join(d, stem + ext)
            if os.path.isfile(p):
                return p
        return None
    b, a = pick("before"), pick("after")
    src_f = os.path.join(d, "source.txt")
    src = io.open(src_f, encoding="utf-8").read().strip().lower() if os.path.isfile(src_f) else ""
    if not (b and a) or src not in ("real", "illustration"):
        return None
    return b, a, src


def beats(room, z):
    """[(html, narration, chapter or None, extra_hold_seconds)]."""
    name = display(room, z["zone"])
    sd = z.get("shine_detail") or {}
    surfaces = [s for s in (sd.get("surfaces") or []) if s.get("surface") and s.get("method")]
    if not surfaces:
        raise SystemExit("%s / %s has no shine_detail surfaces" % (room, z["zone"]))
    sibs = vz.siblings(room)
    nsib = len(sibs)
    out = []

    # 1. Title.
    out.append((frame(
        '<p class="eyebrow">%s &middot; clean-along</p><p class="big">How to clean %s</p>'
        '<p class="lede">%d steps, one surface at a time. Pause on any step.</p>'
        % (e(room), e(name), len(surfaces)), dark=True),
        "How to clean %s, in the %s. %d steps, one surface at a time. Pause on any step."
        % (name, room.lower(), len(surfaces)), "How to clean %s" % name, 0))

    # 2. What a micro zone is, and where this one sits.
    chips = "".join('<span class="%s">%s</span>'
                    % ("on" if s == z["zone"] else "", e(display(room, s))) for s in sibs)
    purpose = str(z.get("purpose") or "").strip()
    out.append((frame(
        '<p class="eyebrow">What a micro zone is</p>'
        '<p class="t">One small place with one job.</p>'
        '<p class="lede" style="margin-top:0">%s</p>'
        '<div class="zl">%s</div>'
        '<p class="lede" style="font-size:40px;margin-top:56px">Small enough to finish in one '
        'session. Specific enough to keep finished.</p>' % (e(purpose), chips)),
        "This is a micro zone: one small place with one job. %s It is one of %d micro "
        "zones in the %s. You finish it in a single session, then move to the next."
        % (purpose, nsib, room.lower()), "What a micro zone is", 0))

    # 3. Before and after, only from a real pair.
    pair = find_pair(page_slug(room, z["zone"]))
    if pair:
        b, a, src = pair
        label = "Real photos" if src == "real" else "Illustration, not a real home"
        out.append((frame(
            '<p class="eyebrow">Before and after</p><div class="ba">'
            '<figure><img src="%s"><figcaption>Before</figcaption></figure>'
            '<figure><img src="%s"><figcaption>After</figcaption></figure></div>'
            '<p class="src">%s</p>' % (file_uri(b), file_uri(a), label)),
            "Before, and after." + ("" if src == "real" else " This is an illustration, not a real home."),
            "Before and after", 2.0))

    # 4. What you need. Pause to gather.
    kit = [re.sub(r"\s*\(not in this zone.s kit\)", "", p).strip()
           for p in (sd.get("products_used") or [])]
    kit = [k for k in kit if k]
    if kit:
        out.append((frame(
            topbar(room, name, "Before you start")
            + '<p class="t">Gather these first</p><ol>%s</ol>'
            '<div class="pause"><s></s>Pause here while you gather them</div>'
            % "".join("<li><b>%d</b><span>%s</span></li>" % (i + 1, e(k)) for i, k in enumerate(kit))),
            "Gather these first. %s. Pause here while you get them." % ", ".join(k.lower() for k in kit),
            "What you need", PAUSE_HOLD))

    # 5. The order.
    summ = str(sd.get("shine_summary") or "").strip()
    if summ:
        out.append((frame(topbar(room, name, "The order")
                          + '<p class="t">How this goes</p><p class="lede" style="margin-top:0">%s</p>' % e(summ)),
                    summ, None, 0))

    # 6. One step per surface or item. Everything on screen for the whole beat.
    n = len(surfaces)
    for k, s in enumerate(surfaces):
        title = cap(s["surface"])
        subs = sentences(s["method"])
        words = sum(len(x.split()) for x in subs)
        fs = "38px" if words <= 70 else "34px" if words <= 95 else "30px"
        items = "".join("<li><b>%d</b><span>%s</span></li>" % (i + 1, e(x)) for i, x in enumerate(subs))
        out.append((frame(
            topbar(room, name, "Step %d of %d" % (k + 1, n)) + dots(n, k)
            + '<p class="t">%s</p><ol style="--fs:%s">%s</ol>' % (e(title), fs, items)
            + '<div class="pause"><s></s>Pause until this one is done, then play</div>'),
            "Step %d. %s. %s" % (k + 1, title, " ".join(subs)),
            "Step %d: %s" % (k + 1, title), PAUSE_HOLD))

    # 7. Look for these while you clean.
    insp = [str(x).strip() for x in (sd.get("inspect_as_you_clean") or []) if str(x).strip()]
    if insp:
        shown = insp[:4]
        more = len(insp) - len(shown)
        extra = ('<p class="src">+ %d more on the zone page</p>' % more) if more else ""
        out.append((frame(
            topbar(room, name, "While you clean") + '<p class="t">Look for these</p>'
            + '<ol style="--fs:32px">%s</ol>' % "".join("<li><b>!</b><span>%s</span></li>" % e(x) for x in shown)
            + extra),
            "While you clean, look for these. " + " ".join(shown),
            "What to look for", 0))

    # 8. Done looks like.
    done = vz.done_items(z)
    if done:
        out.append((frame(
            topbar(room, name, "Done") + '<p class="t">Done looks like this</p>'
            + '<ol style="--fs:38px">%s</ol>' % "".join(
                "<li><b>%d</b><span>%s</span></li>" % (i + 1, e(d)) for i, d in enumerate(done[:6]))),
            "Done looks like this. " + ". ".join(d.rstrip(".") for d in done[:6]) + ".",
            "Done looks like this", 0))

    # 9. End card.
    ps = page_slug(room, z["zone"])
    out.append((frame(
        '<p class="eyebrow">The full guide, free</p><p class="big">%s</p>'
        '<p class="lede">6s-success.com/zones/%s</p>' % (e(name), e(ps)), dark=True),
        "The full guide for %s, with every step and the standard that keeps it, is free at "
        "six S success dot com." % name, None, 0))
    return out


def file_uri(p):
    return "file:///" + os.path.abspath(p).replace(os.sep, "/")


def chapters(durations, bs):
    """YouTube chapter list: first at 0:00, each at least 10 seconds."""
    t, rows = 0.0, []
    for (_mp3, d), (_h, _n, ch, extra) in zip(durations, bs):
        if ch:
            rows.append([t, ch])
        t += d + TAIL + extra
    # A chapter under 10 seconds is folded into the NEXT one, which starts
    # where the short one did. YouTube ignores the whole list if any chapter
    # is shorter than 10 seconds, so one short title card would cost them all.
    keep, carry = [], None
    for i, (start, ch) in enumerate(rows):
        end = rows[i + 1][0] if i + 1 < len(rows) else t
        begin = start if carry is None else carry
        if end - begin < 10 and i + 1 < len(rows):
            carry = begin
            continue
        keep.append((begin, ch))
        carry = None
    keep[0] = (0.0, keep[0][1])
    return "\n".join("%d:%02d %s" % (int(s) // 60, int(s) % 60, c) for s, c in keep) + "\n"


def ff(args, timeout=300):
    return subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + args,
                          capture_output=True, text=True, timeout=timeout)


def build(room, z, frames_only=False):
    import video_narrated as vn
    ps = page_slug(room, z["zone"])
    work = os.path.join(WORK, ps)
    os.makedirs(work, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    bs = beats(room, z)
    exe, extra = vz.browser()
    pngs = []
    for i, (html, _n, _c, _x) in enumerate(bs):
        png = os.path.join(work, "s%03d.png" % i)
        vz.shot(exe, extra, html, png)
        if not os.path.exists(png):
            raise SystemExit("slide %d did not render" % i)
        pngs.append(png)
    print("  %d slides rendered to %s" % (len(pngs), work))
    if not find_pair(ps):
        print("  before/after: no pair at build/before-after/%s/, beat left out" % ps)
    if frames_only:
        return work
    audio = vn.narrate([n for _h, n, _c, _x in bs], work)
    listing, padded = [], []
    for i, ((mp3, d), (_h, _n, _c, x)) in enumerate(zip(audio, bs)):
        listing.append("file '%s'\nduration %.3f" % (pngs[i].replace(os.sep, "/"), d + TAIL + x))
        p = os.path.join(work, "p%03d.mp3" % i)
        ff(["-i", mp3, "-af", "apad=pad_dur=%.3f" % (TAIL + x), "-c:a", "libmp3lame", p], 120)
        padded.append(p)
    listing.append("file '%s'" % pngs[-1].replace(os.sep, "/"))
    lst = os.path.join(work, "list.txt")
    io.open(lst, "w", encoding="utf-8", newline="").write("\n".join(listing))
    alist = os.path.join(work, "audio.txt")
    io.open(alist, "w", encoding="utf-8", newline="").write(
        "\n".join("file '%s'" % p.replace(os.sep, "/") for p in padded))
    voice = os.path.join(work, "voice.mp3")
    ff(["-f", "concat", "-safe", "0", "-i", alist, "-c", "copy", voice])
    out = os.path.join(OUT, ps + ".mp4")
    r = ff(["-f", "concat", "-safe", "0", "-i", lst, "-i", voice,
            "-vf", "scale=1920:1080,fps=30,format=yuv420p",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
            "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-shortest", out], 900)
    if not os.path.exists(out):
        raise SystemExit("ffmpeg produced nothing: %s" % r.stderr[-400:])
    held = [(m, d + x) for (m, d), (_h, _n, _c, x) in zip(audio, bs)]
    io.open(out[:-4] + ".srt", "w", encoding="utf-8", newline="").write(
        vn.srt_from(held, [n for _h, n, _c, _x in bs]))
    io.open(out[:-4] + ".chapters.txt", "w", encoding="utf-8", newline="").write(chapters(audio, bs))
    return out


def main():
    want_z = sys.argv[sys.argv.index("--zone") + 1] if "--zone" in sys.argv else None
    want_r = sys.argv[sys.argv.index("--room") + 1] if "--room" in sys.argv else None
    todo = [(r, z) for r, z in vz.zones()
            if (want_z is None or z["zone"] == want_z) and (want_r is None or r == want_r)]
    if not todo:
        print("  no zone matched")
        return 1
    if want_z is None and "--all" not in sys.argv:
        print("  name a --zone, or pass --all to build all %d" % len(todo))
        return 1
    import video_narrated as vn
    for room, z in todo:
        out = build(room, z, "--frames" in sys.argv)
        if out.endswith(".mp4"):
            print("  %-48s %6.1fs" % (os.path.basename(out), vn.probe_duration(out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
