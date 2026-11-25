#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_aside_landmarks_labeled() (and its pure
helper, unlabeled_aside_landmarks()) correctly flags a page with 2+
<aside> elements that a screen reader cannot tell apart, the real defect
an automated axe-core pass found 2026-11-25 on 135 pages (never tested
before): every <aside> is an unnamed `complementary` ARIA landmark by
default, and this site renders two or three of them on one page without
a distinguishing aria-label.

Run:  python ops/tests/test_gate_aside_landmarks_labeled.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    # 1. A single <aside>: nothing to disambiguate, no landmark collision
    #    is possible regardless of whether it carries a label.
    one = '<aside class="notice">text</aside>'
    if preflight.unlabeled_aside_landmarks(one):
        fails.append("a single aside was wrongly flagged")

    # 2. Two <aside>s, neither labeled: the real shape found on 135 pages,
    #    two silent "complementary" landmarks.
    two_unlabeled = (
        '<aside class="disclosure" id="a">x</aside>'
        '<aside class="notice">y</aside>')
    if not preflight.unlabeled_aside_landmarks(two_unlabeled):
        fails.append("two unlabeled asides were wrongly passed")

    # 3. Two <aside>s, one labeled and one not: still indistinguishable,
    #    since the unlabeled one is still a silent landmark.
    one_labeled = (
        '<aside class="disclosure" id="a" aria-label="How these links '
        'work">x</aside><aside class="notice">y</aside>')
    if not preflight.unlabeled_aside_landmarks(one_labeled):
        fails.append("one labeled, one unlabeled was wrongly passed")

    # 4. Two <aside>s, both labeled but with the IDENTICAL label: fixes
    #    nothing, a screen reader still hears the same name twice.
    same_label = (
        '<aside class="disclosure" aria-label="How these links work">'
        'x</aside>'
        '<aside class="disclosure" aria-label="How these links work">'
        'y</aside>')
    if not preflight.unlabeled_aside_landmarks(same_label):
        fails.append("two identically-labeled asides were wrongly passed")

    # 5. Two <aside>s, each with its own distinct label: the real fix
    #    shape, must pass.
    distinct = (
        '<aside class="disclosure" aria-label="How these links work">'
        'x</aside>'
        '<aside class="notice" aria-label="Safety notice">y</aside>')
    if preflight.unlabeled_aside_landmarks(distinct):
        fails.append("two distinctly-labeled asides were wrongly flagged")

    # 6. aria-labelledby/title also count as a distinguishing name, not
    #    only aria-label.
    labelledby = (
        '<aside class="disclosure" aria-labelledby="h1">x</aside>'
        '<aside class="notice" title="Safety notice">y</aside>')
    if preflight.unlabeled_aside_landmarks(labelledby):
        fails.append("aria-labelledby/title were wrongly not recognised")

    # 7. The real gate against the real, already-fixed site: must be
    #    clean today, since this cycle fixed every instance it found.
    before = len(preflight.FAIL)
    preflight.gate_aside_landmarks_labeled()
    new_fails = preflight.FAIL[before:]
    del preflight.FAIL[before:]
    if new_fails:
        fails.append(
            "gate_aside_landmarks_labeled failed against the real site "
            "after this cycle's own fix: %r" % (new_fails,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: gate_aside_landmarks_labeled correctly flags unlabeled "
          "or identically-labeled <aside> landmarks and is clean against "
          "the real, fixed site")
    return 0


if __name__ == "__main__":
    sys.exit(main())
