#!/usr/bin/env python3
"""
Prove fix_dashes.py's handling of dashes without a clean space on both
sides, found and fixed 2026-09-07.

Two shapes shipped wrong in REVIEW-COMMERCE-2026-09-07.md and
REVIEW-DISCOVERY-2026-09-07.md before this test existed:

1. A dash hard-wrapped to the end of a physical line ("...invite --",
   sentence continuing on the next line) or glued to markup with no space
   ("...a reason --* and") never matches "\\s+em-dash\\s+", which needs
   whitespace on BOTH sides, so it fell through to the "unspaced survivor"
   fallback: `text.replace("--", ", ")`, replacing only the dash character
   and leaving the genuine leading space in place. Result:
   "...invite , " and "...a reason , * and", a stray space before the
   comma in both, and a stray trailing space in the first.

2. A same-sentence pair of dashes bracketing an aside, split across a
   line-wrap so each dash lands at its own line's end ("This is not
   deceptive --\\ntrue and drawn from the page --\\nbut the markup..."),
   never reaches the same-line pair check at all (each line is fixed on
   its own), and is_label() reads a short plain clause like "This is not
   deceptive" as a label on its own (LABELISH's bare-text branch asks for
   nothing more label-like than "short, plain words, no trailing colon"),
   so both ends of the aside got a colon independently: "not deceptive:
   ... page: but the markup...", a colon immediately followed by "but".

Run:  python ops/tests/test_fix_dashes.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import fix_dashes as F                                        # noqa: E402


def fix_text(text):
    """Run fix_line() over every physical line, the same way run() does."""
    lines = [F.fix_line(l)[0] for l in text.split("\n")]
    return "\n".join(lines)


def main() -> int:
    fails = []

    # 1. A dash hard-wrapped to the very end of a line: comma, no stray
    #    leading or trailing space, sentence continues on the next line.
    line = "`ops/service_orders.py` forwards a purchase to Phil with a real `.ics` invite —"
    out, c = F.fix_line(line)
    expected = "`ops/service_orders.py` forwards a purchase to Phil with a real `.ics` invite,"
    if out != expected:
        fails.append(f"end-of-line dash handled wrong: got {out!r}")
    if c["clause"] != 1 or c["label"] != 0:
        fails.append(f"end-of-line dash should count as 1 clause break, got {c}")

    # 2. A dash glued to markup with no trailing space: comma, no stray
    #    space introduced before the markup character.
    line = "listed as a known non-catalogue object with a reason —* and Ledgerium's objects,"
    out, c = F.fix_line(line)
    expected = "listed as a known non-catalogue object with a reason,* and Ledgerium's objects,"
    if out != expected:
        fails.append(f"markup-glued dash handled wrong: got {out!r}")

    # 3. A same-sentence aside split across a line-wrap: comma on both
    #    ends, never a colon before "but" (the exact regression).
    text = ("strings appear only inside the JSON-LD. This is not deceptive —\n"
            "true and drawn from the page —\n"
            "but the markup is not compliant with the")
    out = fix_text(text)
    if ": but" in out or "deceptive:" in out:
        fails.append(f"cross-line aside still produced a colon before "
                      f"\"but\": {out!r}")
    if "deceptive," not in out or "page," not in out:
        fails.append(f"cross-line aside did not get commas on both ends: {out!r}")

    # 4. A same-line paired aside (both dashes on one line) still becomes
    #    comma, comma via the existing pair check, not colon, colon.
    line = ("This is not deceptive — every answer is true and drawn "
            "from the page — but the markup is not compliant")
    out, c = F.fix_line(line)
    expected = ("This is not deceptive, every answer is true and drawn "
                "from the page, but the markup is not compliant")
    if out != expected:
        fails.append(f"same-line paired aside handled wrong: got {out!r}")
    if c["label"] != 0 or c["clause"] != 2:
        fails.append(f"same-line paired aside should count as 2 clause "
                      f"breaks, got {c}")

    # 5. A real label followed later in the line by an unrelated dash in a
    #    NEW sentence must still get its colon: pairing only applies within
    #    one sentence, and only when both dashes are fully spaced.
    line = "PHASE 1 — build the schema. Then ship it — today if possible"
    out, c = F.fix_line(line)
    if ": " not in out.split(".")[0]:
        fails.append(f"a real label before the sentence boundary lost its "
                      f"colon when a later, unrelated dash was present: {out!r}")

    # 6. A short ordinary clause fully spaced on both sides, still under
    #    the 3-word cap, must not become a label when the far side is a
    #    coordinating conjunction picking the sentence back up: found
    #    2026-09-07 in REVIEW-QA-2026-09-07.md ("and found none -- but the
    #    line item...", "**Yes -- and the tool...").
    line = "and found none — but the line item a buyer scans is the name."
    out, c = F.fix_line(line)
    if ": but" in out or "none," not in out:
        fails.append(f"a short clause before a conjunction still read as a "
                      f"label: {out!r}")

    line = "**Yes — and the tool to do it is already written**"
    out, c = F.fix_line(line)
    if ": and" in out or "Yes," not in out:
        fails.append(f"a one-word clause before a conjunction still read "
                      f"as a label: {out!r}")

    # 7. A single, lone dash after a real label, fully spaced on both
    #    sides, is untouched by any of the above (still a colon): its
    #    value is a description, not a conjunction, so is_continuation()
    #    does not fire.
    line = "L3 — the deploy step"
    out, c = F.fix_line(line)
    if out != "L3: the deploy step" or c["label"] != 1:
        fails.append(f"a lone real label regressed: {out!r} {c}")

    # 8. A single, lone dash in ordinary prose, fully spaced, is still a
    #    comma (unchanged behaviour for the common case this file was
    #    already built for).
    line = "It rained all day, we stayed in — which was the right call"
    out, c = F.fix_line(line)
    if "—" in out or c["clause"] != 1:
        fails.append(f"a lone prose dash regressed: {out!r} {c}")

    # 9. The control layer itself must be clean right now: this is the
    #    gate ops/preflight.py's own ("dashes", fix_dashes.py, --check) step
    #    runs.
    bad = F.remaining()
    if bad:
        fails.append(f"control files still carry a dash: {bad}")

    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {9 - len(fails)} of 9 cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
