#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_print_and_play_art_count_current() catches a
stale or invented illustrated-card count on
site/deck/entryway-print-and-play.html, and passes clean on the real file.

Found 2026-09-16, this operator, cold-reading this hand-authored
retired-notice page. It claimed "88 cards, illustrated front and back"
while 9 of the 88 reviewed card heroes are rejected (see
ops/card-hero-verdicts.json / gate_deck_download_has_art) and actually
render with a text-only concept panel, no photograph. Fixed the copy to
state the real split; this test proves the new gate can fail on the old
shape and on an invented number, and passes on the corrected file and the
real committed one.

Run:  python ops/tests/test_gate_print_and_play_art_count_current.py
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    # 1. Clean: the page states the real split.
    problems = preflight.check_print_and_play_art_count(
        "79 of the 88 carry a photograph; the other 9 show a text panel.",
        79, 9)
    if problems:
        fails.append("real split wrongly flagged: %s" % problems)

    # 2. The old defect shape: an unqualified claim with no split sentence
    #    at all (the sentence this gate looks for is simply absent).
    problems = preflight.check_print_and_play_art_count(
        "The deck is finished now: 88 cards, illustrated front and back.",
        79, 9)
    if not problems:
        fails.append("missing split sentence NOT caught")

    # 3. A stale illustrated count (as if a hero got rejected since the
    #    page was last written).
    problems = preflight.check_print_and_play_art_count(
        "80 of the 88 carry a photograph; the other 8 show a text panel.",
        79, 9)
    if not problems:
        fails.append("stale illustrated/missing count NOT caught")

    # 4. A stale total (as if the deck itself grew or shrank).
    problems = preflight.check_print_and_play_art_count(
        "79 of the 89 carry a photograph; the other 9 show a text panel.",
        79, 9)
    if not problems:
        fails.append("stale total NOT caught")

    # 5. The real committed file, against the real verdict file, end to end.
    page = os.path.join(ROOT, "site", "deck", "entryway-print-and-play.html")
    verdicts = os.path.join(ROOT, "ops", "card-hero-verdicts.json")
    if os.path.exists(page) and os.path.exists(verdicts):
        import json
        d = json.load(io.open(verdicts, encoding="utf-8"))
        missing = sum(1 for v in d.values()
                      if isinstance(v, dict) and v.get("verdict") != "ok")
        illustrated = len(d) - missing
        text = preflight._visible_html(page)
        problems = preflight.check_print_and_play_art_count(
            text, illustrated, missing)
        if problems:
            fails.append("the real committed file failed against the real "
                         "verdict file: %s" % problems)
    else:
        fails.append("real page or verdict file missing; end-to-end case "
                     "not exercised")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("ok  all print-and-play art-count cases pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
