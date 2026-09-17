#!/usr/bin/env python3
"""
Prove ops/reflow.py keeps a trailing call-to-action line on its own line,
the exact promise its own docstring makes: "a link buried mid paragraph is
a link nobody follows."

Found 2026-09-10: TAIL_RE only matched a last block naming "6S Success",
"6s-success.com" or "Chapter <number>". Checked directly against the real
311-post corpus (ops/corpus_posts.py's own pool("linkedin-post", raw=True)):
64 distinct trailing blocks point the reader at the free chapter without
using any of those three phrasings ("Read the free chapter.", "Grab the
free Use Test card in the online book", "Curious about the whole method?
The chapter is free online.") and so were left fused into the paragraph
above, the exact mid-paragraph link burial this function exists to
prevent. These are real drafts Phil reads and sends himself every morning
via the linkedin-drafts.yml workflow. Fixed by widening TAIL_RE to the
same free-chapter vocabulary ops/corpus_posts.py's own FREE_CLAIM pattern
already uses elsewhere in this file, plus "online book".

Found 2026-09-17, cold-read: reflow()'s own colon-merge rule lowercases
whatever follows a colon to read as one continuing sentence, with a guard
meant to keep the pronoun "I" capitalised regardless of position. The
guard only matched a literal "I " (a trailing space), so a contraction
with no space before the apostrophe, "I've", "I'm", "I'll" or "I'd", still
got lowercased to "i've" etc, reproduced directly before being fixed in
ops/reflow.py itself. Also fixed here: this file's own failure message
hardcoded "6" as the total check count while 8 checks already ran, the
same self-inconsistent-count class this repository's gates exist to catch
elsewhere; it now counts itself.

Run:  python ops/tests/test_reflow.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import reflow                                                  # noqa: E402

FAILS = []
CHECKS = [0]


def check(name, cond):
    CHECKS[0] += 1
    print(("  [ok] " if cond else "  [FAIL] ") + name)
    if not cond:
        FAILS.append(name)


def main():
    # The real, previously-missed shape, taken verbatim from the corpus (a
    # 3-block reduction of this same post coincidentally landed right even
    # on the old code, because the paragraph-count arithmetic happened to
    # isolate the last block anyway; this is the real 6-block post, where
    # it did not). No "6S Success", no "6s-success.com", no "Chapter
    # <digit>", just "free chapter" / "online book" phrasing.
    real_case = (
        "You built a fair list. Every target has a name. And several "
        "lines still fill you with a small sinking feeling.\n\n"
        "The oven that means an hour and a caustic spray. The shower "
        "screen that never really comes clear. The floors that mean "
        "moving furniture.\n\n"
        "The target is owned. It is also dreaded. And dread, quietly, "
        "beats ownership almost every time.\n\n"
        "The list does not fail because it was unfair. It fails because "
        "the jobs on it were miserable, and miserable jobs do not get "
        "done no matter whose name is next to them.\n\n"
        "So give a dreaded target a method that is quick and works, and "
        "the dread simply drains out of it, because there is nothing "
        "left to dread.\n\n"
        "Read the free chapter in the online book."
    )
    out = reflow.reflow(real_case)
    paras = out.split("\n\n")
    check("the CTA line survives as its own final paragraph, not fused",
          paras[-1] == "Read the free chapter in the online book.")
    check("the CTA sentence does not also appear earlier in the output",
          "Read the free chapter" not in "\n\n".join(paras[:-1]))

    # A second real shape from the corpus: a question-style CTA with no
    # chapter number and no book name at all.
    q_case = (
        "Group by what you do, not by what things are.\n\n"
        "That is the whole move of this chapter.\n\n"
        "Read it free online."
    )
    out2 = reflow.reflow(q_case)
    paras2 = out2.split("\n\n")
    check("a bare 'Read it free online.' CTA also stays isolated",
          paras2[-1] == "Read it free online.")

    # The original, already-working shape must still work (no regression).
    old_case = (
        "The fix is not more willpower. It is a quicker method.\n\n"
        "This is from Chapter 18 of 6S Success: Home Edition. "
        "Read it free online."
    )
    out3 = reflow.reflow(old_case)
    paras3 = out3.split("\n\n")
    check("the original 'Chapter 18 of 6S Success' shape still isolates",
          paras3[-1] == "This is from Chapter 18 of 6S Success: Home Edition. "
                        "Read it free online.")

    # A single-block post has nothing to pop as a tail: len(cleaned) == 1
    # must not empty the body.
    single = "Read the free chapter in the online book."
    out4 = reflow.reflow(single)
    check("a post that is only the CTA is not emptied",
          out4.strip() == single)

    # Filler stripping must still work alongside the wider tail match.
    filler_case = (
        "Here is the thing. The method matters more than the willpower.\n\n"
        "Read the free chapter."
    )
    out5 = reflow.reflow(filler_case)
    check("filler opener still stripped",
          "Here is the thing" not in out5)
    check("CTA still isolated when filler precedes it",
          out5.strip().endswith("Read the free chapter."))

    # A last block that merely happens to contain the word "free" in an
    # unrelated sense must not be treated as a call to action.
    unrelated = (
        "The first pass took an hour.\n\n"
        "Feel free to skip the drawer if it is already sorted."
    )
    out6 = reflow.reflow(unrelated)
    check("an unrelated use of 'free' in the last block is not misread as a "
          "CTA and split off pointlessly",
          out6.strip() == "The first pass took an hour. "
                          "Feel free to skip the drawer if it is already sorted.")

    # Found 2026-09-17: a block merged after a colon that starts with a
    # contraction of the pronoun "I" (no trailing space before the
    # apostrophe) was still lowercased to "i've"/"i'm"/etc, because the old
    # guard only matched a literal "I " with a space. The pronoun must stay
    # capitalised in every one of these shapes; an ordinary capitalised word
    # that merely starts with the letter I ("Idaho", "Its") must still be
    # lowercased, since that is the whole point of this merge rule.
    for pronoun_case, expected_tail in [
        ("I've been doing this wrong for years.", "I've been"),
        ("I'm going to explain why.", "I'm going"),
        ("I'll show you.", "I'll show"),
        ("I'd rather not.", "I'd rather"),
        ("I am fine with that.", "I am fine"),
    ]:
        out = reflow.reflow("Three things people mix up:\n\n" + pronoun_case)
        check(f"pronoun I stays capitalised in {pronoun_case!r}",
              expected_tail in out)
    for other_case, expected_tail in [
        ("Idaho is not a pronoun.", "idaho is not"),
        ("Its own thing broke.", "its own thing"),
    ]:
        out = reflow.reflow("Three things people mix up:\n\n" + other_case)
        check(f"a non-pronoun word starting with I still lowercases in "
              f"{other_case!r}", expected_tail in out)

    print()
    if FAILS:
        print("%d of %d checks failed: %s" % (len(FAILS), CHECKS[0], FAILS))
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
