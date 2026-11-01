#!/usr/bin/env python3
"""Reduce ops/traffic_query.sh output to the headline counts, for a public repo.

Why this exists: traffic went unmeasured from 2026-10-03 to 2026-11-01
because reading it needs an SSH session to the VPS, and Claude Code's auto-mode
classifier refuses that from an operator session (a scheduled GitHub job doing
the same read was refused as well, 2026-11-01). So the owner runs the read-only
query himself and pipes it through this script. This repository is PUBLIC, so
only the rows GOALS.md already publishes are kept (pageviews, visitors, visits
for all time, 30 days and 7 days, plus the week with its busiest 20-minute
bucket removed, which is how a burst of bot traffic was told apart from real
visitors before); page paths and referrers never reach a commit.

Unchecked is not zero: if a row is missing, the output says so and the exit
code is non-zero, rather than writing a 0 that reads like a dead site.

    ssh -i ~/.ssh/6s_deploy root@187.77.25.50 sh -s < ops/traffic_query.sh \n        | python ops/traffic_summary.py ops/traffic-summary.json
"""
import datetime
import json
import sys

ROWS = ("all_time", "last_30d", "last_7d", "raw_week", "ex_busiest_bucket")


def parse(text):
    found = {}
    for line in text.splitlines():
        parts = line.strip().split("|")
        if len(parts) < 4 or parts[0] not in ROWS or parts[0] in found:
            continue
        try:
            pv, visitors, visits = (int(parts[1]), int(parts[2]), int(parts[3]))
        except ValueError:
            continue
        row = {"pageviews": pv, "visitors": visitors, "visits": visits}
        if parts[0] == "all_time" and len(parts) >= 6:
            row["first_day"], row["last_day"] = parts[4], parts[5]
        found[parts[0]] = row
    return found


def main(argv):
    found = parse(sys.stdin.read())
    missing = [r for r in ROWS if r not in found]
    out = {
        "measured_at": datetime.datetime.now(datetime.timezone.utc)
        .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "Umami database on the VPS via ops/traffic_query.sh, "
                  "website_id f1fc5160-4473-422d-a89e-73ff6cbdca7a, /__ paths excluded",
        "complete": not missing,
        "missing_rows": missing,
        "counts": found,
    }
    if len(argv) > 1:
        with open(argv[1], "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
            f.write("\n")
    print(json.dumps({k: out[k] for k in ("measured_at", "complete", "missing_rows")}))
    for k in ("last_7d", "last_30d"):
        if k in found:
            print("%s: %d visitors, %d visits, %d pageviews" % (
                k, found[k]["visitors"], found[k]["visits"], found[k]["pageviews"]))
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
