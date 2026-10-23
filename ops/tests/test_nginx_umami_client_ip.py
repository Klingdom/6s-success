#!/usr/bin/env python3
"""
Umami must be handed the visitor's address, not Nginx Proxy Manager's.

WHY THIS TEST EXISTS
--------------------
Measured 2026-10-23: all 109 Umami sessions this site had ever recorded had
country NULL, while the other site on the same Umami instance had a country on
1,118 of 1,118. Umami 3.1 takes the client address from X-Real-IP before
X-Forwarded-For, and both /stats locations in site/nginx/default.conf set
X-Real-IP to $remote_addr, which inside this container is the proxy's bridge
address. A private address has no location, so "where do visitors come from"
was unanswerable for the whole life of the site, silently: every beacon was
still accepted and counted.

This pins the fix: every proxy hop to Umami forwards $umami_client_ip, and that
variable is mapped from the X-Real-IP Nginx Proxy Manager sets.

Run:  python ops/tests/test_nginx_umami_client_ip.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CONF = os.path.join(ROOT, 'site', 'nginx', 'default.conf')


def problems(text):
    out = []
    code = '\n'.join(l.split('#', 1)[0] for l in text.splitlines())
    if not re.search(r'map\s+\$http_x_real_ip\s+\$umami_client_ip\s*\{[^}]*'
                     r'default\s+\$http_x_real_ip\s*;', code):
        out.append('no map from $http_x_real_ip to $umami_client_ip')
    blocks = re.findall(r'location\s+=?\s*/stats/[^{]*\{(.*?)\n    \}', code,
                        re.S)
    hops = [b for b in blocks if 'proxy_pass' in b]
    if len(hops) < 2:
        out.append('expected 2 proxy hops to Umami, found %d' % len(hops))
    for b in hops:
        m = re.search(r'proxy_set_header\s+X-Real-IP\s+(\S+);', b)
        if not m:
            out.append('a /stats hop sets no X-Real-IP (Umami would fall '
                       'back to a header chain we do not control)')
        elif m.group(1) != '$umami_client_ip':
            out.append('a /stats hop sends X-Real-IP %s, not the visitor'
                       % m.group(1))
    return out


def main():
    text = open(CONF, encoding='utf-8').read()
    bad = problems(text)
    # Prove the check can fail: put back the exact line that shipped broken.
    broken = text.replace('X-Real-IP         $umami_client_ip;',
                          'X-Real-IP         $remote_addr;', 1)
    planted = problems(broken)
    ok = True
    if bad:
        ok = False
        print('FAIL live config: %s' % bad)
    else:
        print('ok   live config forwards the visitor to Umami')
    if not planted:
        ok = False
        print('FAIL the check did not catch $remote_addr planted back')
    else:
        print('ok   planted $remote_addr caught: %s' % planted[0])
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
