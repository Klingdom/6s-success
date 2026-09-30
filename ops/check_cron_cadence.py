#!/usr/bin/env python3
"""
Does a scheduled GitHub Actions workflow actually fire as often as its own
cron line and its own comments claim?

THE GAP THIS CLOSES
--------------------
fulfil-orders.yml is commented "every 30 minutes... chosen against the
promise on thanks.html," on the theory that a fixed interval bounds how long
a paying customer waits for their digital product. hourly-brief.yml is
commented "hourly at 23 past" and its own report email to Phil says a reply
"reaches the operator within the hour." Both are claims about wall-clock
behaviour, and neither had ever been checked against the one thing that can
confirm or deny them: the Actions API's own run history.

Checked 2026-09-09 against 255 real fulfil-orders.yml runs and 146 real
hourly-brief.yml runs: every single gap between consecutive fulfil-orders.yml
runs across the most recent 50 exceeded 60 minutes (mean 213 min, worst 367
min) against a configured 30-minute interval, and hourly-brief.yml's gaps
average 4.6 hours against a configured 60-minute interval, sustained across
14+ days, not a one-off. A 2026-09-09 05:00 log entry had already treated one
such gap as a "GitHub-side incident"; the fuller history says this is the
schedule event's normal, sustained behaviour on this account, not an outage.

This does not mean the promise is being broken today: thanks.html itself
already hedges ("within a few hours... deliveries go out on a schedule, so it
is not instant"), which happens to be roughly true of the measured mean. But
nothing had ever measured it, so the hedge was luck, not verification, and a
future config change (a shorter cron, a since-updated promise) could silently
drift back into a real customer-facing lie with nothing here to catch it.

CORRECTED 2026-09-09, LATER THE SAME DAY: TWO OF FIVE SCHEDULED WORKFLOWS
---------------------------------------------------------------------------
The first version only ever checked fulfil-orders.yml and hourly-brief.yml,
because `configured_interval_minutes()` only understood a cron shape that
fires N times an hour, every hour ("7,37 * * * *", "23 * * * *"). The repo
has three more scheduled workflows this could not parse at all:
linkedin-drafts.yml (once a day), status-email.yml (six fixed hours a day in
one cron line), and roadmap-report.yml (four separate cron lines, one per
fixed hour). A tool that only checks the two workflows it happens to
understand is not "measurement," it is a coverage gap wearing the same
clothes as the thing it replaced.

The parser now counts real fires per day (minute values times hour values,
summed across every `cron:` line in the file) and refuses to guess, staying
UNMEASURABLE, whenever a day-of-month/month/day-of-week field is anything
but `*`, since the every-day-the-same assumption would then be wrong rather
than unmeasured. Measured against the real Actions API history the same day:
linkedin-drafts.yml (mean gap 1438 min against a configured 1440) and
roadmap-report.yml (352 against 360) both run almost exactly on their
configured cadence, ratio 1.00 and 0.98. status-email.yml runs a real 1.57x
slower than its configured four-hour cycle (mean 376 min against 240),
measurable drift but under the 2.5x line this file calls "degraded." So the
sustained multi-day slowdown found in fulfil-orders.yml and hourly-brief.yml
is not, as the wording above could be read to imply, a blanket fact about
this GitHub account's scheduler: it is specific to the two workflows that
ask GitHub for a fire more than once an hour. The three slower-cadence
workflows are not showing the same symptom.

WHAT IT REFUSES TO DO
-----------------------
Report "on schedule" when it could not reach the API. No token or no network
is UNKNOWN, never PASS. Report a configured interval for a cron shape it has
not actually verified the arithmetic for (a day/month/weekday restriction);
UNMEASURABLE beats a confident wrong number.

Run:  python ops/check_cron_cadence.py
      python ops/check_cron_cadence.py --json
"""
from __future__ import annotations

import datetime
import json
import io
import os
import re
import statistics
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "klingdom/6s-success"

