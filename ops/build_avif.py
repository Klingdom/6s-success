"""Add AVIF alongside every WebP, and wire it as the first source.

The site already does the hard part: 121 pages use <picture> with srcset and
748 WebP references, so the responsive plumbing exists and this only adds a
better-compressed format in front of it.

Measured before building, not assumed: six representative images encoded at
crf 32 came out at 59 per cent of their WebP, so AVIF saves about 41 per cent
on files that are already optimised. Across 896 WebP files totalling 39.0 MB
that is roughly 16 MB, and most of the audience is on a phone.

Browsers that do not understand AVIF skip the first <source> and take the WebP
exactly as they do today, so this cannot regress anybody.

    python ops/build_avif.py --encode      make the .avif files
    python ops/build_avif.py --wire        add <source type="image/avif">
    python ops/build_avif.py --check       report coverage, change nothing
"""
from __future__ import annotations

import glob
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
CRF = "32"


def webps() -> list:
    return sorted(glob.glob(os.path.join(SITE, "**", "*.webp"), recursive=True))


def encode(force: bool = False) -> int:
    made, kept, failed = 0, 0, []
    for w in webps():
        a = w[:-5] + ".avif"
        if os.path.exists(a) and not force:
            kept += 1
            continue
        p = subprocess.run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", w,
             "-c:v", "libaom-av1", "-crf", CRF, "-cpu-used", "6",
             "-still-picture", "1", a],
            capture_output=True, text=True, timeout=300)
        # An encoder that returns zero and writes nothing is a failure, so the
        # file is what decides, not the exit code.
        if os.path.exists(a) and os.path.getsize(a) > 0:
            made += 1
        else:
            failed.append((os.path.basename(w), p.stderr[-120:]))
    print("  encoded %d, already present %d, failed %d" % (made, kept, len(failed)))
    for n, e in failed[:5]:
        print("     %s: %s" % (n, e.replace("\n", " ")[:100]))
    return 0


SOURCE = re.compile(r'<source([^>]*?)type="image/webp"([^>]*?)>')


def wire() -> int:
    """Put an AVIF source before each WebP source, when the file exists.

    The tag is rebuilt from its parts rather than patched, because the first
    attempt spliced the new srcset in while the original was still inside the
    captured remainder, which would have emitted two srcset attributes on one
    element. Cheaper to construct than to repair.
    """
    changed, added, skipped = 0, 0, 0
    for f in sorted(glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True)):
        s = io.open(f, encoding="utf-8", errors="replace").read()
        if 'type="image/avif"' in s or "image/webp" not in s:
            continue
        out, last, n = [], 0, 0
        for m in SOURCE.finditer(s):
            whole = m.group(0)
            srcset = re.search(r'srcset="([^"]*)"', whole)
            if not srcset:
                continue
            sizes = re.search(r'sizes="([^"]*)"', whole)

            # Only claim an AVIF that exists. A source pointing at a missing
            # file is a broken image for every browser that prefers it.
            ok = True
            for entry in srcset.group(1).split(","):
                rel = entry.strip().split(" ")[0].split("?")[0]
                if not rel.endswith(".webp"):
                    ok = False
                    break
                disk = os.path.normpath(os.path.join(
                    os.path.dirname(f), rel.replace("/", os.sep)))
                if not os.path.exists(disk[:-5] + ".avif"):
                    ok = False
                    break
            if not ok:
                skipped += 1
                continue

            avif_srcset = srcset.group(1).replace(".webp", ".avif")
            tag = '<source type="image/avif" srcset="%s"%s>' % (
                avif_srcset,
                ' sizes="%s"' % sizes.group(1) if sizes else "")
            out.append(s[last:m.start()])
            out.append(tag)
            out.append(whole)
            last = m.end()
            n += 1
        if not n:
            continue
        out.append(s[last:])
        io.open(f, "w", encoding="utf-8", newline="").write("".join(out))
        changed += 1
        added += n
    print("  %d page(s) rewritten, %d avif source(s) added, %d skipped for a "
          "missing file" % (changed, added, skipped))
    return 0


def check() -> int:
    w = webps()
    have = sum(1 for x in w if os.path.exists(x[:-5] + ".avif"))
    pages = glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True)
    wired = sum(1 for f in pages
                if 'type="image/avif"' in io.open(
                    f, encoding="utf-8", errors="replace").read())
    print("  webp files            : %d" % len(w))
    print("  with an avif sibling  : %d" % have)
    print("  pages serving avif    : %d" % wired)
    return 0


if __name__ == "__main__":
    if "--encode" in sys.argv:
        sys.exit(encode("--force" in sys.argv))
    if "--wire" in sys.argv:
        sys.exit(wire())
    sys.exit(check())
