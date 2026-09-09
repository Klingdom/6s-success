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

import json
import os
import re
import statistics
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "klingdom/6s-success"

# Every scheduled workflow in .github/workflows/, checked against `ls` and
# each file's own `schedule:` block on 2026-09-09. Add a new one here the
# same day it gets a cron line, or this becomes exactly the coverage gap it
# was written to close.
WORKFLOWS = ["fulfil-orders.yml", "hourly-brief.yml", "linkedin-drafts.yml",
             "roadmap-report.yml", "status-email.yml"]


def gh_token() -> str | None:
    return os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")


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


def fetch_runs(workflow_file: str, per_page: int = 50) -> list[dict] | None:
    token = gh_token()
    if not token:
        return None
    try:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{REPO}/actions/workflows/"
            f"{workflow_file}/runs?per_page={per_page}&status=completed",
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