# Every scheduled workflow in .github/workflows/, checked against `ls` and
# each file's own `schedule:` block on 2026-09-09, plus social-drafts.yml
# (cron line added 2026-09-12, missed here for two days: found 2026-09-14
# reading .github/workflows/*.yml cold, ranked by how rarely each file is
# mentioned in ops/NIGHTLY-LOG.md) and bluesky-drafts.yml (added the same
# day its cron line shipped, 2026-09-30, precisely to avoid repeating that
# two-day gap). Add a new one here the same day it gets a cron line, or this
# becomes exactly the coverage gap it was written to close.
WORKFLOWS = ["fulfil-orders.yml", "hourly-brief.yml", "linkedin-drafts.yml",
             "roadmap-report.yml", "status-email.yml", "social-drafts.yml",
             "bluesky-drafts.yml"]


def gh_token() -> str | None:
    """Env first, then the gh CLI's own keyring.

    This checked only the environment, so on the machine that actually runs
    preflight by hand, where gh has been logged in for weeks and a push had
    succeeded seconds earlier, it emitted five warnings a run saying the
    cadence "was NOT measured". Nothing was unreachable. Nothing had asked.

    ops/dashboard.py already carries this exact fix and the docstring
    explaining it, written after the same mistake made the deck report
    "GitHub unreachable, issue counts UNKNOWN" on a logged-in machine. Second
    occurrence of one defect, so this is a copy with the reason attached rather
    than a silent one-liner.

    Saying UNCHECKED when the answer is one subprocess away is worse than
    having no check, because five identical warnings every run is how a person
    learns to skim past the warning that matters.
    """
    t = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if t:
        return t
    try:
        import subprocess
        r = subprocess.run(["gh", "auth", "token"], capture_output=True,
                           text=True, timeout=20)
        return r.stdout.strip() or None
    except Exception:                                          # noqa: BLE001
        return None


def configured_interval_minutes(workflow_file: str) -> float | None:
    """Parse the cron line(s) in the workflow file itself, not a remembered number.

    Handles every shape actually in use here: several fires an hour
    ("7,37 * * * *"), one fire at a fixed hour ("19 14 * * *"), several fixed
    hours in one line ("23 1,5,9,13,17,21 * * *"), and several fixed hours
    spread across separate `cron:` lines (roadmap-report.yml). All of those
    reduce to the same arithmetic: count how many times a day the schedule
    fires (minute values times hour values, "*" counting as the full 24/60),
    sum it across every line, and divide the day into that many equal parts.

    Refuses to guess a number for anything with a day-of-month, month, or
    weekday restriction (field 3, 4 or 5 not "*"): the every-day-alike
    assumption above would silently be wrong there rather than merely
    unmeasured, and no workflow in this repository needs that shape today.
    """
    path = os.path.join(ROOT, ".github", "workflows", workflow_file)
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return None
    crons = re.findall(r"cron:\s*'([^']+)'", text)
    if not crons:
        return None
    fires_per_day = 0
    for line in crons:
        fields = line.split()
        if len(fields) != 5:
            return None
        minute, hour, dom, month, dow = fields
        if (dom, month, dow) != ("*", "*", "*"):
            return None
        minute_count = len(minute.split(","))
        hour_count = 24 if hour == "*" else len(hour.split(","))
        fires_per_day += minute_count * hour_count
    return 1440.0 / fires_per_day if fires_per_day else None


