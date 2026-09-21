#!/usr/bin/env python3
"""
zones() used to scrape video_zone.py's formatted "--list-all" text output,
splitting each line on a run of 2+ spaces and keeping the first and last
piece as (room, zone). That column is fixed to 18 characters
(f"    {r:18} {z['zone']}"); a room name at or past 18 characters leaves
only the one literal space between the two fields, so the split produces a
single unsplit piece and the len(parts) >= 2 guard silently drops that zone
from the batch, no error printed, the exact "success it never observed"
shape this file's own module docstring names as the costliest defect class
here. No real room name reaches 18 characters today (longest is Primary
Bathroom, 16), so it never fired against the live corpus.

Fixed 2026-09-11, cold-read: zones() now reads video_zone.zones() directly,
the same structured source --list-all itself formats from, so there is no
text column to overflow.

Widened 2026-09-21, cold-read: the resource-exhaustion retry compared
p.returncode to 3221225794, the UNSIGNED value of 0xC0000142
(STATUS_DLL_INIT_FAILED). CPython's subprocess reports a Windows exit code
with the high bit set as a SIGNED 32-bit int, -1073741502 for this status,
so the comparison could never match and the documented retry-with-backoff
never fired: a resource-exhausted zone was recorded FAILED on the first
attempt, no pause, no second try. Not reproducible in this Linux sandbox
(no Windows host, no video toolchain); Case 5 below proves the arithmetic
that grounds the fix instead of the live crash.

Run:  python ops/tests/test_render_all_zone_videos.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import render_all_zone_videos as razv                             # noqa: E402
import video_zone as vz                                           # noqa: E402


def old_text_scrape_parser(room: str, zone: str) -> list:
    """The pre-fix logic, isolated, so the regression it had is provable
    without running the real 114-zone --list-all subprocess."""
    line = "    %-18s %s" % (room, zone)
    parts = re.split(r"\s{2,}", line.strip())
    return parts


def main() -> int:
    fails = []

    # Case 1: the fix returns the same 114 pairs the structured source has,
    # in the same order, not a re-derived or re-sorted list.
    direct = [(room, z["zone"]) for room, z in vz.zones()]
    got = razv.zones()
    if got != direct:
        fails.append("zones() diverged from video_zone.zones() directly; "
                      "expected the identical structured pairs")

    # Case 2: every real room name today is short enough that the retired
    # text-column parser would still have split it correctly. This is not
    # proof the old code was safe, only that today's corpus never happened
    # to trigger it.
    for room, zone in direct:
        old_parts = old_text_scrape_parser(room, zone)
        if len(old_parts) < 2:
            fails.append(f"a real room name today already overflows the old "
                          f"18-char column: {room!r}")

    # Case 3: prove the retired parser really did have the defect, on a
    # room name at exactly the 18-character boundary. This is the
    # regression the fix exists to close.
    long_room = "Primary Bathrooms!"  # 18 characters
    assert len(long_room) == 18
    old_parts = old_text_scrape_parser(long_room, "Medicine Cabinet")
    if len(old_parts) >= 2:
        fails.append("expected the retired parser to fail to split an "
                      "18-character room name (this proves the bug was "
                      f"real); it did not, got {old_parts!r}")

    # Case 4: the new zones() has no such boundary. video_zone.zones()
    # itself is monkeypatched to inject a fake 18+ character room, and the
    # fix must still return it correctly paired.
    old_zones_fn = vz.zones
    try:
        vz.zones = lambda: [("Primary Bathrooms!", {"zone": "Medicine Cabinet"})]
        patched = razv.zones()
        if patched != [("Primary Bathrooms!", "Medicine Cabinet")]:
            fails.append(f"zones() mishandled an 18-character room name "
                          f"even after the fix: got {patched!r}")
    finally:
        vz.zones = old_zones_fn

    # Case 5: the retry constant must hold the SIGNED 32-bit representation
    # of 0xC0000142, not only the unsigned DWORD, and a returncode of
    # exactly that signed value must be recognised as the transient to
    # retry, not a real failure.
    signed = 0xC0000142 - 2**32
    if signed != -1073741502:
        fails.append(f"sanity check on the signed-DWORD arithmetic itself "
                      f"is wrong: 0xC0000142 signed should be -1073741502, "
                      f"computed {signed}")
    if signed not in razv.STATUS_DLL_INIT_FAILED:
        fails.append(f"STATUS_DLL_INIT_FAILED does not contain the signed "
                      f"representation {signed}; the retry this constant "
                      f"exists for could never fire against a real Windows "
                      f"crash: {razv.STATUS_DLL_INIT_FAILED!r}")
    if 3221225794 not in razv.STATUS_DLL_INIT_FAILED:
        fails.append("STATUS_DLL_INIT_FAILED dropped the unsigned form; "
                      "keep both so a differently-signed runtime cannot "
                      "silently reopen this gap")

    total = 5
    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {total - len(fails)} of {total} cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
