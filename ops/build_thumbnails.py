"""A designed thumbnail for every zone video.

YouTube picks a frame from the middle of the video when nothing is supplied,
and for these films that frame is a wall of small instructional text. It is
unreadable at the size a thumbnail is actually seen, which is about 168 pixels
wide on a phone. The thumbnail is most of what decides whether anybody clicks,
so leaving it to chance wastes the whole upload.

The design rules here follow from that size, not from taste:

  - Three to five large words. Anything longer cannot be read at 168px.
  - The zone name is the message. The room is a small eyebrow above it, because
    somebody searching "kitchen" needs the room, and somebody scanning a
    playlist needs the zone.
  - Real contrast, no photograph behind the type. There is no per-zone
    photography, and type over a busy image is the usual way thumbnails become
    illegible.
  - The six-S spine as the only brand mark, so a viewer recognises the channel
    across a playlist without any logo.

No clickbait: no fake arrows, no shock faces, no "you're doing it wrong". The
promise on the thumbnail is the promise the video keeps.

Renders through the same headless browser as the videos, so the fonts, palette
and spine are identical rather than merely similar.

    python ops/build_thumbnails.py
    python ops/build_thumbnails.py --zone "Landing Zone" --room Entryway
    python ops/build_thumbnails.py --check
"""
from __future__ import annotations

import io
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))
OUT = os.path.join(ROOT, "build", "video", "thumbnails")

# YouTube's own recommendation, and the size every surface downscales from.
TW, TH = 1280, 720
# Hard limit. An oversized file is rejected at upload with an unhelpful error.
MAX_BYTES = 2 * 1024 * 1024


def shot(exe: str, extra: list, html: str, png: str) -> None:
    """Screenshot at thumbnail size.

    video_zone.shot() is fixed to the video's own dimensions by a module-level
    constant set from argv, so it cannot render 1280x720. Rather than mutate
    that module's globals, which would silently change the next video render,
    this keeps its own copy of a nine-line function.
    """
    with tempfile.TemporaryDirectory() as prof:
        f = png.replace(".png", ".html")
        io.open(f, "w", encoding="utf-8", newline="").write(html)
        subprocess.run([exe, "--headless=new", "--disable-gpu",
                        "--hide-scrollbars", "--force-device-scale-factor=1",
                        "--user-data-dir=%s" % prof,
                        "--window-size=%d,%d" % (TW, TH),
                        "--virtual-time-budget=6000", "--screenshot=%s" % png,
                        *extra,
                        "file:///" + os.path.abspath(f).replace(os.sep, "/")],
                       capture_output=True, timeout=90)
        os.remove(f)


def fit(zone: str) -> str:
    """Type size that keeps the longest zone names readable.

    "Buffet or Sideboard Storage" and "Landing Zone" cannot take the same size
    without one of them either overflowing or looking timid.
    """
    n = len(zone)
    return "150px" if n <= 14 else "126px" if n <= 22 else \
           "104px" if n <= 30 else "88px"


def html_for(room: str, zone: str, vz) -> str:
    spine = "".join(
        '<i style="background:%s"></i>' % c for _n, c in vz.SIX)
    fonts = vz.FONTS if hasattr(vz, "FONTS") else ""
    return """<!doctype html><meta charset="utf-8"><style>
%s
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%dpx;height:%dpx;overflow:hidden}
/* THE BUG THAT COST THREE LAYOUTS: the header row was overflowing 1280px.
   An overflowing row makes the whole DOCUMENT wider and taller than the
   window, and the screenshot captures the window, so anything in a bottom
   row fell outside the frame and rendered as nothing at all. Every attempt
   still exited 0. I chased it as a positioning bug through absolute, flex
   and grid layouts before a clipped wordmark at the right edge showed what
   was actually happening.
   So nothing here may exceed the width. The six-S spine is the whole brand
   mark now: the wordmark was redundant, because YouTube prints the channel
   name under every thumbnail anyway. */
body{background:%s;color:%s;font-family:Inter,system-ui,sans-serif;
     display:grid;grid-template-rows:auto 1fr;
     padding:60px 80px 72px 104px;border-left:26px solid %s}
/* Everything is left-aligned and sized by its own content. Nothing is pushed
   to the right edge by justify-content, because that is what was overflowing
   the frame and taking whole rows out of the picture with it. */
.top{display:flex;flex-direction:column;align-items:flex-start;gap:26px}
.room{background:%s;color:%s;font-size:34px;font-weight:800;
      letter-spacing:.15em;text-transform:uppercase;padding:12px 22px;
      border-radius:6px}
.spine{display:flex;gap:9px}
.spine i{display:block;width:56px;height:12px;border-radius:6px}
.zone{font-size:%s;font-weight:800;line-height:.96;letter-spacing:-.025em;
      text-wrap:balance;max-width:15ch;align-self:center}
</style>
<div class="top"><div class="room">%s</div><div class="spine">%s</div></div>
<div class="zone">%s</div>
""" % (fonts, TW, TH, vz.PAPER, vz.INK, vz.ACCENT, vz.ACCENT, vz.PAPER,
       fit(zone), room.upper(), spine, zone)


def main() -> int:
    import video_zone as vz

    if "--check" in sys.argv:
        n = len([f for f in os.listdir(OUT) if f.endswith(".png")]) \
            if os.path.isdir(OUT) else 0
        print("  thumbnails: %d of 114" % n)
        return 0 if n >= 114 else 1

    want_z = sys.argv[sys.argv.index("--zone") + 1] if "--zone" in sys.argv else None
    want_r = sys.argv[sys.argv.index("--room") + 1] if "--room" in sys.argv else None
    os.makedirs(OUT, exist_ok=True)
    exe, extra = vz.browser()

    def one(t):
        return t.lower().replace(" ", "-").replace(",", "").replace("/", "-")

    made, oversize, failed = 0, [], []
    for room, z in vz.zones():
        zone = z["zone"]
        if (want_z and zone != want_z) or (want_r and room != want_r):
            continue
        png = os.path.join(OUT, "%s--%s.png" % (one(room), one(zone)))
        shot(exe, extra, html_for(room, zone, vz), png)
        if not os.path.exists(png):
            failed.append("%s / %s" % (room, zone))
            continue
        size = os.path.getsize(png)
        if size > MAX_BYTES:
            oversize.append((os.path.basename(png), size))
        made += 1

    print("  thumbnails written: %d" % made)
    if oversize:
        print("  OVER 2 MB (YouTube will reject): %d %s"
              % (len(oversize), oversize[:2]))
    if failed:
        print("  FAILED to render   : %d %s" % (len(failed), failed[:3]))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
