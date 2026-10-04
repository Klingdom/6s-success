#!/usr/bin/env python3
"""
6s-success.com must not serve another business's mailing-list consent.

WHAT WAS LIVE, AND FOR HOW LONG
-------------------------------
site/nginx/default.conf proxied /subscribe to Listmonk's public subscription
form. On 2026-10-04 that page was fetched and READ rather than pattern-matched,
and it rendered three list checkboxes with every one of them pre-ticked:

    [x] Compassion Benchmark Weekly Digest
    [x] Compassion Benchmark Product & Research Updates
    [x] 6S Success Readers

Two of those belong to a different business that shares the Listmonk instance.
A visitor to 6s-success.com who submitted that form subscribed himself, by
default, to two lists belonging to a company he had never heard of. CLAUDE.md
section 8 rules out a pre-ticked consent by name; section 47 says sharing must
be intentional. site/assets/js/site.js's own footer comment states that nothing
here pre-ticks a consent, which was true of our form and false of the page our
domain served.

Nobody was harmed, and that was checked rather than hoped: of 549 requests to
/subscribe in the whole retained access log, 547 were this repository's own
ops/check_integrations.py probe and 2 were curl. No crawler, no visitor, zero
POSTs ever, and the list has 0 subscribers.

WHY A TEST AND NOT JUST A FIX
-----------------------------
The route existed because somebody was trying to make email capture work, which
is a real and still-open objective (GOALS.md O2, OWNER-ACTIONS item 7). The next
session to pick that up will reach for exactly this proxy line again. Listmonk's
public form cannot be scoped to one list by URL: it renders every public list on
the instance. So the prerequisite is a 6S-only subscription surface, and this
file is what makes that prerequisite impossible to skip.

It also pins the shape of the check that reports on it. The previous version of
ops/check_integrations.py passed if /subscribe returned a page containing the
word subscribe and an html tag, which is to say it asserted the defect was
present and called it healthy, for weeks.

Run:  python ops/tests/test_no_foreign_consent_on_our_domain.py
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CONF = os.path.join(ROOT, 'site', 'nginx', 'default.conf')
CHECKER = os.path.join(ROOT, 'ops', 'check_integrations.py')

# Listmonk's public form endpoint. Any proxy_pass reaching it serves every
# public list on that instance, ours and theirs.
PUBLIC_FORM = 'subscription/form'


def main():
    fails = []
    conf = io.open(CONF, encoding='utf-8').read()

    # 1. No DIRECTIVE may reach Listmonk's all-lists public form. Comments may
    #    discuss it; the one above this very route does, at length.
    #
    #    This case was wrong when first written, and the planted defect is what
    #    said so. It matched `^    proxy_pass` with exactly four leading
    #    spaces, and every proxy_pass in this file sits inside a location block
    #    at eight. So it matched nothing at all, and a restored /subscribe
    #    proxy sailed past it reporting OK. Anchoring a check on indentation is
    #    anchoring it on formatting.
    live = [ln for ln in conf.splitlines()
            if ln.strip() and not ln.strip().startswith('#')]
    offenders = [ln.strip() for ln in live if PUBLIC_FORM in ln]
    if offenders:
        fails.append('site/nginx/default.conf reaches the Listmonk public '
                     'subscription form on %d non-comment line(s): %s. That '
                     'form renders every public list on a shared instance, '
                     'including another business, with consent pre-ticked. '
                     'Scope the surface to this business before exposing it.'
                     % (len(offenders), offenders[:2]))

    # 2. And no /subscribe route may exist that proxies anywhere into Listmonk,
    #    even at a different path: its public pages are instance-wide by
    #    design. A route serving our own static content would be fine, so this
    #    looks for the upstream rather than for the location.
    sub = [ln.strip() for ln in live
           if 'proxy_pass' in ln and ':8081' in ln]
    if sub:
        fails.append('site/nginx/default.conf proxies to Listmonk on port '
                     '8081 from %d non-comment line(s): %s. Every public page '
                     'that instance serves lists both businesses.'
                     % (len(sub), sub[:2]))
    # 3. The checker must still assert the absence, not the presence. Proving
    #    this by reading the source rather than by running it, because running
    #    it needs live network reach the sandbox may not have, and a skipped
    #    network check must never read as a pass.
    checker = io.open(CHECKER, encoding='utf-8').read()
    if 'FOREIGN_LISTS' not in checker:
        fails.append('ops/check_integrations.py no longer knows the foreign '
                     'list names, so nothing would notice the form coming '
                     'back')
    else:
        # Plain string slicing, not a regex. The first version built the
        # pattern with chr(40) and chr(41), which are ( and ) and therefore a
        # GROUP in a regex rather than literal parentheses, so it matched
        # zero-width and reported 0 list(s) watched against a file that names
        # two. A pattern that cannot match is indistinguishable from the thing
        # it looks for being absent (LEARNINGS.md LRN-0033).
        # Anchored on the DEFINITION, not the first mention. The first
        # mention is the use site, whose text is `for name in FOREIGN_LISTS if
        # name in (body3 or "")`, and slicing to the next closing paren from
        # there yields no list names at all, which read as 0 watched.
        head = checker.index('FOREIGN_LISTS = ' + chr(40))
        body = checker[head:checker.index(chr(41), head)]
        quotes = chr(34) + chr(39)
        cls = '[' + quotes + ']'
        found = re.findall(cls + '([^' + quotes + ']{8,})' + cls,
                           body)
        if len(found) < 2:
            fails.append('FOREIGN_LISTS names %d list(s); the two measured on '
                         '/subscribe were both Compassion Benchmark lists, so '
                         'fewer than two means one is no longer watched'
                         % len(found))
    if 'not Listmonk' in checker and 'carries its own title' in checker:
        fails.append('ops/check_integrations.py has reverted to passing when '
                     'the Listmonk public form IS reachable here, which is the '
                     'assertion that called the defect healthy')

    if fails:
        print('FAIL')
        for f in fails:
            print(' -', f)
        return 1
    print('OK: no route serves another business pre-ticked mailing lists, '
          'and the checker still watches for their names')
    return 0


if __name__ == '__main__':
    sys.exit(main())
