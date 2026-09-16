#!/usr/bin/env python3
"""
Prove the two store gates actually check something.

Added 2026-09-16 with the phone app's store art and listing. Both gates guard a
submission, which is the slowest thing in this system to correct: a wrong icon
or an over-length subtitle sits in a store listing until an entirely new build
is reviewed.

The failure mode worth testing is not "does it pass today". It is:

  1. png_header misreads a colour type, and gate_store_art waves through an
     Apple icon carrying an alpha channel, which is an outright rejection.
  2. Somebody rewords a heading in STORE-LISTING.md, the gate's regex stops
     matching, and it reports nothing forever while looking green. That is the
     same shape as every "unchecked is not passing" defect this repo has paid
     for, so the gate must report a MISSING FIELD rather than fall silent.

Run:  python ops/tests/test_gate_store_art.py
"""
import os
import struct
import sys
import tempfile
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def make_png(path: str, w: int, h: int, colour_type: int) -> None:
    """A minimal, real PNG header. Built rather than copied from the committed
    art, so this test still means something the day that art is redrawn."""
    ihdr = struct.pack(">IIBBBBB", w, h, 8, colour_type, 0, 0, 0)
    chunk = struct.pack(">I", len(ihdr)) + b"IHDR" + ihdr
    chunk += struct.pack(">I", zlib.crc32(b"IHDR" + ihdr) & 0xFFFFFFFF)
    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n" + chunk)


def check_png_header(fails: list) -> None:
    tmp = tempfile.mkdtemp(prefix="storeart")

    rgb = os.path.join(tmp, "apple.png")
    make_png(rgb, 1024, 1024, 2)
    got = preflight.png_header(rgb)
    if got != (1024, 1024, 2):
        fails.append("RGB 1024 header read back as %r, wanted (1024, 1024, 2)" % (got,))

    rgba = os.path.join(tmp, "adaptive.png")
    make_png(rgba, 1024, 1024, 6)
    got = preflight.png_header(rgba)
    if got != (1024, 1024, 6):
        fails.append("RGBA header read back as %r, wanted (1024, 1024, 6)" % (got,))

    # An Apple icon with alpha is a rejection, so the two must not be confused.
    if preflight.png_header(rgb)[2] == preflight.png_header(rgba)[2]:
        fails.append("RGB and RGBA icons report the same colour type, so alpha is invisible")

    # Play's feature graphic is the one non-square shape; width and height must
    # not be transposed, which a symmetric test would never notice.
    wide = os.path.join(tmp, "feature.png")
    make_png(wide, 1024, 500, 2)
    got = preflight.png_header(wide)
    if got[:2] != (1024, 500):
        fails.append("1024x500 read back as %r, width and height may be transposed" % (got[:2],))

    # gate_store_art calls this on whatever sits at the path. A raise here would
    # be swallowed by run_gate and look exactly like a pass.
    junk = os.path.join(tmp, "notapng.png")
    with open(junk, "wb") as fh:
        fh.write(b"this is not a png at all")
    try:
        got = preflight.png_header(junk)
    except Exception as exc:                                   # noqa: BLE001
        fails.append("png_header raised on a non-PNG (%s); run_gate would hide it" % exc)
    else:
        if got != (0, 0, -1):
            fails.append("non-PNG returned %r, wanted (0, 0, -1)" % (got,))


GOOD_LISTING = """
**App name (Apple, 30 char max):** 6S Success Home Quest

**Subtitle (Apple, 30 max):** One zone, one job, put it down

**Short description (Play, 80 max):**
Draw a zone, do one small job, put it down. 114 micro zones, works offline.
"""


def check_listing_lengths(fails: list) -> None:
    # 1. A compliant listing is silent.
    bad = preflight.store_listing_overruns(GOOD_LISTING)
    if bad:
        fails.append("a compliant listing was flagged: %r" % (bad,))

    # 2. An over-cap subtitle is caught, and reports its real length.
    over = GOOD_LISTING.replace("One zone, one job, put it down",
                                "One zone, one job, and then you put it down")
    bad = preflight.store_listing_overruns(over)
    hits = [b for b in bad if b[0] == "subtitle"]
    if not hits:
        fails.append("a 43-character subtitle was not caught")
    elif hits[0][2] != 43:
        fails.append("subtitle length reported as %r, wanted 43" % (hits[0][2],))

    # 3. THE CASE THIS TEST EXISTS FOR. The gate finds fields by matching a
    # literal heading. Reword the heading and a silent gate checks nothing
    # forever while still reporting green, so it must say the field is missing.
    reworded = GOOD_LISTING.replace("**Subtitle (Apple, 30 max):**",
                                    "**Subtitle (Apple, 30 characters):**")
    bad = preflight.store_listing_overruns(reworded)
    missing = [b for b in bad if b[0] == "subtitle" and b[1] == "FIELD MISSING"]
    if not missing:
        fails.append("a reworded heading did not report FIELD MISSING; "
                     "the gate would silently stop checking the subtitle")

    # 4. An empty document must not read as a clean pass.
    if not preflight.store_listing_overruns(""):
        fails.append("an empty listing reported no problems at all")


def main() -> int:
    fails = []
    check_png_header(fails)
    check_listing_lengths(fails)

    if fails:
        print("test_gate_store_art FAILED:")
        for f in fails:
            print("  -", f)
        return 1
    print("  png_header: sizes, colour types, transposition and a non-PNG all correct")
    print("  store_listing_overruns: compliant silent, overrun caught at its true length,")
    print("    a reworded heading reports FIELD MISSING rather than falling silent")
    print("test_gate_store_art: all cases pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
