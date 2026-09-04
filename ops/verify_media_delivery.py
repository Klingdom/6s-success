"""Confirm every rendered video exists outside build/, where it can survive.

Written 2026-09-03, immediately after nearly losing 456 videos.

Video stopped being tracked in git that day. Untracking with `git rm --cached`
records a real deletion in the commit, and when ship.py rebased that commit
onto an origin that still had the files tracked, git removed 377 of them from
the working tree. Nothing was lost only because a delivery backfill had copied
them to the Desktop twenty minutes earlier.

That was luck, and luck is not a backup. Now that git no longer holds the
video, the Desktop folder is the only copy, so its completeness is a fact worth
checking rather than assuming. This reports a shortfall; it does not copy,
because silently healing a gap would hide the reason the gap appeared.

    python ops/verify_media_delivery.py
    python ops/verify_media_delivery.py --fix    copy what is missing

Exit 0: every rendered file has a copy outside build/.
Exit 1: a real gap, on a machine that has a Desktop/6s-success-videos folder.
Exit 2: no Desktop/6s-success-videos folder exists here at all, so nothing
        could be compared. Not evidence of a gap; most likely this is not
        Phil's own machine.
"""
from __future__ import annotations

import io
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop", "6s-success-videos")

# build directory -> Desktop folder. Narrated output splits by orientation,
# which is why one source maps to two destinations.
PAIRS = [
    ("build/video/zones", "vertical-9x16", lambda f: f.endswith(".mp4")),
    ("build/video/zones-16x9", "wide-16x9", lambda f: f.endswith(".mp4")),
    ("build/video/zones-narrated", "narrated-16x9",
     lambda f: f.endswith(".mp4") and "-16x9" in f),
    ("build/video/zones-narrated", "narrated-9x16",
     lambda f: f.endswith(".mp4") and "-16x9" not in f),
    ("build/video/zones-narrated", "narrated-captions",
     lambda f: f.endswith(".srt")),
]


def differs(src: str, dst: str) -> bool:
    """True when the delivered copy is not the same content as the built one.

    Captions are text and line endings are not content, so they are compared
    after normalising. Video is compared by size, which is enough to catch the
    cases that matter here: an absent copy, or one truncated by a copy that
    died halfway.
    """
    if src.lower().endswith((".srt", ".txt", ".json", ".ass")):
        try:
            crlf, lf = b"\r\n", b"\n"
            a = io.open(src, "rb").read().replace(crlf, lf)
            b = io.open(dst, "rb").read().replace(crlf, lf)
            return a != b
        except OSError:
            return True
    return os.path.getsize(src) != os.path.getsize(dst)


def scan(desktop_root: str, fix: bool = False):
    """Compare build/ against desktop_root. Pure enough to test without a
    real Desktop: pass any path and nothing outside desktop_root is touched.

    Returns (desktop_missing, rows, missing_total, copied). desktop_missing
    is True when desktop_root itself does not exist at all, which means this
    environment has no Desktop delivery folder to compare against, not that
    every file in build/ is confirmed undelivered. Every cloud sandbox and
    CI runner is in exactly this state; only Phil's own machine has a real
    Desktop/6s-success-videos. Collapsing "cannot check" into "228 missing"
    is a fabricated reliability alarm, the same shape already fixed once for
    ops/checkin.py's youtube_published.
    """
    if not os.path.isdir(desktop_root):
        return True, [], 0, 0

    missing_total, copied, rows = 0, 0, []
    for rel, folder, keep in PAIRS:
        src_dir = os.path.join(ROOT, rel)
        dst_dir = os.path.join(desktop_root, folder)
        if not os.path.isdir(src_dir):
            rows.append((folder, 0, 0, "no build directory"))
            continue
        want = sorted(f for f in os.listdir(src_dir) if keep(f))
        gap = []
        for f in want:
            src, dst = os.path.join(src_dir, f), os.path.join(dst_dir, f)
            # A stale copy is worse than an absent one, because it looks
            # fine. But compare what the file MEANS, not its byte count: the
            # first version of this check compared sizes and reported 88
            # captions as undelivered when the only difference was CRLF
            # against LF. A check that cannot tell "different" from "wrong"
            # sends people to re-copy 88 correct files.
            if not os.path.exists(dst):
                gap.append(f)
            elif differs(src, dst):
                gap.append(f)
        if gap and fix:
            os.makedirs(dst_dir, exist_ok=True)
            for f in gap:
                shutil.copy2(os.path.join(src_dir, f), os.path.join(dst_dir, f))
                copied += 1
            gap = []
        missing_total += len(gap)
        rows.append((folder, len(want), len(gap),
                     gap[0] if gap else ""))
    return False, rows, missing_total, copied


def main() -> int:
    fix = "--fix" in sys.argv
    desktop_missing, rows, missing_total, copied = scan(DESKTOP, fix=fix)

    if desktop_missing:
        print("  no Desktop delivery folder here (%s)." % DESKTOP)
        print("  This is not Phil's own machine, or nothing has been "
              "delivered yet. Cannot verify delivery from this environment; "
              "that is not the same as a confirmed gap.")
        return 2

    print("  %-20s %7s %9s  %s" % ("folder", "built", "undelivered", "example"))
    for folder, n, gap, ex in rows:
        print("  %-20s %7d %9d  %s" % (folder, n, gap, ex[:40]))
    if copied:
        print("\n  copied to the Desktop: %d" % copied)
    if missing_total:
        print("\n  %d rendered file(s) exist only in build/, which is not "
              "backed up and is not in git. Run with --fix." % missing_total)
        return 1
    print("\n  Every rendered file has a copy outside build/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