# A workflow whose script decides at RUNTIME whether a triggered run actually
# delivers cannot be judged by its run cadence: a push run is as often not a
# delivery as it is. has_push_trigger() therefore refuses to count those runs
# as coverage, and says in its own comment that this "costs a stale-sounding
# warning" and errs conservative on purpose.
#
# That is the right call with only run data. There is better data. Each of
# these workflows commits a record of its own last real send, so the git
# history of that file IS the delivery log, and it answers the question the
# run counts only approximate: how long does Phil actually wait between
# briefs.
#
# Measured 2026-09-30, which is why this exists. hourly-brief.yml's run
# cadence across every trigger was 11 minutes mean; its schedule-only cadence
# was 290, and the gate reported 290 and called it degraded. Neither is what a
# person experiences. The delivery record showed 59, 59, 71, 52, 55, 61, 59,
# 64, 56, 65, 58, 67, 64, 56, 66, 64, 70, 52, 55 minutes: the brief is
# genuinely hourly, around the clock, and has been for days.
DELIVERY_RECORDS = {
    "hourly-brief.yml": "ops/last-brief-sent.json",
}


def delivery_gaps(record_path: str, limit: int = 40):
    """Minutes between real deliveries, newest first, from the record's own
    git history. None when it cannot be read: unknown is not "on time"."""
    try:
        p = subprocess.run(
            ["git", "log", "--format=%cI", "-%d" % limit, "--", record_path],
            cwd=ROOT, capture_output=True, text=True, timeout=60)
    except Exception:                                          # noqa: BLE001
        return None
    if p.returncode != 0:
        return None
    stamps = []
    for line in (p.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            stamps.append(datetime.datetime.fromisoformat(line))
        except ValueError:
            continue
    if len(stamps) < 3:
        return None
    stamps.sort()
    return [(b - a).total_seconds() / 60.0 for a, b in zip(stamps, stamps[1:])]

def has_push_trigger(workflow_file: str) -> bool:
    """True when this workflow also runs on push to main.

    It changes what the cadence number MEANS. fulfil-orders.yml gained a push
    trigger on 2026-09-09 precisely because GitHub throttles its cron, and every
    commit to main is then another chance to deliver a paid order. Measuring
    only `event=schedule` after that answers "does the cron fire", which is a
    real question, and silently stops answering "how long does a buyer wait",
    which is the one the customer has.
    """
    fp = os.path.join(ROOT, ".github", "workflows", workflow_file)
    try:
        text = io.open(fp, encoding="utf-8", errors="replace").read()
    except OSError:
        return False
    head = text.split("jobs:")[0]
    if "push:" not in head:
        return False
    # AND THE PUSH RUN MUST ACTUALLY DO THE WORK.
    #
    # linkedin-drafts.yml and social-drafts.yml also trigger on push, but they
    # branch on github.event_name and treat push as a gated fallback that only
    # sends once the schedule is already overdue. Their push RUNS are frequent;
    # their push DELIVERIES are not. Counting those runs as coverage produced a
    # line claiming a real gap of 11.7 minutes median for a workflow whose job
    # is to post once a day, which is a true statement about runs and a false
    # one about anything a person cares about.
    #
    # fulfil-orders.yml carries no such branch: every triggered run attempts
    # delivery, which is why it is safe there and why the distinction is drawn
    # on the branch rather than on the trigger.
    #
    # hourly-brief.yml (push trigger added 2026-09-28) gates the same way in
    # spirit, at a different layer: it carries no `github.event_name` branch
    # in the YAML, because ops/hourly_brief.py's own seconds_since_last_send()
    # throttle decides at runtime, inside the script, whether a triggered run
    # sends anything (roughly hourly) or exits without mailing Phil. A push
    # RUN there is just as often not a push DELIVERY as it is for the two
    # workflows above; the substring check above cannot see a throttle that
    # lives in Python, so it is named here explicitly rather than silently
    # miscounted as "ungated" the way the pre-2026-09-27 version of this
    # function once did for the YAML-branch case (see
    # case_coverage_is_earned_not_assumed in
    # ops/tests/test_cron_effective_latency.py). This means this gate stays
    # conservative (reports hourly-brief.yml as still cron-degraded) even
    # after the throttle is doing its job; that costs a stale-sounding
    # warning, not a false claim of coverage, and is the safer side to err on.
    SCRIPT_THROTTLED_PUSH = {"hourly-brief.yml"}
    if workflow_file in SCRIPT_THROTTLED_PUSH:
        return False
    return "github.event_name" not in text


def fetch_runs(workflow_file: str, per_page: int = 50,
               event: str | None = "schedule") -> list[dict] | None:
    """Completed runs actually fired by this workflow's own cron.

    `event=schedule` on purpose: a manual `workflow_dispatch` run (someone
    checking whether a fix landed, or re-running a stuck job) says nothing
    about whether the CRON fires and lands on time, but it carries a real
    `created_at` and would otherwise be counted as one. Found live 2026-09-12:
    linkedin-drafts.yml's own delivery-phase check counted a workflow_dispatch
    run made hours after the promised landing time as "1 scheduled run since"
    the cron changed, which is not what it looked like it was measuring. The
    same unfiltered list would corrupt gaps_minutes too, understating a real
    cadence problem by inserting an artificially short gap around every
    manual run.
    """
    token = gh_token()
    if not token:
        return None
    try:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{REPO}/actions/workflows/"
            f"{workflow_file}/runs?per_page={per_page}&status=completed"
            + (f"&event={event}" if event else ""),
            headers={"Authorization": f"Bearer {token}",
                     "Accept": "application/vnd.github+json",
                     "User-Agent": "6s-cron-cadence-check"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
        return data.get("workflow_runs")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return None


def gaps_minutes(runs: list[dict]) -> list[float]:
    import datetime
    times = sorted(
        datetime.datetime.fromisoformat(r["created_at"].replace("Z", "+00:00"))
        for r in runs)
    return [(times[i + 1] - times[i]).total_seconds() / 60.0
             for i in range(len(times) - 1)]


def intended_landing(workflow_file: str) -> tuple | None:
    '''(hour, minute) UTC a workflow is meant to ARRIVE, from its own file.

    Read from a `# lands-at: HH:MM UTC` comment rather than held here, so the
    promise lives beside the cron it describes and cannot drift away from it.
    Returns None when a workflow makes no such promise, which is most of them.
    '''
    path = os.path.join(ROOT, '.github', 'workflows', workflow_file)
    if not os.path.exists(path):
        return None
    text = io.open(path, encoding='utf-8').read()
    m = re.search(r'#\s*lands-at:\s*(\d{1,2}):(\d{2})\s*UTC', text)
    return (int(m.group(1)), int(m.group(2))) if m else None


def scheduled_times(workflow_file: str) -> list:
    '''Every (hour, minute) UTC this workflow is scheduled to fire.

    Only for crons naming a specific hour. An hourly cron has no phase worth
    measuring: every hour is its hour, so a landing time means nothing.
    '''
    path = os.path.join(ROOT, '.github', 'workflows', workflow_file)
    if not os.path.exists(path):
        return []
    text = io.open(path, encoding='utf-8').read()
    out = []
    for c in re.findall(r"cron:\s*'([^']+)'", text):
        parts = c.split()
        if len(parts) != 5 or parts[1] == '*':
            continue
        for mn in parts[0].split(','):
            for hr in parts[1].split(','):
                try:
                    out.append((int(hr), int(mn)))
                except ValueError:
                    pass
    return out


def landing_minutes(runs: list, times: list) -> list:
    '''Minutes each run landed after its OWN nearest preceding scheduled time.

    Measuring every run against one deadline is how a first pass at this on
    2026-09-11 reported roadmap-report.yml as 8.84 hours late. It has four
    cron lines and four deadlines; the real figure is 2.59. The wrong number
    was nearly published, so the nearest-preceding rule is the whole point of
    this function and not an implementation detail.
    '''
    out = []
    for r in runs:
        stamp = r.get('created_at') or r.get('createdAt')
        if not stamp:
            continue
        t = datetime.datetime.fromisoformat(stamp.replace('Z', '+00:00'))
        best = None
        for back in (0, 1):
            for hr, mn in times:
                due = (t - datetime.timedelta(days=back)).replace(
                    hour=hr, minute=mn, second=0, microsecond=0)
                if due <= t:
                    gap = (t - due).total_seconds() / 60.0
                    if best is None or gap < best:
                        best = gap
        if best is not None:
            out.append(best)
    return out


def most_recent_due(times: list, now: 'datetime.datetime | None' = None) -> 'datetime.datetime | None':
    '''The latest scheduled (hour, minute) UTC moment at or before now.

    Found live 2026-09-12: linkedin-drafts.yml's cron changed at 09:11 UTC,
    its first new-schedule fire was due at 10:47 UTC the same day, and by
    the next morning zero scheduled runs had landed, GitHub's own dashboard
    confirming the workflow was still "active." gate_scheduled_delivery_phase
    could only say "0 scheduled run(s) since, NOT YET VERIFIED," the same
    wording it uses one minute after a legitimate cron edit, which buries a
    fire that is many hours overdue inside a message meant for a fire that
    simply has not come around yet. This tells the two apart: a due moment
    more than a day in the past, with nothing landed against it, is not
    "not yet verified," it is overdue.
    '''
    now = now or datetime.datetime.now(datetime.timezone.utc)
    best = None
    for back in (0, 1, 2):
        for hr, mn in times:
            due = (now - datetime.timedelta(days=back)).replace(
                hour=hr, minute=mn, second=0, microsecond=0)
            if due <= now and (best is None or due > best):
                best = due
    return best


def last_changed(workflow_file: str) -> str | None:
    '''ISO timestamp of the last commit touching this workflow, or None.

    A cron change makes every earlier run unrepresentative: runs that fired
    under the old schedule say nothing about whether the new one lands where
    it promises. Without this, changing a cron makes the delivery-phase gate
    warn for as long as the old runs dominate the sample, and a gate that
    cries wolf after every legitimate change is a gate people learn to skip.
    '''
    try:
        import subprocess
        out = subprocess.run(
            ['git', 'log', '-1', '--format=%cI', '--',
             os.path.join('.github', 'workflows', workflow_file)],
            cwd=ROOT, capture_output=True, text=True, timeout=30)
        return (out.stdout or '').strip() or None
    except Exception:                                         # noqa: BLE001
        return None


def runs_since(runs: list, iso: str | None) -> list:
    '''Runs that started after the given ISO timestamp. All of them if None.'''
    if not iso:
        return runs
    try:
        cut = datetime.datetime.fromisoformat(iso)
    except ValueError:
        return runs
    out = []
    for r in runs:
        stamp = r.get('created_at') or r.get('createdAt')
        if not stamp:
            continue
        t = datetime.datetime.fromisoformat(stamp.replace('Z', '+00:00'))
        if t >= cut:
            out.append(r)
    return out

def check_one(workflow_file: str) -> dict:
    configured = configured_interval_minutes(workflow_file)
    runs = fetch_runs(workflow_file)
    if runs is None:
        return {"workflow": workflow_file, "verdict": "unknown",
                "reason": "no GitHub token or the API was unreachable from here"}
    if len(runs) < 5:
        return {"workflow": workflow_file, "verdict": "unknown",
                "reason": f"only {len(runs)} completed run(s) on record, too few to measure"}
    g = gaps_minutes(runs)
    mean = statistics.mean(g)
    median = statistics.median(g)
    worst = max(g)
    result = {"workflow": workflow_file, "verdict": "measured",
              "configured_interval_min": configured,
              "sample_size": len(g),
              "mean_gap_min": round(mean, 1),
              "median_gap_min": round(median, 1),
              "worst_gap_min": round(worst, 1)}
    if configured:
        result["mean_over_configured"] = round(mean / configured, 1)
        result["degraded"] = mean > configured * 2.5

    # THE NUMBER A CUSTOMER ACTUALLY EXPERIENCES, where a push trigger exists.
    #
    # Measured 2026-09-27 on fulfil-orders.yml: schedule-only gaps mean 284 min
    # and worst 354, which is what this check had been reporting and is true of
    # the cron. Across EVERY trigger the same window gives mean 15.7, median
    # 12.9 and worst 42.1 minutes, because 76 of 80 runs came from push.
    #
    # Reporting only the first number said a buyer might wait six hours when
    # the measured worst case was forty-two minutes. An alarming warning that
    # overstates customer risk by an order of magnitude is not a safe error: it
    # is how a team learns to scroll past warnings.
    if has_push_trigger(workflow_file):
        allruns = fetch_runs(workflow_file, event=None)
        if allruns and len(allruns) >= 5:
            ag = gaps_minutes(allruns)
            if ag:
                result["effective_mean_gap_min"] = round(statistics.mean(ag), 1)
                result["effective_median_gap_min"] = round(statistics.median(ag), 1)
                result["effective_worst_gap_min"] = round(max(ag), 1)
                result["effective_sample_size"] = len(ag)
                # COVERAGE HAS TO BE EARNED, NOT ASSUMED FROM THE TRIGGER.
                #
                # The first version cleared `degraded` for any workflow with an
                # ungated push trigger. ops/tests/test_check_cron_cadence.py
                # caught it: fed 210-minute gaps on BOTH queries, it still
                # reported covered, which says the push trigger fixed a problem
                # the same numbers show it did not. A trigger existing is not
                # the same fact as a trigger helping.
                #
                # So coverage is claimed only when the real interval clears the
                # same bar the degraded verdict uses. If pushes dry up, the
                # effective gap rises to meet the schedule gap and this goes
                # back to DEGRADED on its own, which is the behaviour wanted on
                # a quiet week.
                eff_mean = statistics.mean(ag)
                if configured and eff_mean <= configured * 2.5:
                    result["degraded"] = False
                    result["cron_late_but_covered"] = True

    # A workflow that throttles inside its own script is judged on what it
    # DELIVERED, not on how often it was triggered. See DELIVERY_RECORDS.
    record = DELIVERY_RECORDS.get(workflow_file)
    if result.get("degraded") and record:
        dg = delivery_gaps(record)
        if dg:
            d_mean = statistics.mean(dg)
            result["delivery_mean"] = d_mean
            result["delivery_max"] = max(dg)
            result["delivery_n"] = len(dg)
            result["delivery_record"] = record
            if configured and d_mean <= configured * 1.5:
                result["degraded"] = False
                result["delivery_on_time"] = True
        else:
            # Cannot read the record. Stays degraded, which is the
            # conservative answer, and says why rather than implying the
            # cadence was measured.
            result["delivery_unreadable"] = record
    return result


def check() -> dict:
    return {"workflows": [check_one(w) for w in WORKFLOWS]}


def main() -> int:
    as_json = "--json" in sys.argv
    result = check()
    if as_json:
        print(json.dumps(result, indent=2))
        return 0
    for r in result["workflows"]:
        if r["verdict"] == "unknown":
            print(f"  [??] {r['workflow']}: {r['reason']}")
            continue
        cfg = r.get("configured_interval_min")
        cfg_txt = f"configured {cfg:.0f} min" if cfg else "configured interval not parsed"
        flag = " DEGRADED" if r.get("degraded") else ""
        print(f"  [{'warn' if r.get('degraded') else 'ok'}] {r['workflow']}: "
              f"{cfg_txt}, actual mean {r['mean_gap_min']} min / "
              f"median {r['median_gap_min']} min / worst {r['worst_gap_min']} min "
              f"over {r['sample_size']} gaps{flag}")
        if r.get("cron_late_but_covered"):
            print(f"        cron is late, but a push trigger covers it: real "
                  f"gap across every trigger is mean "
                  f"{r['effective_mean_gap_min']} / median "
                  f"{r['effective_median_gap_min']} / worst "
                  f"{r['effective_worst_gap_min']} min over "
                  f"{r['effective_sample_size']} gaps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
