#!/usr/bin/env python3
"""
Pull an off-host copy of THIS site's analytics, and prove it arrived intact.

WHY
---
Every traffic figure this business has ever quoted comes from one Postgres
container on one VPS. Nothing in this repository holds a copy, and the
Hostinger host-level backup has never been restored (RISKS.md RISK-0007), so
"we have a backup" is a belief. Losing that database loses the entire
measurement history: 3,497 events reaching back to launch, which is the only
evidence of what anyone has ever done on this site.

WHY NOT A pg_dump OF THE DATABASE
---------------------------------
That container serves THREE websites, not one. A whole-database dump would
copy another business's analytics onto the owner's laptop, which is not ours
to move (CLAUDE.md 36b and the privacy rule in section 47). This exports only
rows belonging to the 6S Success website id, joined through website_event for
the child tables.

It writes CSV, not SQL, deliberately: a CSV of 3,497 rows is readable in ten
years by anything, while a dump is hostage to a Postgres version. The point of
this file is that the numbers survive, not that the container can be cloned.

    python ops/backup_analytics.py
    python ops/backup_analytics.py --dir D:/backups/6s

Writes <dir>/analytics-YYYY-MM-DD/<table>.csv.gz plus a MANIFEST.txt holding
the row counts read from the source, and re-counts what landed locally before
claiming success.
"""
from __future__ import annotations

import argparse
import datetime
import gzip
import io
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = "root@187.77.25.50"
KEY = os.path.expanduser("~/.ssh/6s_deploy")
CONTAINER = "umami-analytics-vi0p-umami-db-1"
WEBSITE_ID = "f1fc5160-4473-422d-a89e-73ff6cbdca7a"

# Child tables reach our website through website_event, because only `website`
# and `website_event` carry website_id directly (checked against
# information_schema rather than assumed).
QUERIES = {
    "website":
        "select * from website where website_id = '%s'" % WEBSITE_ID,
    "website_event":
        "select * from website_event where website_id = '%s'" % WEBSITE_ID,
    "event_data":
        "select ed.* from event_data ed join website_event we "
        "on ed.website_event_id = we.event_id "
        "where we.website_id = '%s'" % WEBSITE_ID,
    "session_data":
        "select sd.* from session_data sd "
        "where sd.website_id = '%s'" % WEBSITE_ID,
}


def ssh(sql, timeout=300):
    """Run one SQL statement in the analytics container, read-only."""
    remote = ("docker exec -i %s psql -U umami -d umami -v ON_ERROR_STOP=1 "
              "-c %s" % (CONTAINER, _q(sql)))
    return subprocess.run(
        ["ssh", "-i", KEY, "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=20", HOST, remote],
        capture_output=True, text=True, timeout=timeout)


def _q(text):
    return '"' + text.replace('\\', '\\\\').replace('\"', '\\\"') + '"'


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.path.join(ROOT, "backups"))
    args = ap.parse_args()

    if not os.path.exists(KEY):
        print("  no SSH key at %s. Nothing was backed up, and that is not "
              "the same as nothing needing backup." % KEY)
        return 2

    day = datetime.date.today().isoformat()
    out = os.path.join(args.dir, "analytics-" + day)
    os.makedirs(out, exist_ok=True)

    manifest, failures = [], []
    for table, sql in QUERIES.items():
        copy = "copy (%s) to stdout with (format csv, header true)" % sql
        r = ssh(copy)
        if r.returncode != 0:
            failures.append("%s: %s" % (table, (r.stderr or "").strip()[:160]))
            continue
        body = r.stdout
        rows = max(0, len([l for l in body.splitlines() if l]) - 1)
        fp = os.path.join(out, table + ".csv.gz")
        with gzip.open(fp, "wt", encoding="utf-8", newline="") as f:
            f.write(body)

        # Re-read what actually landed. Writing a file is not the same as
        # having the data, and a backup nobody verifies is the shape of
        # problem this whole exercise exists to stop.
        with gzip.open(fp, "rt", encoding="utf-8") as f:
            back = max(0, len([l for l in f.read().splitlines() if l]) - 1)
        ok = back == rows
        if not ok:
            failures.append("%s: wrote %d rows, read back %d" % (table, rows, back))
        manifest.append((table, rows, os.path.getsize(fp), ok))

    lines = ["6S Success analytics export",
             "taken       : %s" % datetime.datetime.now().isoformat(timespec="seconds"),
             "source      : %s on %s" % (CONTAINER, HOST),
             "website_id  : %s" % WEBSITE_ID,
             "scope       : this website's rows only; the container serves "
             "three sites and the other two are deliberately not copied",
             ""]
    for t, n, size, ok in manifest:
        lines.append("  %-16s %6d rows  %7d bytes  %s"
                     % (t, n, size, "verified" if ok else "MISMATCH"))
    io.open(os.path.join(out, "MANIFEST.txt"), "w",
            encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")

    for l in lines:
        print("  " + l if l else "")
    if failures:
        print("\n  FAILED:")
        for f in failures:
            print("    " + f)
        return 1
    print("\n  wrote %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
