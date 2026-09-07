#!/usr/bin/env python3
"""
Prove ops/linkedin_posts.py's "N carry a link" line matches the real posts.

Found 2026-09-07 reading the file cold: build() hardcoded "Three carry a
link and seven do not, on purpose" into the preview text Phil reads before
publishing these by hand, but only 2 of the 10 POSTS entries actually
contain a 6s-success.com link. The claim was wrong from the file's one and
only commit, not a regression, just never checked against the content it
describes: the exact "the file Phil reads must not state the wrong count"
shape this project already fixed once today for
content/images/prompts/tier-0-prompts.md.

Fixed by computing with_link/without_link from POSTS itself in build(), so
the header and the content share one source and cannot drift apart again.
This test recomputes the real split independently (a plain substring scan,
not a call into build()'s own logic) and checks build()'s printed text
states that same number, so a future hand-edit that hardcodes words again
is caught here instead of by the next person who happens to count by eye.
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

import linkedin_posts as lp                                    # noqa: E402


def main() -> int:
    failures = []

    real_with = sum(1 for _, body in lp.POSTS if "6s-success.com" in body)
    real_without = len(lp.POSTS) - real_with

    _, text = lp.build()
    m = re.search(r"^(\w+) carry a link and (\w+) do not, on purpose\.",
                  text, re.MULTILINE)
    if not m:
        failures.append(
            "build() output is missing the link-count line entirely: "
            f"{text[:200]!r}")
    else:
        words = {v: k for k, v in lp.NUMBER_WORDS.items()}
        stated_with = words.get(m.group(1))
        stated_without = words.get(m.group(2))
        if stated_with != real_with or stated_without != real_without:
            failures.append(
                "build() claims '%s carry a link and %s do not' but only "
                "%d of %d POSTS actually contain a 6s-success.com link." %
                (m.group(1), m.group(2), real_with, len(lp.POSTS)))

    # A future eleventh post, or one with zero/all links, must still render
    # as a word rather than crash with a KeyError.
    if real_with not in lp.NUMBER_WORDS or real_without not in lp.NUMBER_WORDS:
        failures.append(
            "real link counts (%d with, %d without) fall outside "
            "NUMBER_WORDS, which build() needs to render them as words" %
            (real_with, real_without))

    if failures:
        print("FAIL")
        for f in failures:
            print(" -", f)
        return 1
    print("ok: linkedin_posts.py's link-count line matches the real posts "
          "(%d with, %d without)" % (real_with, real_without))
    return 0


if __name__ == "__main__":
    sys.exit(main())
