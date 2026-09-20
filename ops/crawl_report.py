#!/usr/bin/env python3
"""
What has actually been fetching this website, from the server's own log.

WHY THIS EXISTS
---------------
Google Search Console is verified to no property (OWNER-ACTIONS item 1a is one
paste from Phil and has been open since August), so there is no impressions,
clicks or coverage data for this site anywhere. The only evidence that exists
about whether search engines read these pages is the web server access log.

Until 2026-09-20 that log went to stdout and nowhere else, which meant it lived
in docker logs and was destroyed by every deploy. Checked that day: the
container had restarted an hour earlier and the site entire crawl history was
61 requests. site/nginx/default.conf now also writes to a bind-mounted file
that outlives the container, and this reads it.

WHAT IT CANNOT TELL YOU, said before any number is quoted
---------------------------------------------------------
A user agent is a claim. Verifying that a request calling itself Googlebot came
from Google needs a reverse DNS lookup on the source address, and the log
deliberately records no addresses at all, because the question here is which
pages get fetched by what, not who visited. So every count below is requests
from something calling itself X. Spoofing inflates it; nothing here detects it.

It also sees only what reached the container. Anything Nginx Proxy Manager
answers itself, and anything blocked upstream, never appears.

    python ops/crawl_report.py                 # last 7 days, summary
    python ops/crawl_report.py --days 30
    python ops/crawl_report.py --bot Googlebot --paths
"""
from __future__ import annotations

import argparse
import collections
import datetime
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = "root@187.77.25.50"
KEY = os.path.expanduser("~/.ssh/6s_deploy")
LOGDIR = "/var/log/6s-success"

# Ordered: the first pattern that matches wins, so Googlebot-Image is
# classified before the bare Googlebot can claim it.
BOTS = [
    ("Googlebot-Image", r"Googlebot-Image"),
    ("Googlebot-News", r"Googlebot-News"),
    ("Googlebot", r"Googlebot(?!-)"),
    ("Google-Other", r"GoogleOther|Google-InspectionTool|Google-Extended"),
    ("Bingbot", r"bingbot|BingPreview"),
    ("YandexBot", r"Yandex"),
    ("DuckDuckBot", r"DuckDuckBot|DuckAssistBot"),
    ("Applebot", r"Applebot"),
    ("PetalBot", r"PetalBot"),
    ("Amazonbot", r"Amazonbot"),
    ("GPTBot", r"GPTBot"),
    ("OAI-SearchBot", r"OAI-SearchBot"),
    ("ChatGPT-User", r"ChatGPT-User"),
    ("ClaudeBot", r"ClaudeBot|Claude-Web|anthropic"),
    ("PerplexityBot", r"Perplexity"),
    ("Meta/FacebookBot", r"facebookexternalhit|meta-external"),
    ("SEO tools", r"AhrefsBot|SemrushBot|MJ12bot|DotBot|DataForSeo"),
    ("Uptime/monitor", r"UptimeRobot|Pingdom|StatusCake|wget|curl"),
]
BOT_RE = [(name, re.compile(pat, re.I)) for name, pat in BOTS]

LINE = re.compile(
    r'^(?P<ts>\S+) (?P<status>\d{3}) (?P<method>\S+) (?P<path>\S+) '
    r'"(?P<ua>[^"]*)" "(?P<ref>[^"]*)" (?P<bytes>\d+) (?P<time>[\d.]+)$')


def classify(ua):
    for name, rx in BOT_RE:
        if rx.search(ua):
            return name
    if re.search(r"bot|crawl|spider|slurp", ua, re.I):
        return "other bot (unrecognised)"
    return "human or unknown"


