# The continuous work loop

How Claude works overnight on 6S Success, and how you debrief in the morning.

---

## One thing is needed from you

The nightly loop runs as a **cloud routine**: an isolated Claude session in
Anthropic's cloud that clones this repository, works, commits, and pushes. It
runs whether or not your machine is on.

Creating it failed with:

> Connect your GitHub account before saving a routine that uses a GitHub repository.

**Fix it once, in about a minute:** run `/web-setup` in Claude Code and connect
your GitHub account, or install the Claude GitHub App on `Klingdom/6s-success`
at <https://claude.ai/code/onboarding?magic=github-app-setup>.

Then say "create the nightly loop" and it goes live with the configuration in
`ops/nightly-routine.json`. Nothing else is outstanding.

---

## Why cloud and not local

| | Cloud routine | Local loop (`/loop`, cron) |
|---|---|---|
| Runs while your machine is off | **Yes** | No |
| Survives closing the terminal | **Yes** | No |
| Can reach the Desktop originals | No | Yes |
| Can reach everything in this repo | **Yes** | Yes |

The local options only run while a session is open on your machine, so they
cannot give you work done while you sleep. That is why the whole estate was
mirrored into `content/`: a cloud agent can only touch what is in the
repository, and until that migration the repository held the website and the
operating system but none of the actual products.

`content/` is text only. 40 MB of text against 1.78 GB of images and PDFs, which
stay on the Desktop.

---

## The schedule

Four passes a night, at 9pm, midnight, 3am and 6am Denver time
(`0 3,6,9,12 * * *` UTC). Each pass is independent: it re-reads the state, picks
the highest-value thing it can finish, does it, and records it. If one pass
fails, the next simply picks up from wherever things stand.

Four short passes beat one long one. A pass that dies halfway through leaves a
mess; four bounded passes leave four commits.

---

## What each pass does

1. **Orient.** Read `CLAUDE.md`, `STATUS.md`, `EXECUTIVE-DASHBOARD-LIVE.md`, then
   the open issues.
2. **Pick one thing.** Highest value it can actually finish. Money path first,
   then P0 issues, then content improvement. It skips anything labelled
   `blocked-on-art` or `decision`.
3. **Do it properly.** House style enforced: zero em and en dashes, Straighten
   never "Set in Order", Safety is the fourth S, product types never brands.
   Never weakens a safety disclaimer.
4. **Record it.** Commit and push, regenerate the dashboard, update `STATUS.md`
   if the operating state changed, and append to `ops/NIGHTLY-LOG.md`.
5. **Leave it clean.** Never a broken tree. Runs out of time, commits what works.

If it hits something irreversible, financial, legally material, or strategically
consequential, it stops and opens an issue labelled `decision` instead. Those are
the only things that wait for you.

---

## Your morning debrief

Three things, in this order. It should take about five minutes.

**1. Open `ops/dashboard.html`.** The 60-second read: overall status, revenue
against the 20,000 dollar target, the one constraint, and how many items need
your call. Every number is measured by `ops/dashboard.py`, never typed, so it
cannot quietly drift the way a hand-maintained status page does.

**2. Read the top of `ops/NIGHTLY-LOG.md`.** One dated entry per pass, under 200
words, written for someone half awake. What was done, what was verified, what
was found, what is recommended next. Failures are recorded as plainly as wins.

**3. Check the `decision` issues.** `gh issue list --label decision`. These are
the only things blocking progress that Claude will not decide for you. Answer
them in the issue and the next pass picks them up.

Then say what you want changed, or say nothing and let it keep running.

---

## Changing the instructions

The prompt each pass runs is in `ops/nightly-routine.json`. Editing that file
does not change the live routine; ask for the routine to be updated after
editing, or just say what you want done differently and it will be updated for
you.

To pause it: <https://claude.ai/code/routines>.
