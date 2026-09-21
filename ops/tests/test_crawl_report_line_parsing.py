#!/usr/bin/env python3
"""
Prove ops/crawl_report.py's PROXY_LINE regex actually parses both real log
line shapes, and prove the check can fail (the class of defect it exists to
prevent has already happened once, silently).

crawl_report.py's own comment records that 1,162 real Nginx Proxy Manager
log lines were being dropped as unparseable until PROXY_LINE was widened to
handle a second column shape: the plain-HTTP-to-HTTPS redirect, where there
is no distinct upstream status and every column after it shifts left by one.
A dropped line does not raise or warn, it is silently counted as "unparsed"
and never reaches the day/bot/purpose breakdown, so a crawler that mostly
redirects (nearly everything does, once, from http to https) would look
less active than it really is, on the one measurement instrument this
business has while Search Console stays unverified.

That regression had no test guarding it before this file: the existing
test_crawl_report_purpose.py exercises classify()/purpose() on already-
extracted user-agent strings, never the line parser that has to extract
them first.

Run:  python ops/tests/test_crawl_report_line_parsing.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import crawl_report as CR                                     # noqa: E402

# The two real shapes crawl_report.py's own module docstring/comment record,
# reproduced as literal lines rather than paraphrased.
NORMAL_HTTPS = (
    '[13/Sep/2026:13:00:40 +0000] - 200 200 - GET https 6s-success.com '
    '"/robots.txt" [Client 66.249.74.196] [Length 231] [Gzip -] '
    '[Sent-to 187.77.25.50] '
    '"Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" "-"'
)
HTTP_REDIRECT = (
    '[13/Sep/2026:13:05:12 +0000] - - 301 - GET http 6s-success.com '
    '"/quest.html" [Client 40.77.167.88] [Length 0] [Gzip -] '
    '[Sent-to 187.77.25.50] '
    '"Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)" "-"'
)

# A stand-in for the narrower pattern the docstring says used to ship: it
# expects exactly one token, a 3-digit status, a numeric upstream status,
# one more token, then the method, with no room for the redirect shape's
# missing upstream-status column. This is what "1,162 lines dropped" looked
# like from the regex's point of view.
NAIVE_PRE_FIX_LINE = re.compile(
    r'^\[(?P<ts>[^\]]+)\]\s+\S+\s+(?P<status>\d{3})\s+\d+\s+\S+\s+'
    r'(?P<method>[A-Z]+)\s+(?P<scheme>\S+)\s+(?P<host>\S+)\s+'
    r'"(?P<path>[^"]*)"\s+\[Client (?P<ip>[^\]]+)\]\s+'
    r'\[Length (?P<bytes>[^\]]*)\].*?'
    r'"(?P<ua>[^"]*)"\s+"(?P<ref>[^"]*)"\s*$')


def main() -> int:
    fails = []

    m = CR.PROXY_LINE.match(NORMAL_HTTPS)
    if not m:
        fails.append("PROXY_LINE did not match the normal HTTPS line shape at all")
    else:
        d = m.groupdict()
        want = {"status": "200", "method": "GET", "scheme": "https",
                "host": "6s-success.com", "path": "/robots.txt",
                "ip": "66.249.74.196", "bytes": "231"}
        for k, v in want.items():
            if d.get(k) != v:
                fails.append(f"normal HTTPS line: {k} = {d.get(k)!r}, expected {v!r}")
        if "Googlebot" not in d.get("ua", ""):
            fails.append(f"normal HTTPS line: ua lost, got {d.get('ua')!r}")

    m2 = CR.PROXY_LINE.match(HTTP_REDIRECT)
    if not m2:
        fails.append(
            "PROXY_LINE did not match the plain-HTTP redirect line shape: "
            "this is the exact 1,162-dropped-line regression the widened "
            "regex exists to prevent")
    else:
        d2 = m2.groupdict()
        want2 = {"status": "301", "method": "GET", "scheme": "http",
                 "host": "6s-success.com", "path": "/quest.html",
                 "ip": "40.77.167.88", "bytes": "0"}
        for k, v in want2.items():
            if d2.get(k) != v:
                fails.append(f"redirect line: {k} = {d2.get(k)!r}, expected {v!r}")
        if "bingbot" not in d2.get("ua", "").lower():
            fails.append(f"redirect line: ua lost, got {d2.get('ua')!r}")

    # A genuinely malformed line (no brackets at all) must fail to match,
    # not silently succeed with garbage groups: an unparsed line should be
    # counted as unparsed, never guessed at.
    garbage = "this is not a log line at all"
    if CR.PROXY_LINE.match(garbage):
        fails.append("PROXY_LINE matched a non-log-line string; it should return None")

    # Prove the check can fail: the naive pre-widen pattern must reproduce
    # the real historical defect on the redirect shape while still handling
    # the plain shape, so this is a genuine regression test and not a
    # tautology that only ever matches its own regex.
    if not NAIVE_PRE_FIX_LINE.match(NORMAL_HTTPS):
        fails.append(
            "test setup broken: the naive pre-fix pattern should still "
            "match the normal HTTPS line")
    if NAIVE_PRE_FIX_LINE.match(HTTP_REDIRECT):
        fails.append(
            "test setup broken: the naive pre-fix pattern should NOT match "
            "the redirect line, or it does not reproduce the real defect")

    if fails:
        print("FAIL:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("OK: PROXY_LINE parses both real log line shapes correctly, "
          "rejects a non-log line, and the naive pre-fix pattern was "
          "proved to reproduce the original dropped-line defect")
    return 0


if __name__ == "__main__":
    sys.exit(main())
