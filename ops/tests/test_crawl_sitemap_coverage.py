#!/usr/bin/env python3
"""
ops/crawl_report.py must be able to say WHICH of our pages no crawler read.

WHY THIS TEST EXISTS
--------------------
Before 2026-10-03 the report could say how many distinct paths search engines
fetched (275) and never which sitemap URLs they had missed. 275 against a
211-URL sitemap looks like full coverage and does not prove it: the two sets
overlap rather than nest, and legacy .html redirects pad the first number.

The first attempt at the answer was a hand-written grep pipeline, which said
211 of 211. sitemap_coverage() said 210 of 211 and named the missing page, a
real article published the day before that no retrieval crawler had reached.
The pipeline was wrong because it matched a looser bot set and looser path
variants. That is LEARNINGS.md LRN-0033 happening again, so the number now
lives in the tool, and this file is what keeps the tool honest.

Run:  python ops/tests/test_crawl_sitemap_coverage.py
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import crawl_report as cr                                 # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
BASE = 'https://6s-success.com'


def sitemap_paths():
    text = io.open(os.path.join(ROOT, 'site', 'sitemap.xml'),
                   encoding='utf-8').read()
    out = []
    for u in re.findall(r'<loc>([^<]+)</loc>', text):
        p = u[len(BASE):] if u.startswith(BASE) else u
        out.append(p or '/')
    return out


def main():
    fails = []
    paths = sitemap_paths()
    if len(paths) < 50:
        print('NOT VERIFIED: site/sitemap.xml yielded %d URL(s), too few to '
              'exercise this. Nothing below was checked.' % len(paths))
        return 0

    # 1. Fetched exactly the canonical set: nothing may be reported missing.
    total, covered, never = cr.sitemap_coverage(set(paths))
    if (total, covered, never) != (len(paths), len(paths), []):
        fails.append('fetching every canonical URL still reported %d of %d '
                     'with %d never: %s'
                     % (covered, total, len(never), never[:3]))

    # 2. Fetched nothing: every URL must be reported missing. A function that
    #    returned an empty never-list here would pass case 1 and be useless.
    total, covered, never = cr.sitemap_coverage(set())
    if covered != 0 or len(never) != len(paths):
        fails.append('fetching nothing reported %d covered and %d never, '
                     'expected 0 and %d' % (covered, len(never), len(paths)))

    # 3. A crawler that only ever hit the legacy .html form has still read the
    #    page, because this site 301s .html to the canonical extensionless URL.
    #    This is the variant handling the ad-hoc pipeline got wrong.
    html_only = {(p.rstrip('/') or '/') + '.html' for p in paths}
    total, covered, never = cr.sitemap_coverage(html_only)
    if never:
        fails.append('%d URL(s) counted as never fetched when only the .html '
                     'variant was fetched, e.g. %s' % (len(never), never[:3]))

    # 4. One withheld URL must be named, not merely counted.
    victim = paths[len(paths) // 2]
    total, covered, never = cr.sitemap_coverage(
        {p for p in paths if p != victim})
    if never != [victim]:
        fails.append('withholding %r reported never=%r' % (victim, never))

    # 5. An unreadable sitemap must report UNCHECKED, not clean coverage.
    saved = cr.ROOT
    try:
        cr.ROOT = os.path.join(ROOT, 'no-such-directory-for-this-test')
        total, covered, never = cr.sitemap_coverage(set(paths))
        if total is not None:
            fails.append('an unreadable sitemap reported %r of %r rather than '
                         'refusing to answer' % (covered, total))
    finally:
        cr.ROOT = saved

    if fails:
        print('FAIL')
        for f in fails:
            print(' -', f)
        return 1
    print('OK: crawl_report sitemap_coverage, 5/5 checks pass against the real '
          '%d-URL sitemap' % len(paths))
    return 0


if __name__ == '__main__':
    sys.exit(main())
