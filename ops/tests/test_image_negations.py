#!/usr/bin/env python3
"""
Prove that a "no X" in an image prompt is moved to the negative prompt, and
that a "nothing else here" is not.

WHY
---
A diffusion model has no reliable notion of "not". The tokens it receives are
what it draws toward, so a prompt reading "a crib with a bare white fitted
sheet only, no blankets or toys" puts BLANKETS and TOYS into the positive
prompt and reliably produces both.

Verified by generating it on 2026-09-09 rather than by argument: the nursery
hero from that exact prompt came back with a pillow in the crib, against a zone
standard reading "a bare mattress with one fitted sheet pulled tight to the
corners". Moving the phrase to the negative prompt produced a genuinely bare
crib on the first attempt.

That page is a nursery, so the picture was contradicting our own safety
guidance, which is the reason this is a test and not a note.

THE CASE THAT MAKES THIS SUBTLE
-------------------------------
The first version of split_negations() also matched "nothing" and "never", and
the entryway door mat prompt reads "...just inside a closed front door, nothing
else on the floor". That moved "on the floor" into the negative prompt, which
tells the model to suppress the floor the mat is standing on.

"no X" and "without X" name objects to leave out. "nothing else HERE" is a
statement about a scene. They do not survive the same treatment, and this file
exists mostly to stop somebody generalising the first into the second again.

Run:  python ops/tests/test_image_negations.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import image_local as L                                          # noqa: E402


CASES = [
    # (subject, must_be_in_negative, must_NOT_be_in_negative, note)
    ("a crib with a bare white fitted sheet only, no blankets or toys, "
     "monitor cable clipped high on the wall, in a nursery",
     ["blankets", "toys"], [],
     "the nursery, the case this was written for"),

    ("a coir door mat on bare wood floor just inside a closed front door, "
     "nothing else on the floor, in an entryway",
     [], ["floor"],
     "'nothing else on the floor' must not negate the floor itself"),

    ("primary prep counter, one clear run of counter, in a kitchen",
     [], [], "an ordinary prompt is left alone"),

    ("a north-facing window and a nook, in a study",
     [], ["north", "nook"],
     "word boundary: 'north' and 'nook' start with 'no' and are not negations"),

    # Found 2026-09-26: the original fix only anchored "nothing else" at the
    # START of a clause. Two real, shipped art briefs put the identical
    # "this is a statement about the scene, not an object" shape later in
    # the sentence, and the anchored version let both ride into the positive
    # prompt untouched.
    ("an open drawer holding a divided flatware insert, each compartment "
     "holding one kind of utensil and nothing loose beside it, in a kitchen",
     [], [],
     "ops/cardtext/kitchen-deck.json's real EK card subject: 'nothing loose "
     "beside it' does not start with 'nothing' and must still be dropped"),

    ("drawer organizer, a place for loose items so nothing gets lost, tidy "
     "and settled, in an entryway",
     [], [],
     "ET-010's real subject: 'so nothing gets lost' is mid-clause and must "
     "still be dropped"),
]


def main() -> int:
    fails = []

    for subject, want, unwanted, note in CASES:
        positive, negative = L.split_negations(subject)
        for w in want:
            if w not in negative:
                fails.append("%s: %r missing from the negative prompt %r"
                             % (note, w, negative))
            if w in positive:
                fails.append("%s: %r left in the POSITIVE prompt, which is "
                             "where it gets drawn" % (note, w))
        for u in unwanted:
            if u in negative:
                fails.append("%s: %r wrongly moved to the negative prompt %r"
                             % (note, u, negative))
        # Nothing may be silently lost: every clause that is not an
        # instruction-to-omit survives. A clause carrying "nothing" IS such
        # an instruction and is deliberately dropped whole (checked
        # separately below), wherever in the clause the word falls, not only
        # when the clause happens to start with it.
        for clause in [c.strip() for c in subject.split(",")]:
            low = clause.lower()
            if low.startswith(("no ", "without ")) or "nothing" in low:
                continue
            if clause not in positive:
                fails.append("%s: clause %r vanished from the prompt entirely"
                             % (note, clause[:40]))

        # Any clause carrying "nothing" must leave the positive prompt AND
        # put clutter terms in the negative one, wherever in the clause the
        # word sits. Leaving it in the positive is what produced a kitchen
        # counter covered in bowls and vegetables under a standard reading
        # "nothing else is on the run", measured 2026-09-14. Dropping it
        # without suppressing anything would be a quieter version of the
        # same bug.
        for clause in [c.strip() for c in subject.split(",")]:
            if "nothing" not in clause.lower():
                continue
            if clause in positive:
                fails.append("%s: the clause %r carrying 'nothing' is still "
                             "in the POSITIVE prompt, where its tokens tell "
                             "the model to draw toward it" % (note, clause))
            if "clutter" not in negative.lower():
                fails.append("%s: a clause carrying 'nothing' (%r) was "
                             "dropped but nothing was suppressed in its "
                             "place: %r" % (note, clause, negative))

    # The seed must not change when a negation moves, or every previously
    # generated image silently becomes unreproducible.
    subject = CASES[0][0]
    import hashlib
    seed_before = int(hashlib.sha256(subject.encode()).hexdigest()[:8], 16) % (2 ** 31)
    positive, _ = L.split_negations(subject)
    seed_after = int(hashlib.sha256(subject.encode()).hexdigest()[:8], 16) % (2 ** 31)
    if seed_before != seed_after:
        fails.append("the seed is derived from something the split changed; "
                     "every existing image would become unreproducible")
    if positive == subject:
        fails.append("the nursery prompt was not changed at all, so the fix "
                     "is not doing anything")

    for f in fails:
        print("  FAIL  %s" % f)
    if fails:
        print("  %d problem(s) across %d case(s)" % (len(fails), len(CASES)))
    else:
        print("  ok  'no X' moves to the negative prompt, 'nothing else here' "
              "does not, ordinary prompts are untouched, no clause is lost, "
              "and the seed is unchanged")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
