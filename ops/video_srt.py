"""Write an SRT sidecar for every zone video.

The zone videos render HTML slides in a headless browser, so their words are
baked into the pixels. That reads fine and is invisible to everything that
matters for reach: YouTube cannot index it, a screen reader cannot speak it, a
translation cannot touch it, and a deaf viewer gets nothing a hearing viewer
does not, which is the one case burned-in text is supposed to cover.

The timings are not guessed. ops/video_zone.py's beats() returns the exact
(seconds, html) pairs the video is assembled from, so each caption starts where
its beat starts and ends where it ends, by construction.

    python ops/video_srt.py                 all zones
    python ops/video_srt.py --zone "Landing Zone" --room Entryway
    python ops/video_srt.py --check         report coverage, write nothing
"""
from __future__ import annotations

import html as htmllib
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))
OUT = os.path.join(ROOT, "build", "video", "zones")

TAG = re.compile(r"<[^>]+>")
WS = re.compile(r"\s+")
# The brand mark is painted on every slide. It is a watermark, not speech, and
# repeating it in every caption is noise to a reader who can already see it.
BRAND = re.compile(r"\s*6S Success\s*$", re.I)

LINE_CHARS = 42     # one comfortable caption line
MAX_CHARS = 84      # two of them; longer than this is a wall over the picture


def visible_text(fragment: str) -> str:
    """The words a viewer actually sees in one beat, in reading order."""
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", fragment)
    # A block boundary is a line break to a reader, so keep it as a space
    # rather than letting two words run together into one.
    s = re.sub(r"(?i)</(p|div|h[1-6]|li|section)\s*>", " ", s)
    s = re.sub(r"(?i)<br\s*/?>", " ", s)
    s = TAG.sub(" ", s)
    s = htmllib.unescape(s)
    return WS.sub(" ", s).strip()


def stamp(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    sec, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, sec, ms)


def wrap_two_lines(text: str) -> str:
    if len(text) <= LINE_CHARS:
        return text
    lines, cur = [], ""
    for w in text.split(" "):
        if cur and len(cur) + 1 + len(w) > LINE_CHARS:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    if len(lines) <= 2:
        return chr(10).join(lines)
    return chr(10).join([lines[0], " ".join(lines[1:])])


def split_beat(text: str) -> list:
    """One beat can hold a whole checklist. Split it into readable cues.

    A single cue carrying an entire "what done looks like" list is a wall of
    text over the picture it describes, and it sits there for the whole beat
    whether the viewer has finished reading or not.
    """
    if len(text) <= MAX_CHARS:
        return [text]
    # Numbered markers are the natural seam, because that is how the slide is
    # laid out. Fall back to sentence ends, then to a hard word split.
    parts = re.split(r"\s+(?=\d+\s+[A-Z])", text)
    if len(parts) == 1:
        parts = re.split(r"(?<=[.!?])\s+", text)
    out = []
    for p in parts:
        p = p.strip()
        while len(p) > MAX_CHARS:
            cut = p.rfind(" ", 0, MAX_CHARS)
            cut = cut if cut > 0 else MAX_CHARS
            out.append(p[:cut].strip())
            p = p[cut:].strip()
        if p:
            out.append(p)
    return out or [text]


def srt_for(room: str, z: dict) -> str:
    import video_zone

    out, t, n = [], 0.0, 0
    for secs, fragment, _dark in video_zone.beats(room, z):
        text = BRAND.sub("", visible_text(fragment)).strip()
        start, end = t, t + float(secs)
        t = end
        if not text:
            continue
        cues = split_beat(text)
        span = (end - start) / len(cues)
        for i, cue in enumerate(cues):
            n += 1
            out.append("%d%s%s --> %s%s%s%s" % (
                n, chr(10),
                stamp(start + i * span), stamp(start + (i + 1) * span),
                chr(10), wrap_two_lines(cue), chr(10)))
    return chr(10).join(out)


def slug(room: str, zone: str) -> str:
    def one(t):
        return t.lower().replace(" ", "-").replace(",", "").replace("/", "-")
    return "%s--%s" % (one(room), one(zone))


def main() -> int:
    import video_zone

    if "--check" in sys.argv:
        have = len([f for f in os.listdir(OUT) if f.endswith(".srt")]) \
            if os.path.isdir(OUT) else 0
        mp4 = len([f for f in os.listdir(OUT) if f.endswith(".mp4")]) \
            if os.path.isdir(OUT) else 0
        print("  videos: %d, srt sidecars: %d" % (mp4, have))
        return 1 if have < mp4 else 0

    want_zone = (sys.argv[sys.argv.index("--zone") + 1]
                 if "--zone" in sys.argv else None)
    want_room = (sys.argv[sys.argv.index("--room") + 1]
                 if "--room" in sys.argv else None)

    made, empty = 0, []
    for room, z in video_zone.zones():
        if want_zone and z["zone"] != want_zone:
            continue
        if want_room and room != want_room:
            continue
        body = srt_for(room, z)
        if not body.strip():
            # An empty caption file is worse than none: it tells a player there
            # are captions and then shows nothing.
            empty.append(z["zone"])
            continue
        io.open(os.path.join(OUT, slug(room, z["zone"]) + ".srt"),
                "w", encoding="utf-8", newline="").write(body)
        made += 1

    print("  srt written : %d" % made)
    if empty:
        print("  no caption text for %d zone(s): %s" % (len(empty), empty[:4]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
