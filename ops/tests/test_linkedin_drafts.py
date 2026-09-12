#!/usr/bin/env python3
"""
build()'s own docstring says "--preview" must not consume rotation
inventory: only an actual --send should mark a post as served.

Found 2026-09-08: build() called corpus_posts.take(..., record=True)
unconditionally, so the exact command this file's docstring recommends for
looking at today's draft ("python ops/linkedin_drafts.py --preview") silently
advanced ops/corpus-rotation.json every time it ran, permanently skipping
posts Phil never actually saw. A cold read of the tool for an unrelated
investigation reproduced this by accident the same day. Fixed by threading a
record flag through build() that only __main__ sets True for a real --send.
This test proves both directions: a default/preview call must not touch the
rotation file, and record=True must still advance it.

Run:  python ops/tests/test_linkedin_drafts.py
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import linkedin_drafts as ld                                      # noqa: E402
import corpus_posts as cp                                         # noqa: E402


def _read_rotation():
    if not os.path.exists(cp.ROTATION):
        return None
    return io.open(cp.ROTATION, encoding="utf-8").read()


def _remaining(text: str) -> int:
    m = re.search(r"([\d,]+) usable", text)
    return int(m.group(1).replace(",", ""))


def main() -> int:
    fails = []
    before = _read_rotation()

    try:
        # A bare/default call, and an explicit "--preview"-shaped call
        # (record=False), must leave the rotation file byte-identical.
        ld.build()
        after_default = _read_rotation()
        if after_default != before:
            fails.append("build() with no args mutated corpus-rotation.json; "
                         "the default must behave like a preview")

        ld.build(record=False)
        after_explicit_false = _read_rotation()
        if after_explicit_false != before:
            fails.append("build(record=False) mutated corpus-rotation.json")

        # record=True (what an actual --send now passes) must still advance
        # the rotation, or the real daily send would repeat itself forever.
        _, text_day1 = ld.build(record=True)
        after_record_true = _read_rotation()
        if after_record_true == before:
            fails.append("build(record=True) left corpus-rotation.json "
                         "unchanged; a real --send would never advance")

        # Found 2026-09-12: "remaining" was a bare len(pool(...)), so the
        # real daily --send email Phil actually reads has reported the same
        # full corpus size every day forever, never reflecting a single one
        # of the three posts it serves every day. A second real day must
        # show it drop by exactly three, not stay frozen.
        remaining_day1 = _remaining(text_day1)
        _, text_day2 = ld.build(record=True)
        remaining_day2 = _remaining(text_day2)
        if remaining_day2 != remaining_day1 - 3:
            fails.append(f"'remaining' read {remaining_day1} then "
                         f"{remaining_day2} across two served days; expected "
                         f"it to drop to {remaining_day1 - 3}, one day's "
                         f"worth of posts actually served")
    finally:
        # Restore exactly what was on disk before this test ran, whatever
        # happened above, so running this test never itself costs rotation
        # inventory.
        if before is None:
            if os.path.exists(cp.ROTATION):
                os.remove(cp.ROTATION)
        else:
            io.open(cp.ROTATION, "w", encoding="utf-8", newline="").write(before)

    total = 4
    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {total - len(fails)} of {total} cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
