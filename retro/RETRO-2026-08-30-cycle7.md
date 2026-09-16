# Retrospective, seventh cycle ending 2026-08-30

Five commits. The most important one corrected a claim in our own operational
record rather than shipping anything new.

---

## What went well

**Checked the blocker first, again, and it paid.** The cycle opened by
measuring the outage rather than assuming the previous cycle's report still
held. It does: 6 of 6 live payment links still deactivated. That single check
then turned out to matter for a second reason.

**Caught STATUS.md quietly closing an open problem.** The previous update
described `ops/check_live_links.py` as "the code fix" and said whether "the
redeployed site" is taking money again was unverifiable from that sandbox.
Both readings are wrong and the second is the dangerous one: a session reading
that would conclude the work was done and only the confirmation was missing.
There is no code fix. The detector found the outage and changes nothing on the
live site, and the repository's links were never wrong, which is the entire
point of the finding. This session has both egress and a Stripe credential, so
the open question is now closed and the answer is no.

**Every link to this site stops looking like every other link.** All 114 zone
pages advertised the same generic room map as their social and answer-engine
preview, on the pages most likely to be shared, while 102 of them had a
photograph of their own subject sitting unused. Verified every referenced file
exists rather than trusting the path construction, because a preview that
404s is worse than the generic one it replaced.

**The 13 without a photograph keep the room map on purpose.** A real generic
image beats a broken specific one, and room pages keep it too, because a room
is twenty zones and no single zone photograph represents it honestly.

---

## What did not go well

**My own alt text fix was wrong three times, and each was visible only in the
output.** Comparing against the published name trimmed nothing, because "The
Shoes and Boots" and "shoe and boot zone" share no prefix. Trimming a fixed
fourteen characters left the word "zone" stranded at the front of the
sentence. Prefixing "The" produced "The The Shoes and Boots" and "The Your Own
Nightstand" on the same run.

Every one of those would have passed a code review. None survived reading the
rendered attribute. That is now the fourth cycle where the defect was invisible
in the source and obvious in the artefact, and the only reason it did not ship
is that I looked.

**I wrote the defect I then fixed.** The duplicated alt text was mine, from the
cycle that added the hero images. I wrote the caption honestly and never read
the attribute aloud.

**The record needed correcting because two agents wrote about the same events
from different vantage points.** The cloud operator read a retrospective and
credited the owner with the operator's work, then inferred a deploy that never
happened. Neither was careless; both came from writing about work rather than
measuring it. The lesson is not "trust the other agent less", it is that a
status file should carry measurements, not summaries of summaries.

---

## What to change next cycle

**Anything that renders gets read after it renders.** Alt attributes, PDF
text, generated titles, preview URLs. Four cycles running, this is where the
defects are.

**Status claims carry their measurement or they do not go in.** "The fix is on
main" is a summary. "6 of 6 live links deactivated, measured from a session
with egress and a credential" is a fact with a method attached, and it cannot
be misread by the next session as progress.

**Stop deferring the last mile items.** The 13 zones without a photograph, the
duplicate product names, and the articles that ask a first-time reader for $19
before offering the free tool are all still open, and all three are small.

---

## Numbers

| | |
|---|---|
| Live payment links dead | 6 of 6, unchanged, measured this cycle |
| Days the outage has been open | at least 4 |
| Zone pages with their own preview image | 102 of 114 |
| Preview images referenced but missing | 0 |
| Alt texts with a defect, after the fix | 0 of 102 |
| Attempts that fix took | 3 |
| Status claims corrected | 2 |
| Preflight | every gate passes, 3 warnings, two of them the outage |
| Revenue | $19, unchanged |
