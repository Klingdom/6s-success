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

# THE CORRECTION THAT MATTERS, 2026-09-20.
#
# This file shipped that morning saying the container's own access log was the
# only evidence about who reads this site. That was WRONG, and it was written
# into the nginx config, the commit message, DATA-SOURCES and STATUS before
# anyone checked. LEARNINGS.md LRN-0010 had already named a second log and
# used it for real attribution work back on 2026-09-14: Nginx Proxy Manager
# terminates TLS in front of this site and keeps its own access log, which
# survives container recreation and is rotated with four archives kept.
#
# It is not merely an equal alternative, it is the better source:
#
#   * It has HISTORY. 42,396 lines in the current file alone when this was
#     written, reaching back to 2026-09-13, plus four gzipped archives. The
#     log added this morning starts at zero and can answer nothing about the
#     past.
#   * It keeps the CLIENT IP, so "something calling itself Googlebot" can be
#     checked by reverse DNS against googlebot.com. That is exactly the
#     limitation the new log documents about itself and cannot fix, because it
#     deliberately stores no addresses.
#
# So this reads the proxy log by default. The container log stays as
# --source=container: it is this site alone rather than every vhost on a
# shared box, and it carries no personal data, which makes it the safer thing
# to keep long term. But a tool that only read it would have thrown away three
# weeks of evidence that was sitting on the same machine.
PROXY_LOG = "/data/logs/proxy-host-4_access.log"
PROXY_CONTAINER = "nginx-proxy-manager"

# [13/Sep/2026:13:00:40 +0000] - 200 200 - GET https 6s-success.com
# "/robots.txt" [Client 66.249.74.196] [Length 231] [Gzip -]
# [Sent-to 187.77.25.50] "Mozilla/5.0 (compatible; Googlebot/2.1; ...)" "-"
# Two shapes, both real, found by counting what did not parse rather than by
# assuming the first sample was the format:
#   [ts] - 200 200 - GET https host "/path" [Client ip] [Length n] ... "ua" "ref"
#   [ts] - -  301 -  GET http  host "/path" [Client ip] [Length n] ... "ua" "ref"
# The second is the plain-HTTP to HTTPS redirect, where there is no upstream
# status to report, so the columns shift. 1,162 lines were being dropped as
# unparseable until this was widened, and dropped lines are the ones that
# quietly make a crawler look less active than it is.
PROXY_LINE = re.compile(
    r'^\[(?P<ts>[^\]]+)\]\s+(?:\S+\s+)*?(?P<status>\d{3})\s+'
    r'(?:\S+\s+)*?(?P<method>[A-Z]+)\s+(?P<scheme>\S+)\s+(?P<host>\S+)\s+'
    r'"(?P<path>[^"]*)"\s+\[Client (?P<ip>[^\]]+)\]\s+'
    r'\[Length (?P<bytes>[^\]]*)\].*?'
    r'"(?P<ua>[^"]*)"\s+"(?P<ref>[^"]*)"\s*$')

_MONTHS = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05",
           "Jun": "06", "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10",
           "Nov": "11", "Dec": "12"}


def _proxy_day(ts):
    """'13/Sep/2026:13:00:40 +0000' -> '2026-09-13'."""
    try:
        d, mon, rest = ts.split("/", 2)
        return "%s-%s-%s" % (rest[:4], _MONTHS.get(mon, "01"), d)
    except Exception:                                          # noqa: BLE001
        return ""

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


def fetch_proxy():
    """Read the Nginx Proxy Manager access log for this site, current plus
    archives. Returns (lines, note), same contract as fetch()."""
    if not os.path.exists(KEY):
        return [], ("no SSH key at %s, so the proxy log could not be read. "
                    "NOT a measurement of zero." % KEY)
    inner = ("cat %s 2>/dev/null; zcat -f %s.*.gz 2>/dev/null; "
             "exit 0" % (PROXY_LOG, PROXY_LOG))
    cmd = "docker exec %s sh -c %s" % (PROXY_CONTAINER, _shq(inner))
    try:
        out = subprocess.run(
            ["ssh", "-i", KEY, "-o", "StrictHostKeyChecking=no",
             "-o", "ConnectTimeout=20", HOST, cmd],
            capture_output=True, text=True, timeout=600)
    except Exception as exc:                                   # noqa: BLE001
        return [], "could not reach the VPS (%s). NOT a measurement." % exc
    if out.returncode != 0:
        return [], ("ssh/docker exited %d. NOT a measurement of zero."
                    % out.returncode)
    lines = [l for l in out.stdout.splitlines() if l.strip()]
    if not lines:
        return [], ("the proxy log read back empty. That is not zero traffic; "
                    "check the container name and path still match "
                    "(%s:%s)." % (PROXY_CONTAINER, PROXY_LOG))
    return lines, ""


def _shq(text):
    return "'" + text.replace("'", "'\''") + "'"


