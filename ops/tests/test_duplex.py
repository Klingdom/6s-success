#!/usr/bin/env python3
"""
A back must land on its own front when the sheet is flipped.

Paper flipped on its long edge reverses left and right. A back printed in the
same column as its front therefore lands on a different card, and every card
in the deck lies about itself. Nobody sees it until they have printed, cut and
sleeved ninety cards, which is the most expensive moment to find out.

Run:  python ops/tests/test_duplex.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src = open(os.path.join(ROOT, "ops", "build_deck_pdf.py"), encoding="utf-8").read()
ns = {"COLS": int(re.search(r"^COLS, ROWS = (\d+)", src, re.M).group(1))}
exec(re.search(r"^def place.*?^    return .*$", src, re.S | re.M).group(0), ns)
place, COLS = ns["place"], ns["COLS"]


def main() -> int:
    fails = []

    for i in range(COLS * 3):
        fc, fr = place(i, "front")
        bc, br = place(i, "back")
        if fr != br:
            fails.append(f"card {i}: rows differ, {fr} and {br}. A long edge "
                         f"flip does not change the row.")
        # After the flip, the back's column becomes COLS-1-bc. That must be
        # the front's column, or the faces belong to different cards.
        if (COLS - 1 - bc) != fc:
            fails.append(f"card {i}: back lands on column {COLS-1-bc} after "
                         f"the flip, front is at {fc}")

    # The mirroring must be a genuine swap, not a no-op on a 3 wide grid.
    if place(0, "back")[0] == place(0, "front")[0] and COLS > 1:
        fails.append("backs are not mirrored at all, which is the bug this "
                     "test exists for")

    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {COLS * 3} card positions checked, {len(fails)} problem(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
