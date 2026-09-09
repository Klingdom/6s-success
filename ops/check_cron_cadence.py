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

WHAT IT REFUSES TO DO
-----------------------
Report "on schedule" when it could not reach the API. No token or no network
is UNKNOWN, never PASS.

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

# workflow file -> configured interval in minutes, read once and trusted only
# as a fallback; the real source of truth is parsed straight out of the cron
# line below so this dict cannot itself go stale.
WORKFLOWS = ["fulfil-orders.yml", "hourly-brief.yml"]


def gh_token() -> str | None:
    return os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")


def configured_interval_minutes(workflow_file: str) -> float | None:
    """Parse the cron line(s) in the workflow file itself, not a remembered number."""
    path = os.path.join(ROOT, ".github", "workflows", workflow_file)
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return None
    crons = re.findall(r"cron:\s*'([^']+)'", text)
    if not crons:
        return None
    # "7,37 * * * *" -> two fires an hour, 30 min apart. "23 * * * *" -> one, 60 min.
    minute_field = crons[0].split()[0]
    fires_per_hour = len(minute_field.split(","))
    if len(crons) > 1:
        # Multiple separate cron lines (roadmap-report.yml style: fixed hours,
        # not an interval), not modelled here; caller should treat as unknown.
        return None
    return 60.0 / fires_per_hour if fires_per_hour else None


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