def verify_bots(ips, limit=14):
    """Reverse-DNS a sample of addresses that CLAIMED to be a search engine.

    This is the check the container log can never support, because it stores
    no addresses, and it is the whole reason the proxy log is the better
    source. Reverse DNS is Google's and Bing's own documented way to tell
    their crawler from anyone wearing its name.

    Done locally rather than over SSH: it is a public DNS lookup, it needs no
    production access, and it keeps this out of shell quoting. Sampled rather
    than exhaustive, because the answer per address is stable and this is a
    report, not a firewall. An address with no PTR is reported as unverified
    rather than as a forgery: plenty of legitimate infrastructure has none.
    """
    import socket
    names = {}
    # Caller order is preserved deliberately: main() passes the most-seen
    # addresses first. Sorting by IP string meant the sample was entirely
    # 40.77.x (Bing) and never reached Googlebot's 66.249.x, so the one
    # crawler this business cares about most was the one never checked.
    for ip in list(ips)[:limit]:
        try:
            socket.setdefaulttimeout(4)
            names[ip] = socket.gethostbyaddr(ip)[0]
        except Exception:                                      # noqa: BLE001
            names[ip] = "(no PTR)"
    return names


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
    ap.add_argument("--source", choices=("proxy", "container"),
                    default="proxy",
                    help="proxy = Nginx Proxy Manager's log, which has weeks "
                         "of history and client IPs; container = this site's "
                         "own IP-free log, which starts 2026-09-20")
    ap.add_argument("--verify", action="store_true",
                    help="reverse-DNS a sample of addresses claiming to be a "
                         "search engine")
    ap.add_argument("--bot", default="")
    ap.add_argument("--paths", action="store_true",
                    help="list the most fetched paths")
    args = ap.parse_args()

    raw, note = fetch_proxy() if args.source == "proxy" else fetch()
    if note:
        print("UNCHECKED: " + note)
        return 2

    cutoff = (datetime.datetime.now(datetime.timezone.utc)
              - datetime.timedelta(days=args.days)).strftime("%Y-%m-%d")
    rows, unparsed = [], 0
    pat = PROXY_LINE if args.source == "proxy" else LINE
    for line in raw:
        m = pat.match(line)
        if not m:
            unparsed += 1
            continue
        d = m.groupdict()
        d["day"] = (_proxy_day(d["ts"]) if args.source == "proxy"
                    else d["ts"][:10])
        if not d["day"] or d["day"] < cutoff:
            continue
        d.setdefault("ip", "")
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

    if args.verify:
        claim = [ip for ip, _ in collections.Counter(
            r["ip"] for r in search if r.get("ip")).most_common()]
        names = verify_bots(claim)
        if not names:
            print("    (no addresses to verify: the container log keeps none "
                  "by design, so use --source proxy)")
        else:
            print("")
            print("  REVERSE DNS on addresses claiming to be a search engine (sampled)")
            for ip, host in sorted(names.items()):
                # .spider.yandex.com is Yandex's own documented PTR and it
                # was missing from the first version of this list, which
                # reported two genuine Yandex crawlers as UNVERIFIED. A list
                # that is wrong in the accusing direction is worse than none.
                good = host.endswith((".googlebot.com", ".google.com",
                                      ".search.msn.com", ".spider.yandex.com",
                                      ".yandex.ru", ".yandex.net",
                                      ".applebot.apple.com",
                                      ".crawl.baidu.com"))
                print("    %-16s %-42s %s"
                      % (ip, host[:42], "verified" if good else "UNVERIFIED"))

    if args.paths:
        sel = [r for r in rows
               if not args.bot or args.bot.lower() in r["bot"].lower()]
        print("")
        print("  MOST FETCHED PATHS%s"
              % (" by %s" % args.bot if args.bot else ""))
        for path, n in collections.Counter(
                r["path"] for r in sel).most_common(25):
            print("    %5d  %s" % (n, path))

    ext = [r for r in rows
           if r["ref"] not in ("-", "") and "6s-success.com" not in r["ref"]]
    refs = collections.Counter(r["ref"] for r in ext)
    if refs:
        print("")
        print("  EXTERNAL REFERRERS")
        print("    A REFERRER IS A HEADER THE CLIENT CHOOSES. It is not "
              "evidence of a click.")
        # Measured 2026-09-20 and the reason this warning is here rather than
        # in a doc nobody opens: 365 requests on this log claimed to come from
        # Google, 130 of them to /quest.html, while Umami recorded 7 Google
        # pageviews in the same period. The addresses were AWS (34.208.x,
        # 35.85.x) and Alibaba Cloud (47.79.x) in a burst over five days.
        # They are scrapers wearing a search engine's referrer. Reading that
        # 365 as arrivals would have overstated this site's organic traffic
        # by a factor of fifty.
        for ref, n in refs.most_common(12):
            who = [r["ip"] for r in ext if r["ref"] == ref and r.get("ip")]
            uniq = len(set(who))
            # Always print the address spread rather than flagging on a
            # ratio. A threshold was tried first and missed the very case
            # this exists for: the 365 fake Google referrals came from
            # dozens of different cloud addresses, so concentration was low
            # and a "few addresses" rule said nothing. The spread is useful
            # either way and lets the reader judge instead of trusting a
            # rule that has already been wrong once.
            print("    %5d  %-58s  %d address(es)" % (n, ref[:58], uniq))
    return 0


if __name__ == "__main__":
    sys.exit(main())
