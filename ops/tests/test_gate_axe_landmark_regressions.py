#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_axe_landmark_regressions() (and its two pure
helpers, unmarked_callout_asides() and intro_div_outside_landmark())
correctly flag the two axe-core landmark defects found 2026-11-25/26 in
site/downloads/, outside gate_aside_landmarks_labeled's own scope
(all_pages() deliberately excludes downloads/): 137 inline "callout" boxes
in the free sample book exposed as unnamed complementary landmarks nested
inside their own chapter section (landmark-complementary-is-top-level),
and three standalone printable downloads opening <body> straight onto
<div class="intro"> with no landmark around it at all (axe's region rule).

Run:  python ops/tests/test_gate_axe_landmark_regressions.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    # 1. A callout aside with no role= override at all: the real shape
    #    found on 137 nodes in the free sample book.
    bare = '<aside class="callout tip"><p>text</p></aside>'
    if preflight.unmarked_callout_asides(bare) != 1:
        fails.append("a bare callout aside was not flagged")

    # 2. The real fix shape: role="note" on the same tag, must pass.
    fixed = '<aside class="callout tip" role="note"><p>text</p></aside>'
    if preflight.unmarked_callout_asides(fixed) != 0:
        fails.append("a role=\"note\" callout aside was wrongly flagged")

    # 3. Any explicit role at all removes the implicit complementary
    #    mapping, so the check is "has a role", not "has exactly note".
    other_role = '<aside class="callout win" role="group">x</aside>'
    if preflight.unmarked_callout_asides(other_role) != 0:
        fails.append("a differently-roled callout aside was wrongly flagged")

    # 4. A plain disclosure/safety <aside> (no "callout" class) is a
    #    different, deliberately-landmark pattern gate_aside_landmarks_
    #    labeled already owns; this helper must not touch it.
    disclosure = '<aside class="disclosure" aria-label="x">y</aside>'
    if preflight.unmarked_callout_asides(disclosure) != 0:
        fails.append("a non-callout aside was wrongly flagged")

    # 5. Multiple unmarked callouts on one page: must count all of them,
    #    not just detect "any".
    three = bare + bare + fixed
    if preflight.unmarked_callout_asides(three) != 2:
        fails.append("multiple unmarked callouts were not all counted")

    # 6. <body> opening directly onto <div class="intro">: the real shape
    #    found on all three standalone printable downloads.
    bad_intro = '<body><div class="intro"><h1>Title</h1></div><main></main></body>'
    if not preflight.intro_div_outside_landmark(bad_intro):
        fails.append("body-then-intro was not flagged")

    # 7. The real fix shape: <header> wrapping the intro, must pass.
    good_intro = ('<body><header><div class="intro"><h1>Title</h1></div>'
                  '</header><main></main></body>')
    if preflight.intro_div_outside_landmark(good_intro):
        fails.append("header-wrapped intro was wrongly flagged")

    # 8. <main> wrapping the intro directly (the other honest fix shape)
    #    must also pass.
    main_wrapped = '<body><main><div class="intro"><h1>Title</h1></div></main></body>'
    if preflight.intro_div_outside_landmark(main_wrapped):
        fails.append("main-wrapped intro was wrongly flagged")

    # 9. A page with no intro div at all must not be flagged.
    no_intro = '<body><main><h1>Title</h1></main></body>'
    if preflight.intro_div_outside_landmark(no_intro):
        fails.append("a page with no intro div was wrongly flagged")

    # 10. The real gate against the real site, including site/downloads/,
    #     which gate_aside_landmarks_labeled never reaches: must be clean
    #     today, since this cycle fixed every instance either check found.
    before = len(preflight.FAIL)
    preflight.gate_axe_landmark_regressions()
    new_fails = preflight.FAIL[before:]
    del preflight.FAIL[before:]
    if new_fails:
        fails.append(
            "gate_axe_landmark_regressions failed against the real site "
            "after this cycle's own fix: %r" % (new_fails,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: gate_axe_landmark_regressions correctly flags unmarked "
          "callout asides and landmark-less intro divs, and is clean "
          "against the real, fixed site")
    return 0


if __name__ == "__main__":
    sys.exit(main())
