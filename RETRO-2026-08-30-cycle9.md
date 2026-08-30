# Retrospective, ninth cycle ending 2026-08-30

Four commits, all of them repairing checks rather than adding features. Two of
the three things fixed were checks I had written in the previous two cycles
that did not do what they said.

---

## What went well

**The gate I wrote last cycle was wrong in the most useful way.** It failed on
the most careful sentence on the site: deck.html reads "The 72 cards shown, 88
written", which is exactly true. 72 of the 88 cards have artwork in the gallery
today and the deck is 88 written. A gate that fires on precision teaches people
to ignore it, so it now allows a count that appears alongside the real total
and still fails on a bare wrong number. Both behaviours proved.

**The two numbers that disagreed became a gate.** Last cycle's defects were
found only by printing two counts side by side. `gate_image_coverage` now
asserts that pages carrying a photograph, pages advertising one, and approved
images are the same number, and prints all three whether it passes or fails,
because the whole lesson was that they are only useful together.

**The carry forward's real failure mode was found and closed.** It worked
exactly once. It carried the previous run's revenue, so the first blind run
carried $19 correctly and wrote "not measured" into state. The next blind run
found that and had nothing to carry. One credential-less run poisoned every run
after it, and the dashboard went back to reporting no revenue for a business
that has taken a payment. The last measured figure now lives under its own key
and only a measuring run writes it.

---

## What did not go well

**Two of my own checks were decorative.** The deck count gate cried wolf on a
true sentence. The carry forward degraded to useless after one blind run. Both
passed their tests, and in the carry forward's case the test covered four cases
and missed the fifth, which is the one that happened. Writing a test is not the
same as writing the test for the thing that will go wrong.

**A backslash was eaten by a heredoc for the third time in this project.** The
word boundaries in a regex arrived as literal backspace bytes, 0x08, so the
expression matched nothing at all while reading perfectly in a diff. The gate
then silently allowed everything it existed to catch. Found by printing the
repr of the line rather than looking at it. My own retrospective told me to
stop writing Python with escapes through heredocs two cycles ago, and I did it
again anyway.

**My first proof of the new gate was a false proof.** I edited a page to
advertise a picture it does not show, ran preflight, and it stayed green. The
page I picked had gained its own photograph earlier in the session, so my probe
changed nothing. Had I stopped there I would have committed a gate I believed
was proved and was not.

---

## What to change next cycle

**Write the test for the failure that will actually happen, not four that
won't.** The carry forward had four passing cases and shipped broken. The case
that mattered was "two blind runs in a row", which is the ordinary operating
condition of this system, and I did not write it because it was not the
interesting case.

**A probe that leaves the gate green has not proved anything.** Check the probe
changed what you think it changed before drawing a conclusion from the result.

**Never put a backslash in a patch written through a shell.** Build it from
chr(92), or write the file. Third occurrence, and the first two also cost a
round trip each.

---

## Numbers

| | |
|---|---|
| Live payment links dead | 6 of 6, day four, measured again |
| Checks repaired that I had written | 2 |
| Gates added | 1, proved on the real defect shape |
| False proofs caught before committing | 1 |
| Backslashes eaten by a heredoc | 1, third occurrence |
| Test cases added for the failure that happened | 2 |
| Preflight | every gate passes, 3 warnings, two of them the outage |
| Revenue | $19, and the dashboard can no longer forget it |
