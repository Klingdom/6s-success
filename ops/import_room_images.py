#!/usr/bin/env python3
"""
Put the book's real photographs on the room and zone pages.

The 114 zone pages and 20 room pages shipped with no images at all, while the
book chapters they were generated from carry 38 finished figures with alt text
already written by a person: before and after pairs, overhead zone plans,
cleaning sequences, and per zone standards.

Describing an image in a caption when the image exists is worse than useless,
so this imports the real ones.

What it does
  Reads each room chapter's final HTML, which already places every figure and
  describes it, and takes the src and the alt verbatim. The alt text is the
  book's own and is better than anything generated: it describes what is in the
  frame, not what the picture is for.

  Copies the JPG, never the PNG. The PNGs are 1.6 to 2.6 MB each because they
  are lossless masters. The JPGs are 150 to 320 KB and are what the book itself
  uses on the page.

  Resizes anything wider than 1600 pixels and re-encodes at quality 82, which
  is invisible at reading size and keeps the site's total weight sane. The
  site's largest asset problem has already cost one investigation.

Run:  python ops/import_room_images.py --check
      python ops/import_room_images.py --apply
"""
import glob
import io
import json
import os
import re
import shutil
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = (r"C:\Users\philk\Desktop\Process Kaizen\Process Kaizen\Work Folder"
          r"\Nova Consulting\06 - Lean Six Sigma Initiative\07 - 6S Materials"
          r"\6S Environment\Master\6S Success Home Edition")
OUT = os.path.join(ROOT, "site", "assets", "img", "rooms")
MAP = os.path.join(ROOT, "ops", "room-images.json")
MAX_W, QUALITY = 1600, 82


def rooms():
    d = json.load(io.open(os.path.join(ROOT, "content", "manual", "source",
                                       "content.json"), encoding="utf-8"))
    return [r["room"] for r in d["rooms"]]


def figures():
    """chapter number -> [(filename, alt)], taken from the book's own markup."""
    out = {}
    for n, room in zip(range(31, 51), rooms()):
        f = glob.glob(os.path.join(ROOT, "content", "book", f"*Chapter-{n}*",
                                   f"chapter_{n}_final.html"))
        if not f:
            continue
        s = io.open(f[0], encoding="utf-8", errors="replace").read()
        figs = re.findall(r'<img[^>]*src="([^"]+\.jpg)"[^>]*alt="([^"]*)"', s)
        if figs:
            out[n] = (room, [(os.path.basename(a), b) for a, b in figs])
    return out


def source_path(n, fname):
    return os.path.join(MASTER, f"6S-Success-Chapter-{n}", fname)


def main(apply_it):
    figs = figures()
    total = sum(len(v[1]) for v in figs.values())
    print(f"  {len(figs)} illustrated rooms, {total} figures referenced")

    if apply_it:
        os.makedirs(OUT, exist_ok=True)

    manifest, copied, saved = {}, 0, 0
    for n, (room, items) in sorted(figs.items()):
        entries = []
        for fname, alt in items:
            src = source_path(n, fname)
            if not os.path.exists(src):
                print(f"    MISSING on disk: {fname}")
                continue
            before = os.path.getsize(src)
            dst = os.path.join(OUT, fname)
            if apply_it:
                im = Image.open(src).convert("RGB")
                if im.width > MAX_W:
                    im = im.resize((MAX_W, round(im.height * MAX_W / im.width)),
                                   Image.LANCZOS)
                im.save(dst, "JPEG", quality=QUALITY, optimize=True, progressive=True)
                after = os.path.getsize(dst)
                saved += before - after
                copied += 1
            entries.append({"file": fname, "alt": alt})
        if entries:
            manifest[room] = entries
            print(f"    {room:<18} {len(entries)} figures")

    if apply_it:
        io.open(MAP, "w", encoding="utf-8", newline="").write(
            json.dumps(manifest, indent=1, ensure_ascii=False))
        print(f"\n  copied {copied} images into site/assets/img/rooms/")
        print(f"  reclaimed {saved/1048576:.1f} MB by resizing and re-encoding")
        print(f"  wrote {os.path.relpath(MAP, ROOT)}")
    else:
        print("\n  Run with --apply to copy them.")
    return 0


if __name__ == "__main__":
    sys.exit(main(len(sys.argv) > 1 and sys.argv[1] == "--apply"))
