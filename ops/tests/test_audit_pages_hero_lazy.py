#!/usr/bin/env python3
"""
Prove the hero-lazy check in ops/audit_pages.py does not fire on a video
thumbnail that happens to be the first <img> in source order.

Found 2026-09-11: withdrawing the kitchen--primary-prep-counter zone hero
(a real content defect, see ops/hero-verdicts.json and OWNER-ACTIONS.md)
left that page's "Watch this zone" video thumbnail, which sits inside its
own play button hundreds of words down the page, as the technically-first
<img> tag in source order. The old check assumed the first <img> in source
order is "almost always above the fold" and flagged it for being lazy
loaded, which is correct for a real hero and wrong for a click-to-play
thumbnail nobody sees until they have already read the page.

Run:  python ops/tests/test_audit_pages_hero_lazy.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import audit_pages as A                                           # noqa: E402


def names(html):
    return [n for n, _ in A.check("fixture.html", html)]


def main():
    fails = []

    # Case 1: a genuine above-fold lazy hero must still be caught.
    bad = ('<html lang="en"><head><title>T</title>'
           '<meta name="viewport" content="width=device-width">'
           '<meta name="description" content="d"></head>'
           '<body><p>Intro</p>'
           '<img src="https://x/hero.jpg" alt="" loading="lazy">'
           "<h2>More</h2></body></html>")
    if "hero-lazy" not in names(bad):
        fails.append("a genuine lazy above-fold hero was not flagged")

    # Case 2: the only image on the page is a lazy video-play thumbnail.
    # This must NOT be flagged: it is never the thing above the fold.
    video_only = ('<html lang="en"><head><title>T</title>'
                  '<meta name="viewport" content="width=device-width">'
                  '<meta name="description" content="d"></head>'
                  '<body><p>Intro</p><h2>Watch this zone</h2>'
                  '<button type="button" class="video-play">'
                  '<img src="https://x/thumb.png" alt="" loading="lazy">'
                  "</button></body></html>")
    if "hero-lazy" in names(video_only):
        fails.append("a video-play thumbnail was wrongly flagged as a lazy "
                      "above-fold hero")

    # Case 3: an eager real hero is correctly left alone (regression guard).
    eager = ('<html lang="en"><head><title>T</title>'
             '<meta name="viewport" content="width=device-width">'
             '<meta name="description" content="d"></head>'
             '<body><p>Intro</p>'
             '<img src="https://x/hero.jpg" alt="" loading="eager">'
             "<h2>More</h2></body></html>")
    if "hero-lazy" in names(eager):
        fails.append("an eager hero was wrongly flagged")

    # Case 4: a lazy hero ABOVE a later lazy video thumbnail must still be
    # caught by the real hero, not skipped just because a video exists later.
    both = ('<html lang="en"><head><title>T</title>'
            '<meta name="viewport" content="width=device-width">'
            '<meta name="description" content="d"></head>'
            '<body><p>Intro</p>'
            '<img src="https://x/hero.jpg" alt="" loading="lazy">'
            '<h2>Watch this zone</h2>'
            '<button type="button" class="video-play">'
            '<img src="https://x/thumb.png" alt="" loading="lazy">'
            "</button></body></html>")
    if "hero-lazy" not in names(both):
        fails.append("a real lazy hero before a video thumbnail was missed")

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("PASS: 4 case(s), a video-play thumbnail is excluded from the "
          "first-image check, a genuine lazy hero is still caught")
    return 0


if __name__ == "__main__":
    sys.exit(main())
