#!/usr/bin/env python3
"""
ops/indexnow.py must not read a line-ending difference as a content change.

WHY THIS TEST EXISTS
--------------------
Read out of ops/indexnow-log.json on 2026-10-03. Six runs that morning
announced 6, 6, 12, 30, 7 and 14 URLs, which is what a change-notification
channel should look like. Then two consecutive runs each announced all 210.
The first was honest, a measure.js refingerprint really did change every
page. The second was not: nothing changed between them except which machine
took the hash. CI checks out LF; this workstation has core.autocrlf=true and
checks out CRLF. Measured directly at the time: all 211 stored hashes matched
a raw-byte reading and exactly 1 matched an LF-normalised one, so every
alternation between a scheduled run and an interactive session re-announced
the whole site.

indexnow.py's own module docstring says re-blasting the whole site is how a
domain earns a rate limit rather than a crawl, so this was the file breaking
its own stated rule, several times a day, on a domain with no crawl trust to
spend.

Run:  python ops/tests/test_indexnow_page_hash.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
import indexnow as inx                                   # noqa: E402


CR = bytes([13])
LFEND_ONLY = bytes([10])
CRLFEND_ONLY = bytes([13, 10])
LFEND = bytes([10])
DQ = chr(34)


def main():
    fails = []

    # 1. The same page, checked out two ways, is the same page.
    lf = b'<html>line one' + LFEND_ONLY + b'line two</html>' + LFEND
    crlf = lf.replace(LFEND_ONLY, CRLFEND_ONLY)
    if crlf == lf:
        fails.append('the test fixture has no line endings to differ on, so case 1 proves nothing')
    if inx.page_hash(lf) != inx.page_hash(crlf):
        fails.append('page_hash gave different answers for the LF and CRLF checkouts of one page, which is the 2026-10-03 defect')

    # 2. It must still notice a real change. A hash that returns a constant
    #    would pass case 1 perfectly and make the tool useless.
    if inx.page_hash(lf) == inx.page_hash(lf.replace(b'two', b'three')):
        fails.append('page_hash did not change when the page content did, so it cannot detect a change at all')

    # 3. A lone CR is not a line ending here and must not be normalised away,
    #    or two genuinely different files could collide.
    if inx.page_hash(b'a' + CR + b'b') == inx.page_hash(b'a' + LFEND_ONLY + b'b'):
        fails.append('page_hash treated a bare CR as an LF, which is a collision between two different files')

    # 4. The recipe must be named, and the name must travel with the hashes,
    #    or a future change to page_hash silently compares apples to pears.
    if not getattr(inx, 'HASH_ALGO', ''):
        fails.append('indexnow.py has no HASH_ALGO, so nothing records which recipe a stored baseline was taken with')
    src = open(inx.__file__, encoding='utf-8').read()
    for needed in ('log[' + DQ + 'hash_algo' + DQ + '] = HASH_ALGO',
                   'BASELINE NOT COMPARABLE'):
        if needed not in src:
            fails.append('indexnow.py is missing %r, so a recipe change would not be recorded or refused' % needed)

    if fails:
        print('FAIL')
        for f in fails:
            print(' -', f)
        return 1
    print('OK: indexnow page_hash, 4/4 checks pass (EOL-insensitive, still change-sensitive, no bare-CR collision, recipe recorded)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
