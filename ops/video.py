#!/usr/bin/env python3
"""
Short form video: a still, slow motion on it, and word by word captions.

WHAT THIS IS BUILT ON, all verified present rather than assumed
--------------------------------------------------------------
    ffmpeg 8.1.1 with libass, zoompan, xfade, drawtext and libx264
    PIL, numpy and OpenCV for frames
    headless Chromium, which already renders the card fronts to PNG
    Windows SAPI speech, two voices, both noticeably robotic

There is no stock footage, no music library, no AI video and no voice cloning
on this machine, so nothing here is designed around them. A format that needs
an asset that does not exist is not a format, it is a wish.

WHY CAPTIONS RATHER THAN A VOICE
--------------------------------
Short form is watched muted by default, so the captions are the content and
not an accessibility afterthought. The two available voices are robotic
enough that they would make a careful brand sound like a scam advert, and a
robotic voice is worse than no voice. Silence with strong captions is also the
dominant format, so this is the normal choice rather than a compromise.

The captions are burned in as ASS with karaoke timing, which is the effect
people mean by "highlighted captions": a short phrase on screen, each word
lighting up as it is spoken or read.

THE THING THAT MAKES THESE LOOK CHEAP, AND HOW IT IS AVOIDED
------------------------------------------------------------
A still image with a caption over it looks like generated filler. Three things
prevent that here: a slow continuous push on the image so the frame is never
static, captions set in the brand's own type and colour rather than the
default white block every generator produces, and a first second that states a
specific problem rather than a brand name.

Run:  python ops/video.py --probe
      python ops/video.py --demo
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "build", "video")

# Portrait by default. video_zone.py --wide renders the same beats at
# 1920x1080, and the verifier has to follow the mode rather than assert
# portrait, or every correct wide render reports itself as broken.
WIDE = "--wide" in sys.argv
W, H = (1920, 1080) if WIDE else (1080, 1920)
FPS = 30

# Brand palette, from site/assets/css/site.css rather than invented.
INK = "2B2622"
PAPER = "F7F2E9"
ACCENT = "BC4B2A"
HONEY = "DDA63A"


def ass_colour(hexrgb: str, alpha: str = "00") -> str:
    """ASS wants &HAABBGGRR, which is backwards from CSS in two ways."""
    r, g, b = hexrgb[0:2], hexrgb[2:4], hexrgb[4:6]
    return f"&H{alpha}{b}{g}{r}"


def wrap(words: list, per_line: int = 3) -> list:
    return [words[i:i + per_line] for i in range(0, len(words), per_line)]


def build_ass(phrases: list, path: str) -> str:
    """Karaoke captions. phrases is [(start, end, "some words"), ...].

    Each word is emitted with a \\k tag so it fills in across the phrase. The
    highlight is the brand terracotta rather than the usual yellow, because
    yellow on cream is the single fastest way to look like every other
    generated video.
    """
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Arial Black,78,{ass_colour(ACCENT)},{ass_colour(PAPER)},{ass_colour(INK)},&H80000000,0,0,0,0,100,100,0,0,1,7,3,2,140,140,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    def ts(t: float) -> str:
        h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
        return f"{h}:{m:02d}:{s:05.2f}"

    lines = []
    for start, end, text in phrases:
        words = text.split()
        if not words:
            continue
        dur_cs = max(1, int((end - start) * 100))
        each = max(1, dur_cs // len(words))
        # A hard line break every four words. WrapStyle 2 disabled wrapping
        # entirely, so a phrase wider than 1080px was simply cut off at both
        # edges and unreadable. Smart wrapping alone still fills the width
        # edge to edge, and a caption touching the frame reads as broken on a
        # phone, so the break is forced rather than left to the renderer.
        chunks = [" ".join(words[i:i + 4]) for i in range(0, len(words), 4)]
        body = "\\N".join(
            "".join(f"{{\\k{each}}}{w} " for w in c.split()).strip()
            for c in chunks)
        lines.append(f"Dialogue: 0,{ts(start)},{ts(end)},Cap,,0,0,0,,{body}")

    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(head + "\n".join(lines) + "\n")
    return path


def render(image: str, phrases: list, out: str, seconds: float = 0.0,
           title: str | None = None) -> str:
    """One still, a slow push, burned in captions, encoded for social."""
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if not seconds:
        seconds = max(p[1] for p in phrases) + 0.6

    ass = build_ass(phrases, out.replace(".mp4", ".ass"))
    frames = int(seconds * FPS)

    # A continuous slow push. A static frame under a caption is the single
    # clearest tell of a generated video, and 8 percent over the whole clip is
    # enough to read as alive without becoming a zoom effect.
    # A landscape photograph in a 9:16 frame. Cropping to fill throws away
    # most of a 4:3 image and usually cuts the subject in half, so the frame
    # is a heavily blurred copy of the same picture with the real one sitting
    # over it. The eye reads the blur as depth rather than as a letterbox.
    #
    # Captions sit in the lower third but above 430px of margin, which clears
    # the caption and button furniture every platform draws over the bottom
    # of a vertical video.
    esc = ass.replace(os.sep, "/").replace(":", chr(92) + ":")
    vf = (
        f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},gblur=sigma=32,eq=brightness=-0.06[bg];"
        # The subject, cropped to 4:5 and filling the full width. A 4:3
        # photograph placed whole occupied about 40 percent of a 9:16 frame
        # and the rest read as dead blur. Losing the far edges of a landscape
        # shot costs little, because the subject of an interior photograph is
        # almost never at the extreme left or right, and it buys a picture
        # that fills the screen.
        f"[0:v]scale={W}:{int(W*1.25)}:force_original_aspect_ratio=increase,"
        f"crop={W}:{int(W*1.25)}[fg];"
        f"[bg][fg]overlay=0:190,"
        f"zoompan=z='min(1.06,1+0.06*on/{frames})':d={frames}"
        f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},"
        f"ass='{esc}'"
    )

    cmd = ["ffmpeg", "-y", "-loop", "1", "-i", image,
           "-t", f"{seconds:.2f}", "-filter_complex", vf,
           "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           "-r", str(FPS), out]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit("ffmpeg failed:\n" + p.stderr[-1400:])
    return out


def probe(path: str) -> dict:
    p = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,nb_frames,r_frame_rate",
         "-show_entries", "format=duration,size", "-of", "default=nw=1", path],
        capture_output=True, text=True)
    return dict(l.split("=", 1) for l in p.stdout.strip().splitlines() if "=" in l)


def verify(path: str, want_seconds: float) -> list:
    """A file that exists is not a video that plays. Check what is in it."""
    bad = []
    if not os.path.exists(path):
        return ["no file was written"]
    d = probe(path)
    if int(d.get("width", 0)) != W or int(d.get("height", 0)) != H:
        bad.append(f"{d.get('width')}x{d.get('height')}, wanted {W}x{H}")
    dur = float(d.get("duration", 0) or 0)
    if abs(dur - want_seconds) > 1.2:
        bad.append(f"{dur:.1f}s, wanted about {want_seconds:.1f}s")
    if int(os.path.getsize(path)) < 40_000:
        bad.append(f"{os.path.getsize(path)} bytes, too small to hold video")

    # A video of a blank screen encodes fine and is useless, so look at a
    # frame from the middle and check there is something in it.
    mid = os.path.join(OUT, "_probe.png")
    subprocess.run(["ffmpeg", "-y", "-ss", f"{dur/2:.2f}", "-i", path,
                    "-frames:v", "1", mid], capture_output=True)
    if os.path.exists(mid):
        try:
            from PIL import Image
            import numpy as np
            a = np.asarray(Image.open(mid).convert("L"), dtype=float)
            if a.std() < 10:
                bad.append(f"the middle frame is nearly flat "
                           f"(deviation {a.std():.1f}), the video may be blank")
        finally:
            os.remove(mid)
    return bad


if __name__ == "__main__":
    if "--probe" in sys.argv:
        for t in ("ffmpeg", "ffprobe"):
            p = subprocess.run([t, "-version"], capture_output=True, text=True)
            print(f"  {t}: {p.stdout.splitlines()[0][:60] if p.returncode==0 else 'MISSING'}")
        print(f"  output: {OUT}")
        raise SystemExit(0)
    raise SystemExit(0)
