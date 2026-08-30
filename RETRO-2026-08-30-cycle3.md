# Retrospective, third cycle ending 2026-08-30

Four commits. The cycle found that none of the last three cycles' work is
reaching anybody, and then broke every gate in the repository while fixing it.

---

## What went well

**Asking a question nobody had asked.** Two cycles produced 102 reviewed zone
photographs and 71 clean card fronts. Before starting a third, the obvious
check: is any of it live? It is not. Production is serving a build from weeks
ago, and all four of the homepage's assets differ from the repository. That is
not a small finding. It means the last three retrospectives all reported work
that reached zero customers.

**`ops/verify_deploy.py` was passing 10 of 10 the whole time.** Every one of
those checks is true and none of them ask whether the site is current. The site
answers 200, the legal pages load, a missing path returns 404. "Working" and
"current" are different questions, and only one was ever being asked. The
dashboard had the matching half: "102/114 zone pages carry a reviewed picture"
is measured honestly off the repository, where it is true, and a reader takes
it as a fact about the website. It was a fact about a folder.

**The fix needed no new machinery.** `fingerprint_assets.py` already stamps
each asset reference with a hash of that file's contents, so the live homepage
states in its own HTML which version it expects. Comparing that to the file on
disk is exact, with no version endpoint and nothing to keep in sync.

**This cycle's rule was applied while writing, and caught two bugs.** The
content probe was hard coded to the Landing Spot, which is one of the twelve
zones whose image failed review, so it compared absent against absent and would
have read as current forever. And the dashboard's first version caught every
exception and reported "6s-success.com could not be reached" when what had
actually happened was a `NameError` in `dashboard.py`, because `sys` was never
imported. Both are the defect the file was written to prevent, wearing
different clothes. Both were visible because the check now says what it looked
at.

**Four verdicts, all proved.** A check that has only ever printed one verdict is
a hypothesis. `ops/tests/test_deploy_freshness.py` exercises current, stale,
unreachable, and the case that matters most: assets matching while the content
marker is absent, which asset hashes alone would call current. That is exactly
what a partial deploy leaves behind.

---

## What did not go well

**I committed unresolved conflict markers into `ops/preflight.py`.** Rebasing
onto the cloud operator's work conflicted in three generated dashboard files. I
resolved those and ran `git add -A`, which also staged `preflight.py`, still
conflicted, which nothing had asked me about. The commit went through with
three markers inside the file that runs every other gate. Python could not
parse it. **Every gate in this repository was dead, and the commit that killed
them was one adding a gate.**

I found it only because I checked for markers on a hunch after the rebase. If I
had pushed and moved on, the next several cycles would have run a preflight
that silently did nothing while printing nothing, which is the worst possible
version of this project's recurring defect and one I would have built myself.

**Resolving generated files by hand was the wrong instinct, briefly.** All three
dashboard conflicts were in files a script writes. Merging them by hand is
meaningless; the right move is to take either side and regenerate, which is
what I did, but only after starting to read the diffs.

**Three separate heredoc escaping failures.** `\n` inside a Python string
written through a shell heredoc broke an f-string twice and a regex once. Each
cost a round trip. The pattern is known and I keep walking into it.

---

## What to change next cycle

**Never `git add -A` during a rebase or merge.** Stage the files actually
resolved, by name. The blanket add is what turned a three file conflict into a
dead gate suite.

**A gate exists for it now.** `gate_conflict_markers` scans every text file and
fails on any unresolved conflict, reporting what it scanned rather than only
what it found. Proved it fails by planting a conflicted file.

**Escalate deployment on the dashboard, not just report it.** Redeploying is now
the first item under What needs you, above the decision queue, because it is
the one step this system cannot take itself and the one that makes everything
else reach nobody. Next cycle should consider whether a stale deploy should
turn the overall verdict red rather than yellow.

**Stop writing Python through heredocs when the code contains escapes.** Write
the file, then edit it.

---

## Numbers

| | |
|---|---|
| Assets on production differing from the repository | 4 of 4 |
| Zone pages carrying a photograph, live | 0 of 102 |
| Cycles whose output has reached a customer | 0 of the last 3 |
| Gates dead due to my own conflict markers | all of them, for one commit |
| Freshness verdicts proved by test | 4 of 4 |
| Preflight | every gate passes, 2 warnings, one of them the stale deploy |
| Revenue | $19, unchanged |
