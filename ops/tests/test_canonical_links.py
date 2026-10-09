#!/usr/bin/env python3
"""
Prove canonical_links.py's rewrite can see a link that carries a URL
fragment, not just a bare .html link.

Found live 2026-10-09, second-pass cold read: LINK's own regex required
".html" to sit immediately before the closing quote, so a real link like
CAPACITY_ARTICLE's "zone-too-small-for-what-it-holds.html#honest-count"
(114 occurrences, one per zone page) never matched at all. That made 114
real .html links invisible both to the rewrite pass and to this file's own
"N .html" tally, which exists specifically to measure this split. The
regex now captures an optional trailing (#fragment)? group and reattaches
it after stripping ".html"/"index.html"/"", and the tally regex strips a
trailing #fragment or ?query before judging the extension.

Run:  python ops/tests/test_canonical_links.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import canonical_links as C                                   # noqa: E402


def main() -> int:
    fails = []

    # Case 1: a fragment-bearing link to an existing target is rewritten,
    # extensionless, with the fragment preserved unchanged.
    page = os.path.join(ROOT, "site", "zones", "_test_fixture.html")
    target = os.path.join(ROOT, "site", "articles",
                           "zone-too-small-for-what-it-holds.html")
    if not os.path.exists(target):
        fails.append("fixture target article is missing: %s" % target)
    else:
        s = ('<a href="../articles/zone-too-small-for-what-it-holds.html'
             '#honest-count">Run the honest count</a>')
        new, (n, miss) = C.rewrite(page, s)
        if n != 1 or miss != 0:
            fails.append("expected 1 rewritten / 0 skipped, got n=%d miss=%d"
                         % (n, miss))
        want = ('<a href="../articles/zone-too-small-for-what-it-holds'
                '#honest-count">Run the honest count</a>')
        if new != want:
            fails.append("fragment link rewritten wrong: got %r, want %r"
                         % (new, want))

    # Case 2: a plain .html link with no fragment still rewrites exactly as
    # before (no regression from adding the optional group).
    if os.path.exists(target):
        s = '<a href="../articles/zone-too-small-for-what-it-holds.html">x</a>'
        new, (n, miss) = C.rewrite(page, s)
        want = '<a href="../articles/zone-too-small-for-what-it-holds">x</a>'
        if new != want:
            fails.append("plain link regressed: got %r, want %r" % (new, want))

    # Case 3: a fragment link to a target that does NOT exist is left alone
    # and counted as skipped, same as a bare missing link always was.
    s = '<a href="../articles/no-such-article.html#section">x</a>'
    new, (n, miss) = C.rewrite(page, s)
    if new != s or n != 0 or miss != 1:
        fails.append("missing-target fragment link should be left untouched "
                     "and counted as skipped, got new=%r n=%d miss=%d"
                     % (new, n, miss))

    total = 3
    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {total - len(fails)} of {total} cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
