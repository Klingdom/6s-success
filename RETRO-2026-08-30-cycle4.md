# Retrospective, fourth cycle ending 2026-08-30

Four commits. No new product work. The cycle went entirely on making the
system tell the truth about itself, which turned out to be where the value was.

---

## What went well

**Checked the blocker before building on top of it.** The cycle opened by
re-running the freshness check rather than starting something new. Production
is still serving the old build. Then, instead of accepting "it needs Phil" as
established, verified there is genuinely no automated path to fix instead: no
SSH key and no VPS credential in the repository secrets, and publish-image.yml
stops at ghcr.io. It really is his click. That took two commands and turns an
assumption into a fact.

**Moved the blocker to where it is actually read.** The staleness was on the
dashboard and in preflight, and in neither place Phil looks on a Sunday. The
status PDF is what gets emailed. Its "What needs you" section listed only
decision issues, and a decision can wait a week without costing anything while
an undeployed build costs every day it sits. It now leads that section.

**Verified the redeploy will not create the exposure it could create.**
Production currently serves no card art at all: the live deck page references
zero card images and both trademark files return 404. The staleness holding
back the good work is also, accidentally, what has been keeping the bad art off
the internet. So the deploy is a value question, not a safety one. That is a
materially different risk picture and it came from four curl commands rather
than reasoning.

**Found a gap in somebody else's gate by using it.** The cloud operator's
gate_deck_art_withheld checks that the two trademarked codes are absent from
the gallery index. nginx serves any file under site/ whether a page links to it
or not, so delisting is not withholding. Checked by hand, found clean, then put
the check in the gate so it never needs doing by hand twice.

**Named a real systemic problem rather than working around it.** The committed
dashboard has been alternating between "$19" and "not measured" every cycle,
because two agents regenerate it and only one can reach the network. Read as a
timeline, that says the business keeps losing its revenue and getting it back.
The rule here was already "None is not zero"; this is the same rule facing the
other way, and it had never been stated: an absent answer must not delete a
known one.

---

## What did not go well

**A paragraph I added to the owner's PDF silently rendered nothing.** The
figures are nested under `d["state"]` while issues sit at the top level, and I
read `deploy_verdict` from the top. It returned None, the whole block was
skipped, and the PDF looked entirely correct. Found only by opening the built
PDF and searching its text. Running without error is not evidence that anything
happened.

**Shipped no product work at all this cycle.** Four commits, all infrastructure.
That is defensible when the finding is "none of the last three cycles reached a
customer", but it is the second cycle in a row where the deliverable is a
better view of the problem rather than a fix to it. Revenue is unchanged and
the constraint is unchanged.

**Nearly repeated last cycle's rebase mistake.** Rebased onto the cloud
operator's work again. This time staged by name and checked for conflict
markers immediately after, which is only a fix because I remembered; the gate
that makes it automatic was written last cycle and it did its job.

---

## What to change next cycle

**Open the artefact, not the log.** The PDF bug and last cycle's silent-probe
bug are the same mistake: reading the code's exit status instead of its output.
Anything that produces a file gets opened and searched before it is called done.

**Do product work next cycle unless something is on fire.** Two consecutive
cycles of instrumentation is the limit. The 17 remaining cards, the 12
remaining zone images, and the Entryway deck as a sellable artefact are all
sitting there, and none of them need the deploy to progress.

**Tests now run in preflight.** Both files written in the last two cycles prove
a check can return more than the verdict its environment happened to be in.
Unwired they were documentation. `gate_tests` runs them, and was proved to fail
by planting a failing test.

---

## Numbers

| | |
|---|---|
| Production still stale | 4 of 4 assets differ |
| Card art live on production | 0 files, both trademark URLs 404 |
| Automated deploy paths found | 0, confirmed rather than assumed |
| Gates added this cycle | 2 (tests, withheld-art files) |
| Gates proved failing before being trusted | 3 of 3 |
| Test files, now run by preflight | 2 |
| Product work shipped | none, second cycle running |
| Revenue | $19, unchanged |
