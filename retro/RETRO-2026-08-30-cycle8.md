# Retrospective, eighth cycle ending 2026-08-30

Four commits. Two of my own defects found and fixed inside the same session
that created them, and one reported defect that did not survive being looked at.

---

## What went well

**A flagged defect was checked before it was fixed.** An audit reported that 27
of 30 articles ask a cold reader for $19 before offering anything free. Opening
one showed the offer band already carries "Or work this zone, free" as a
first-class second action, routing through the zone page, which is the
diagnosis step. The funnel is defensible and the finding was a summary of a
grep, not of the page. Nothing was changed. Acting on that report would have
been exactly what I keep criticising in other people's checks.

**The zone imagery is essentially done.** A fourth prompt pass recovered eight
of the last twelve, taking coverage to 110 of 114. The landing zone came back
as a wooden tray holding keys and a wallet, which is precisely what its own
standard describes and what three earlier attempts could not produce while the
prompt still named the front door. The remaining four fail for reasons I can
state rather than guess at.

**Duplicate product names are gone, and only where they collided.** Six SKUs
across three names were indistinguishable in the shop, with the room appearing
only in the blurb, so a buyer scanning 109 tiles could pick the wrong one and
be entirely right to ask for a refund. The room is appended only where a zone
name repeats, counted from the source the packs are built from rather than a
list that would drift.

**The corrected status held.** Nothing this cycle had to re-argue whether the
outage is open. It is, on day four, measured again at the top of the cycle.

---

## What did not go well

**I shipped an ordering bug and a logic bug into the same feature, in the same
session I wrote it.**

The social preview image is chosen when the page head is written, and the
images it names are produced by a script the same generator chains at the end,
so eight newly approved zones shipped pointing at the generic map while their
photograph appeared on the page. A build that only converges on a second run is
a build nobody runs twice.

Worse, the preview check asked whether a stem was present in `approved()`,
which returns every judged stem mapped to its verdict, including "no". So four
pages advertised, to every social and answer engine preview, a picture
deliberately kept off the page. That is the second time in a week that
delisting has been mistaken for withholding, and I wrote the gate for the first
one.

**Both were invisible until I compared two numbers.** 110 pages with a picture
and 114 with their own preview should not both be true. Neither bug appears in
the source, in a linter, or in any existing gate. The only reason they did not
ship is that I printed both counts next to each other.

**My cleanup script parsed the same filename wrongly twice**, deleting nothing
the first time and 684 files the second. It converged correctly only because
the build regenerates derivatives, which is luck dressed as recovery.

---

## What to change next cycle

**When a helper returns a mapping, read what it maps to.** `approved()` sounds
like a set of approved things and is a dictionary of verdicts. The name lied
and I believed the name. Any membership test against a function whose return
type is not obviously a set gets the value checked, not the key.

**Print the two numbers that should agree.** Both bugs this cycle were found
that way and neither was findable any other way. Coverage counts, file counts,
approved counts: put them on one line and look.

**A gate for the two-number check.** Pages with a picture and pages advertising
their own picture should be equal, and nothing currently asserts it. That is
the cheapest possible guard against exactly what happened today.

---

## Numbers

| | |
|---|---|
| Live payment links dead | 6 of 6, day four, measured again |
| Zone pages with a picture | 110 of 114, from 102 |
| Zone pages advertising a rejected picture | 4, now 0 |
| Stale derivative files removed from the shipped site | 684 |
| Duplicate product names | 3 across 6 SKUs, now 0 |
| Reported defects that did not survive inspection | 1 |
| Gates added | 1 |
| Preflight | every gate passes, 3 warnings, two of them the outage |
| Revenue | $19, unchanged |