def fetch():
    """Read the log off the VPS. Returns (lines, note).

    Never invents data: if the key or the host is unavailable it says so and
    returns nothing, because a report that silently shows zero crawling looks
    exactly like a site nobody crawls.
    """
    if not os.path.exists(KEY):
        return [], ("no SSH key at %s, so the production log could not be "
                    "read. NOT a measurement of zero." % KEY)
    # Trailing "exit 0" is load bearing. The rotated-file reads are expected
    # to find nothing until logrotate has run for the first time, and a
    # compound command takes the exit status of its LAST part, so a perfectly
    # good read of a live access.log came back as status 1. The first run of
    # this script against real production data reported
    # "UNCHECKED: ssh exited 1" while 500 bytes of log sat in front of it:
    # the honest-failure path firing on a success, which is worse than no
    # check, because it teaches the reader to ignore the word UNCHECKED.
    #
    # ssh itself still reports connection and auth failures as 255, and that
    # is kept below, so a real "could not look" is still not confused with
    # "looked and found nothing".
    cmd = ("{ cat %s/access.log 2>/dev/null; "
           "zcat -f %s/access.log.*.gz 2>/dev/null; "
           "cat %s/access.log.[0-9] 2>/dev/null; } ; exit 0"
           % (LOGDIR, LOGDIR, LOGDIR))
    try:
        out = subprocess.run(
            ["ssh", "-i", KEY, "-o", "StrictHostKeyChecking=no",
             "-o", "ConnectTimeout=20", HOST, cmd],
            capture_output=True, text=True, timeout=300)
    except Exception as exc:                                   # noqa: BLE001
        return [], "could not reach the VPS (%s). NOT a measurement." % exc
    if out.returncode != 0:
        return [], ("ssh exited %d (255 means it could not connect or "
                    "authenticate). NOT a measurement of zero."
                    % out.returncode)
    lines = [l for l in out.stdout.splitlines() if l.strip()]
    if not lines:
        return [], ("the log is empty or not mounted. If the container was "
                    "redeployed without the volume from "
                    "docker-compose.hostinger.yml, this is what that looks "
                    "like. Check the container Mounts with docker inspect.")
    return lines, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--bot", default="")
    ap.add_argument("--paths", action="store_true",
                    help="list the most fetched paths")
    args = ap.parse_args()

    raw, note = fetch()
    if note:
        print("UNCHECKED: " + note)
        return 2

    cutoff = (datetime.datetime.now(datetime.timezone.utc)
              - datetime.timedelta(days=args.days)).strftime("%Y-%m-%d")
    rows, unparsed = [], 0
    for line in raw:
        m = LINE.match(line)
        if not m:
            unparsed += 1
            continue
        d = m.groupdict()
        d["day"] = d["ts"][:10]
        if d["day"] < cutoff:
            continue
        d["bot"] = classify(d["ua"])
        rows.append(d)

    if not rows:
        print("  the log holds %d line(s) but none inside the last %d day(s)."
              % (len(raw), args.days))
        if raw:
            print("  oldest line: %s" % raw[0][:40])
        return 0

    days = sorted({r["day"] for r in rows})
    print("  window         : %s to %s (%d day(s) with traffic)"
          % (days[0], days[-1], len(days)))
    print("  requests       : %d" % len(rows))
    if unparsed:
        print("  unparsed lines : %d (log format changed?)" % unparsed)

    by_bot = collections.Counter(r["bot"] for r in rows)
    print("")
    print("  BY CLIENT (a user agent is a claim, not an identity)")
    for name, n in by_bot.most_common():
        errs = sum(1 for r in rows
                   if r["bot"] == name and r["status"][0] in "45")
        redir = sum(1 for r in rows
                    if r["bot"] == name and r["status"][0] == "3")
        extra = []
        if redir:
            extra.append("%d redirected" % redir)
        if errs:
            extra.append("%d error" % errs)
        print("    %-26s %5d  %s"
              % (name, n, ", ".join(extra) if extra else ""))

    search = [r for r in rows if r["bot"] in
              ("Googlebot", "Bingbot", "YandexBot", "Applebot",
               "DuckDuckBot", "Google-Other")]
    pages = {r["path"] for r in search
             if not r["path"].startswith("/assets/")
             and not r["path"].startswith("/stats")}
    print("")
    print("  SEARCH ENGINES: %d fetch(es), %d distinct non-asset path(s)"
          % (len(search), len(pages)))
    if search:
        per_day = collections.Counter(r["day"] for r in search)
        print("    per day: " + ", ".join(
            "%s %d" % (d, per_day[d]) for d in sorted(per_day)))

    if args.paths:
        sel = [r for r in rows
               if not args.bot or args.bot.lower() in r["bot"].lower()]
        print("")
        print("  MOST FETCHED PATHS%s"
              % (" by %s" % args.bot if args.bot else ""))
        for path, n in collections.Counter(
                r["path"] for r in sel).most_common(25):
            print("    %5d  %s" % (n, path))

    refs = collections.Counter(
        r["ref"] for r in rows
        if r["ref"] not in ("-", "") and "6s-success.com" not in r["ref"])
    if refs:
        print("")
        print("  EXTERNAL REFERRERS")
        for ref, n in refs.most_common(12):
            print("    %5d  %s" % (n, ref[:90]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
