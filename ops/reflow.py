#!/usr/bin/env python3
"""
Turn a chopped-up social post back into solid paragraphs.

WHY
---
Phil read the drafts and said they sound like AI slop, and asked for a solid
paragraph with crisp sentences instead. He is right, and the reason is worth
writing down because it is invisible until somebody names it.

The substance of these posts is good. The FORMAT is the influencer cadence:
every sentence promoted to its own paragraph, a one line dramatic opener, a gap,
another one liner. That layout is now so strongly associated with generated
content that it overrides the writing inside it. A reader decides it is slop
from the shape before reading a word.

WHAT THIS FIXES, AND WHAT IT LEAVES ALONE
-----------------------------------------
It joins the fragments back into paragraphs and removes the specific tics that
signal filler. It does not rewrite sentences, invent transitions, or change what
the post says. The words stay Phil's; only the shape changes.

THE TICS IT REMOVES, and each is removed rather than reworded because a reworded
filler transition is still a filler transition:

    Here is the thing.        Here's the thing.       The thing is.
    But here is the truth.    And here is why.        Let that sink in.
    Sound familiar?           Here is what I mean.

Run:  python ops/reflow.py --demo
"""
from __future__ import annotations

import re
import sys

# Openers that exist only to fill a beat. Matched at the start of a sentence.
FILLER = [
    r"here is the thing[.,]?\s*", r"here's the thing[.,]?\s*",
    r"the thing is[.,]?\s*", r"but here is the truth[.,]?\s*",
    r"and here is why[.,]?\s*", r"here is why[.,]?\s*",
    r"let that sink in[.,]?\s*", r"sound familiar\?\s*",
    r"here is what i mean[.,]?\s*", r"and that is the point[.,]?\s*",
    r"but wait[.,]?\s*", r"the truth\?\s*", r"the reality\?\s*",
    r"quick one[.,]?\s*", r"one more thing[.,]?\s*",
    r"and that is it[.,]?\s*", r"simple as that[.,]?\s*",
]
FILLER_RE = re.compile("|".join(FILLER), re.I)


def reflow(text: str, max_paras: int = 2) -> str:
    """Join one-line paragraphs into solid ones and drop filler openers.

    max_paras is a ceiling rather than a target. A post with a genuine two part
    structure keeps it; a post that was chopped into six keeps its meaning but
    reads as prose.
    """
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    if not blocks:
        return text.strip()

    # Strip filler at the head of any block, then re-capitalise what follows.
    cleaned = []
    for b in blocks:
        b2 = FILLER_RE.sub("", b).strip()
        if b2 and b2[0].islower():
            b2 = b2[0].upper() + b2[1:]
        if b2:
            cleaned.append(b2)

    # A trailing block that names the book is the call to action and stays on
    # its own line, because a link buried mid paragraph is a link nobody follows.
    tail = ""
    if cleaned and re.search(r"6S Success|6s-success\.com|Chapter \d+",
                             cleaned[-1], re.I) and len(cleaned) > 1:
        tail = cleaned.pop()

    # A block ending in a colon introduces the one after it, so joining them
    # with a space reads as a stumble: "Three things people mix up: Cleaning
    # removes dirt." Merge those pairs first, before any distribution.
    merged = []
    for b in cleaned:
        if merged and merged[-1].rstrip().endswith(":"):
            # What follows a colon continues the sentence, so it does not take
            # a capital. Leaving one reads as two sentences fused by accident.
            b = b[0].lower() + b[1:] if b and b[0].isupper() and not b.startswith("I ") else b
            merged[-1] = merged[-1].rstrip() + " " + b
        else:
            merged.append(b)
    cleaned = merged

    # A single short opening line followed by a gap is the exact cadence being
    # fixed, so a first block under twelve words is pulled into the one after
    # it rather than left standing alone.
    if len(cleaned) > 1 and len(cleaned[0].split()) < 12:
        cleaned = [cleaned[0] + " " + cleaned[1]] + cleaned[2:]

    # Distribute what is left across at most max_paras, keeping order.
    n = min(max_paras, max(1, len(cleaned)))
    per = max(1, round(len(cleaned) / n))
    paras, cur = [], []
    for b in cleaned:
        cur.append(b)
        if len(cur) >= per and len(paras) < n - 1:
            paras.append(" ".join(cur))
            cur = []
    if cur:
        paras.append(" ".join(cur))

    out = "\n\n".join(p.strip() for p in paras if p.strip())
    if tail:
        out += "\n\n" + tail
    # Collapse any double spaces the joins introduced.
    return re.sub(r" {2,}", " ", out).strip()


if __name__ == "__main__":
    if "--demo" in sys.argv:
        sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
        from corpus_posts import pool
        # raw=True bypasses corpus_posts.clean()'s own reflow() call, which
        # pool() otherwise already applies to every post it serves. Without
        # this, BEFORE and AFTER here were identical on every run: both had
        # already been reflowed once, so this demo could never show what the
        # fix actually changes.
        for p in pool("linkedin-post", raw=True)[:2]:
            print("=" * 66)
            print("BEFORE, as it was sent:\n")
            print(p["body"])
            print("\nAFTER:\n")
            print(reflow(p["body"]))
            print()
