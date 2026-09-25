#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_deck_og_image_honest() catches a room deck
page whose social preview image was copied from a different room's deck
template.

Found live 2026-09-25: the Entryway (second deck), Laundry Room, Home
Office, Primary Bathroom and Garage deck page generators were each built by
copying the Kitchen deck's own generator as a template, and every one kept
the Kitchen chapter's real photograph (ch32-image01.jpg) as its own
og:image/twitter:image, unchanged. Sharing any of those five links anywhere
(LinkedIn, Facebook, iMessage, Pinterest) showed a kitchen photo, not the
room the link was actually about.

Tests the pure logic (check_deck_og_image_honest) with synthetic page
text, so it never touches the real committed pages, then separately checks
the real committed pages directly.

Run:  python ops/tests/test_gate_deck_og_image_honest.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def page(og: str, tw: str = None) -> str:
    tw = og if tw is None else tw
    return (f'<meta property="og:image" content="{og}">\n'
            f'<meta name="twitter:image" content="{tw}">\n')


CLEAN = {
    "kitchen-deck.html": page(
        "https://6s-success.com/assets/img/rooms/ch32-image01.jpg"),
    "entryway-deck.html": page(
        "https://6s-success.com/assets/img/rooms/ch31-image01.jpg"),
    "garage-deck.html": page(
        "https://6s-success.com/assets/zones/garage--primary-workbench-lg.jpg"),
    "laundry-room-deck.html": page(
        "https://6s-success.com/assets/zones/laundry-room--washer-and-dryer-lg.jpg"),
    "home-office-deck.html": page(
        "https://6s-success.com/assets/zones/home-office--primary-desk-lg.jpg"),
    "primary-bathroom-deck.html": page(
        "https://6s-success.com/assets/zones/primary-bathroom--vanity-counter-lg.jpg"),
}


def main() -> int:
    fails = []

    # 1. Clean: every deck's own room-correct image, no false positive.
    problems = preflight.check_deck_og_image_honest(CLEAN)
    if problems:
        fails.append("the clean synthetic case was flagged: %s" % problems)

    # 2. The real, live defect this gate exists to catch: a room deck with
    #    no real photo of its own borrowing the Kitchen chapter's photo,
    #    the exact shape found live on all five decks built after Kitchen.
    borrowed = dict(CLEAN)
    borrowed["garage-deck.html"] = page(
        "https://6s-success.com/assets/img/rooms/ch32-image01.jpg")
    problems = preflight.check_deck_og_image_honest(borrowed)
    if not any("garage-deck.html" in p and "zone hero" in p
               for p in problems):
        fails.append("a borrowed Kitchen photo on the Garage deck was NOT "
                      "caught: %s" % problems)
    if not any("identical" in p for p in problems):
        fails.append("the resulting duplicate-image-across-decks case was "
                      "NOT caught: %s" % problems)

    # 3. A real-photo room (Entryway) drifted onto the wrong chapter photo.
    wrong_chapter = dict(CLEAN)
    wrong_chapter["entryway-deck.html"] = page(
        "https://6s-success.com/assets/img/rooms/ch35-image01.jpg")
    problems = preflight.check_deck_og_image_honest(wrong_chapter)
    if not any("entryway-deck.html" in p for p in problems):
        fails.append("Entryway's og:image drifting off its own real photo "
                      "(ch31) was NOT caught: %s" % problems)

    # 4. og:image and twitter:image disagree.
    mismatched = dict(CLEAN)
    mismatched["kitchen-deck.html"] = page(
        "https://6s-success.com/assets/img/rooms/ch32-image01.jpg",
        tw="https://6s-success.com/assets/img/rooms/ch31-image01.jpg")
    problems = preflight.check_deck_og_image_honest(mismatched)
    if not any("does not match" in p for p in problems):
        fails.append("a mismatched og:image/twitter:image pair was NOT "
                      "caught: %s" % problems)

    # 5. Against the real thing: the actual six committed deck pages, not
    #    synthetic stand-ins. This is the check that would have caught the
    #    real defect this gate was built to fix.
    real_pages = {}
    for fname in CLEAN:
        path = os.path.join(ROOT, "site", fname)
        if os.path.exists(path):
            real_pages[fname] = open(path, encoding="utf-8").read()
    if len(real_pages) < len(CLEAN):
        fails.append("not all six real deck pages exist; the real-site "
                      "case could not run against all of them: found %s"
                      % sorted(real_pages))
    problems = preflight.check_deck_og_image_honest(real_pages)
    if problems:
        fails.append("the real committed deck pages have a live og:image "
                      "problem: %s" % problems)

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("OK  gate_deck_og_image_honest: 5/5 cases pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
