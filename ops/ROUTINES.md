# The scheduled routines, and why the cadence looks odd

Three cloud routines run against this repository. This file exists because the
schedule is not obvious from any one of them, and because a routine nobody can
find is a routine nobody can fix.

Created 2026-09-10 on Phil's instruction: review current state, backlog and
progress every 30 minutes, and initiate new work if the previous work is
completed.

## The schedule

| When | Routine | Id | Job |
|---|---|---|---|
| :10 hourly | 6S Success agile PM (:10) | `trig_01KYMpAJo7UHBMtUYmqXj25L` | review, close, and do one small thing |
| :40 hourly | 6S Success agile PM (:40) | `trig_01JCURkStiuxTMyZDNbVGumL` | review, then hand the next item to the operator |
| :43 hourly | 6S Success hourly operator | `trig_011oe2y7KR3AiPxUTd6b9P6c` | the substantial work of the cycle |

That gives a project-management review every 30 minutes, which is what was
asked for, and a full working cycle every hour.

## Why two PM routines instead of one every 30 minutes

Cloud routines have a **one hour minimum interval**. `*/30 * * * *` is rejected.
So a 30 minute cadence needs two routines half an hour apart, and that is what
these are: one prompt in two copies, differing only in what each does with the
slot.

## Why :40 and :43 are three minutes apart

Deliberate, and it is the point of the pairing. The :40 PM reads the state and
writes a single line into `ops/NIGHTLY-LOG.md`:

    NEXT FOR THE OPERATOR: <item>, because <one clause>.

The operator starts three minutes later and finds it. So the decision about
what to work on is made by a routine whose whole job is deciding, and the
execution is done by the routine that has an hour to do it. The :10 PM has no
operator behind it, so it does its own small closing work instead.

## The division of labour, which is the part that matters

The PM routines are told to **prefer small and closing over large and opening**:
close an item already done but still listed as open, verify a claim an earlier
cycle did not check, fix a red gate, correct a document that no longer matches
reality. Anything needing hours goes to the operator, named explicitly in the
log.

This is aimed at one failure this repository has had repeatedly: work that is
committed but not finished, and claims recorded but never verified. Both PM
prompts open with the same question, before anything else happens: **is the
previous work actually finished?** Finished means shipped and verified, not
committed. If it is not, finishing it is that run's work and nothing new starts.

## Collision

Three routines can touch the repository in the same hour. All three are told to
merge rather than force, and to re-derive a generated file rather than resolve
its conflict by hand, which is the rule that keeps `ops/state.json`,
`site/sw.js` and `site/build-id.txt` correct.

## Changing them

`ops/routine-prompt.md` holds the operator's prompt verbatim and is kept in step
with the live routine. The two PM prompts live only in the routines themselves
today. If you edit a routine in the Routines UI, the copy here goes stale, which
is exactly what happened to `routine-prompt.md` once already: it sat at 6,156
bytes against a live 9,462 and told anybody reading it a version of the job that
had not run for weeks.
