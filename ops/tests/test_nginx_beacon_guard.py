#!/usr/bin/env python3
"""
Our own headless browser must not be able to count as a visitor.

WHY THIS TEST EXISTS
--------------------
Measured 2026-10-03 from the site's own persistent access log, 15 days:
9,113 analytics beacons reached /stats/api/send from a HeadlessChrome user
agent, against 1 to 11 pageviews a day recorded in Umami for this site. They
are this repository's own screenshot and visual-audit tooling, which drives a
real Chromium and so executes the tracker on every page it loads.

Umami was discarding them, which is why no reported figure was ever wrong.
It discarded them because its bot list happens to recognise the string
HeadlessChrome: a third-party heuristic, not a decision this repository made
or tests. Traffic is the one number every objective in GOALS.md rests on and
the site measures 7 to 22 visitors a week, so the gap between the real figure
and 9,000 of our own pageviews was one upstream library change wide.

site/nginx/default.conf now refuses those beacons itself. This test is what
stops the refusal being deleted, reordered after proxy_pass (where it would
never run), or quietly narrowed to something a headless UA no longer matches.

Run:  python ops/tests/test_nginx_beacon_guard.py
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CONF = os.path.join(ROOT, 'site', 'nginx', 'default.conf')

# The exact user agents measured hitting this endpoint, and the ones that
# must still get through. Real strings from the log, not invented.
MUST_REFUSE = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
    'like Gecko) HeadlessChrome/153.0.0.0 Safari/537.36 Edg/153.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
    'like Gecko) HeadlessChrome/154.0.0.0 Safari/537.36 Edg/154.0.0.0',
    '6s-freshness',
    '6s-linkcheck',
    '6s-success-indexnow/1.0',
]
MUST_ALLOW = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
    'like Gecko) Chrome/145.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/'
    '605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
]


def send_block(text):
    """The body of `location = /stats/api/send { ... }`, or ''."""
    m = re.search(r'location\s*=\s*/stats/api/send\s*' + chr(123),
                  text)
    if not m:
        return ''
    i = m.end()
    depth = 1
    while i < len(text) and depth:
        if text[i] == chr(123):
            depth += 1
        elif text[i] == chr(125):
            depth -= 1
        i += 1
    return text[m.end():i - 1]


def main():
    fails = []
    text = io.open(CONF, encoding='utf-8').read()
    block = send_block(text)
    if not block:
        print('FAIL')
        print(' - no `location = /stats/api/send` block in '
              'site/nginx/default.conf, so the beacon endpoint this test '
              'guards does not exist as expected')
        return 1

    # 1. The guard exists, and nginx's own matching rules are respected: an
    #    `if` placed after proxy_pass still evaluates, but a reader cannot
    #    tell, so require it before. Order is the thing most likely to be
    #    broken by a later edit that only moves lines around.
    g = re.search(r'if\s*\(\s*\$http_user_agent\s*(~\*?|~)\s*'
                  + chr(34) + r'([^' + chr(34) + r']+)' + chr(34)
                  + r'\s*\)\s*' + chr(123) + r'\s*return\s+(\d{3})',
                  block)
    if not g:
        fails.append('no `if ($http_user_agent ~* "...") { return NNN; }` '
                     'guard in the /stats/api/send block, so our own headless '
                     'tooling can count as a visitor again')
        print('FAIL')
        for f in fails:
            print(' -', f)
        return 1
    if block.index('proxy_pass') < g.start():
        fails.append('the user-agent guard appears AFTER proxy_pass, which '
                     'reads as dead to anyone maintaining this file')
    if g.group(3) not in ('204', '403', '444'):
        fails.append('the guard returns %s; a beacon is fire-and-forget so a '
                     'redirect or a body is wrong here' % g.group(3))

    # 2. The pattern must actually match every user agent measured abusing
    #    this endpoint. Compiled and run against the real strings rather than
    #    eyeballed, because a pattern that matches nothing looks exactly like
    #    a guard that works (LEARNINGS.md LRN-0033).
    pattern, flags = g.group(2), re.I if '*' in g.group(1) else 0
    try:
        rx = re.compile(pattern, flags)
    except re.error as e:
        fails.append('the guard pattern %r does not compile as a regex: %s'
                     % (pattern, e))
        rx = None
    if rx is not None:
        for ua in MUST_REFUSE:
            if not rx.search(ua):
                fails.append('the guard does NOT match a user agent measured '
                             'hitting this endpoint: %r' % ua[:60])
        # 3. And it must not catch a real visitor. A guard that matched
        #    everything would pass case 2 perfectly and delete the business's
        #    only traffic figure.
        for ua in MUST_ALLOW:
            if rx.search(ua):
                fails.append('the guard WOULD refuse a real browser, so live '
                             'traffic would stop being counted: %r' % ua[:60])

    if fails:
        print('FAIL')
        for f in fails:
            print(' -', f)
        return 1
    print('OK: nginx beacon guard, %d measured tooling agent(s) refused, '
          '%d real browser(s) still counted'
          % (len(MUST_REFUSE), len(MUST_ALLOW)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
