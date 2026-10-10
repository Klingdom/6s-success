#!/usr/bin/env python3
"""
Every zone page's jump list must point at sections that exist, above them.

WHY THIS EXISTS
---------------
Measured 2026-10-09 across all 114 zone pages: median 4,462 words and 22 h2
sections, against about 2,100 words in early September. Each addition was
defensible alone (common_items, sort_scope, capacity, variants, the kit, the
surface-by-surface clean) and nobody measured the total.

On the Entryway Landing Spot the step-by-step instructions, the thing somebody
standing in their entryway actually wants, begin at word 1,005 behind five
sections. That ordering is deliberate and stays (CLAUDE.md 6, root cause before
solution). What was missing was any way past it: the page had thirteen in-page
links and every one sat at word 1,318 or later, inside the kit copy, pointing
backwards.

WHAT COULD GO WRONG, WHICH IS WHAT THIS CHECKS
----------------------------------------------
Half the linkable sections are conditional. A zone with no capacity, no
variants, no storage block or no surface-by-surface clean renders none of them,
so a hardcoded list would put dead anchors on real pages. This repository has
shipped exactly that before: 44 dead deck anchors, commit 223f5111. The nav is
therefore built from the finished page, and this proves it per page rather than
on one sample.

Run:  python ops/tests/test_zone_jump_nav.py
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
ZONES = os.path.join(ROOT, 'site', 'zones')

# Each label and a word that MUST appear in the heading it lands on. The
# pairing is written down so changing either side has to be deliberate: a nav
# label that no longer describes its destination is the same copy-and-control
# disagreement gate_price_matches_its_own_link exists for, one level up.
EXPECTED = {
    'diagnosis': ('Which of these is true here?', 'true here'),
    'passes': ('The six passes, in order', 'six passes'),
    'what-to-store-it-in': ('What to store it in', 'store it in'),
    'shine-detail': ('Cleaning it, surface by surface', 'surface by surface'),
    'capacity': ('How much it holds', 'How much'),
    'variants': ('When this is not your home', 'When this does not describe'),
}
MIN_LINKS = 3


def main():
    fails = []
    if not os.path.isdir(ZONES):
        print('NOT VERIFIED: no site/zones directory, so nothing was checked.')
        return 0
    # _visual_probe.html is audit_visual.py's own scratch shell, excluded by
    # exact name for the same reason ops/audit_pages.py's pages() excludes
    # it: a run whose window overlaps that tool's write/cleanup can catch it
    # mid-existence and report it as a real zone page with no jump list.
    names = [n for n in sorted(os.listdir(ZONES))
             if n.endswith('.html') and n != 'index.html'
             and n != '_visual_probe.html']
    if len(names) < 50:
        print('NOT VERIFIED: only %d zone page(s) on disk, too few to be the '
              'real corpus. Nothing below was checked.' % len(names))
        return 0

    counts = []
    for n in names:
        h = io.open(os.path.join(ZONES, n), encoding='utf-8',
                    errors='replace').read()
        if 'ZONE-JUMP' in h:
            fails.append('%s: the jump marker survived into the page, so an '
                         'HTML comment shipped where the nav belongs' % n)
            continue
        navs = re.findall(r'<nav class="zone-jump".*?</nav>',
                          h, re.S)
        if not navs:
            fails.append('%s: no jump list at all' % n)
            continue
        if len(navs) > 1:
            fails.append('%s: %d jump lists on one page' % (n, len(navs)))
        nav = navs[0]
        if 'aria-label=' not in nav:
            fails.append('%s: the jump list is a <nav> with no accessible '
                         'name, so a screen reader announces an unlabelled '
                         'landmark' % n)
        links = re.findall(r'href="#([a-z0-9-]+)"', nav)
        counts.append(len(links))
        if len(links) < MIN_LINKS:
            fails.append('%s: jump list has %d link(s); below %d it costs more '
                         'attention than it saves' % (n, len(links), MIN_LINKS))
        if len(set(links)) != len(links):
            fails.append('%s: the jump list repeats a target' % n)
        for a in links:
            target = 'id=' + chr(34) + a + chr(34)
            if target not in h:
                fails.append('%s: jump link #%s points at no section on this '
                             'page' % (n, a))
                continue
            if h.index('href=' + chr(34) + '#' + a + chr(34)) > h.index(target):
                fails.append('%s: the jump list sits AFTER #%s, so it sends a '
                             'reader backwards' % (n, a))
            label, needle = EXPECTED.get(a, (None, None))
            if label is None:
                fails.append("%s: jump link #%s is not in the expected "
                             "table in this test, so its label is unchecked" % (n, a))
                continue
            if label not in nav:
                fails.append('%s: #%s is linked but its agreed label %r is not '
                             'in the nav' % (n, a, label))
            # The destination must actually be about what the label promises.
            after = h[h.index(target):h.index(target) + 1400]
            if needle.lower() not in after.lower():
                fails.append('%s: the label %r lands on a section whose own '
                             'text does not contain %r, so the nav is '
                             'describing something else' % (n, label, needle))

    if fails:
        print('FAIL')
        for f in fails[:12]:
            print(' -', f)
        if len(fails) > 12:
            print(' - ... and %d more' % (len(fails) - 12))
        return 1
    print('OK: %d zone page(s), every jump link resolves to a section above '
          'it and matches its own destination (%d to %d links each)'
          % (len(names), min(counts), max(counts)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
