# 6S Success Daily Operating Loop

> Canonical description of the recurring autonomous work cycle for 6S Success. Required by `CLAUDE.md` section 56 and referenced from `STATUS.md`. Written 2026-08-24 because the loop existed in practice before it existed in writing.

## 1. Purpose

`DAILY-LOOP.md` documents the cycle that actually runs, not an aspirational one. When the mechanism changes, this file should change with it. If this file and the live trigger prompt disagree, treat that disagreement itself as a defect worth recording (see section 5).

## 2. What actually fires, today

A GitHub-account-scoped scheduled trigger, `trig_011oe2y7KR3AiPxUTd6b9P6c` ("6S Success hourly operator"), fires once an hour. Each firing starts a fresh session with no memory of prior runs; everything the session needs to pick up where the last one left off is either in the repository or in GitHub issues.

The trigger was created through the http_api rather than by a Claude session, which means no Claude session can update its stored prompt with `update_trigger`. That is a known, tracked defect: see issue #17. Do not treat the trigger's stored prompt as automatically current; check whether it matches `ops/routine-prompt.md` when in doubt.

## 3. The steps every cycle runs

1. **Attach to a real branch.** The checkout arrives detached and local `main` can be stale or, after any history rewrite on `origin`, entirely unrelated to it. Fetch `origin/main` and reset to it before trusting local history. This has cost enough runs that it is now step 0 rather than an assumption.
2. **Read the plan, not a summary of it.** `BACKLOG-2026-H2.md` (the work queue), `ROADMAP-2026-2029.md` (the strategy and arithmetic), `CLAUDE.md` (the rules), and the last four entries of `ops/NIGHTLY-LOG.md` (the only reliable account of what has actually been tried). The backlog wins on any conflict with a stale prompt.
3. **Check the tree before touching it.** `ops/audit_pages.py`, `ops/fix_dashes.py --check`, `ops/fingerprint_assets.py --check`, `content/manual/source/validate.py`. A failing gate becomes the cycle's work, not something to route around.
4. **Pick one item.** Work the backlog epics in order: measurement, then broken-or-dishonest, then traffic, then conversion, then product, then operational honesty. Take the highest item not waiting on Phil. Finish it. Do not open a second workstream in the same cycle.
5. **Verify what was touched**, including re-running the gates and, where the change sends mail or changes a served asset, checking the actual delivered artifact rather than a 200 status code.
6. **Sync Stripe** if a price or product changed, so the catalog, Stripe, and structured data cannot drift apart.
7. **Read the inbox** with `ops/inbox_agent.py --apply`. An owner reply outranks whatever was picked in step 4. A customer email is drafted for a human, never auto-sent.
8. **Deploy.** Push to `main`. The image builds automatically; the Hostinger host still needs a manual Redeploy click no session can make, so the log says so plainly rather than claiming the change is live.
9. **Write the retrospective.** One dated entry in `ops/NIGHTLY-LOG.md`, under 250 words, with the same six headings every time, failures recorded as plainly as wins.
10. **Update the backlog** if an item was finished, and **escalate** anything irreversible, financial, or strategic as a GitHub issue labelled `decision` rather than deciding it alone.

## 4. Why a fresh session every hour, not a long-running one

A fresh checkout each cycle means no session can accumulate silent, un-pushed state. Everything that matters for the next cycle has to survive as a commit, an issue, or a line in `ops/NIGHTLY-LOG.md`. That is a deliberate constraint, not an accident: it forces the operating memory to live in Git rather than in a context window that eventually resets anyway.

## 5. Known defects in the loop itself

- **Issue #17.** The trigger's stored prompt cannot be updated by any session, so fixes to `ops/routine-prompt.md` do not reach the thing that actually fires until Phil (or whoever holds http_api access) copies them across, or the trigger is recreated. Open, awaiting a decision.
- **Issue #22.** The sandboxed network most cycles run in cannot reach `6s-success.com`, `api.stripe.com`, or `api.indexnow.org`, so steps that need real egress (verifying the live site, submitting to IndexNow) sit as honestly-unverified rather than fabricated as done. Open, awaiting a decision.
- **History resets.** At least eighteen cycles have started from a local `main` that shares no ancestor with `origin/main`, because the container's baked-in git state predates a later rewrite on origin. Recovery is safe (reset to `origin/main`; nothing is lost, since the local-only commits never existed anywhere else), but it is not free, and it is the same root cause as issue #17.

## 6. One writer at a time (backlog 6.2)

On 2026-08-23 an interactive session and the cloud routine were both writing to
this repository at the same time and independently fixed the same cache
bug, discovered only when one session read the other's diff. That is the
failure this section exists to prevent, recorded rather than left as a
line in `ops/NIGHTLY-LOG.md` that the next cycle cannot find.

The rule:

1. **Only one scheduled writer runs at a time.** The single hourly trigger
   (section 2) already removes the case that actually caused the 2026-08-23
   collision: two automated loops running concurrently. Do not add a second
   scheduled trigger that also pushes to `main` without retiring or
   coordinating with the first.
2. **A session is never the only writer by assumption.** Phil, or anyone
   working interactively, can push to `main` at any point during a cycle.
   Step 0 (fetch and reset to `origin/main`) checks this at the start of a
   cycle; it does not check it again before the cycle's own push. Re-fetch
   `origin/main` immediately before pushing, not only at the start, and if
   it moved, diff the change in before treating the working tree as ready.
3. **A non-fast-forward push is a stop, not a retry.** Never force-push to
   resolve it. Fetch, read what changed, and check whether the fix this
   cycle built is already present upstream before reapplying it, the same
   check that would have caught the 2026-08-23 duplicate.
4. **Keep commits small and scoped to the one backlog item chosen in step
   4.** A wide commit touching unrelated files is the one most likely to
   conflict with a second writer's narrower one.

## 7. Read with

- `CLAUDE.md`, section 17 (the philosophical loop: OBSERVE through STANDARDIZE OR REVISE) and section 57 (startup procedure)
- `ops/routine-prompt.md`, the source of truth the trigger's prompt is supposed to mirror
- `ops/NIGHTLY-LOG.md`, the run history
- `BACKLOG-2026-H2.md` and `ROADMAP-2026-2029.md`, what the loop is currently working toward
