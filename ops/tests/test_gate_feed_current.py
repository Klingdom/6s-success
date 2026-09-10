#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_feed_current() catches site/feed.xml drifting
from what ops/build_feed.py would write right now.

Added 2026-09-10 alongside ops/build_feed.py, a new Atom feed of the site's
root-cause articles: a zero-cost distribution surface, needing no account
only Phil can create, in a week where every other unblocked traffic lever
was already done or Phil-gated (GOALS.md O1, decision rule 1). Every field
in the feed is read back off the article pages themselves (title,
description, canonical link, JSON-LD dates), the same "source corrected,
artifact never re-derived" defect class this backlog names as dominant, so
this gate mirrors gate_sitemap_complete/gate_downloads_current's own
regenerate-and-diff pattern rather than trusting the file on sight.

Run:  python ops/tests/test_gate_feed_current.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import build_feed                                              # noqa: E402


def _run():
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_feed_current()
    return list(preflight.FAIL), list(preflight.WARN)


def main() -> int:
    fails = []
    real_feed = os.path.join(preflight.SITE, "feed.xml")

    # 1. The real, committed site/feed.xml: clean.
    f, w = _run()
    if f:
        fails.append("the real committed site/feed.xml failed: %r" % (f,))

    # 2. A stale feed (missing an entry the real corpus has) must fail, named.
    real = io.open(real_feed, encoding="utf-8").read()
    stale = real.replace("</feed>\n", "  <entry><title>ghost</title></entry>\n</feed>\n")
    backup = real_feed + ".bak"
    shutil.copy2(real_feed, backup)
    try:
        io.open(real_feed, "w", encoding="utf-8").write(stale)
        f, w = _run()
        if not f or "feed-current" not in f[0][0]:
            fails.append("a stale, hand-edited feed.xml was not caught by "
                         "name: %r" % (f,))
    finally:
        shutil.copy2(backup, real_feed)
        os.remove(backup)

    # 3. site/feed.xml missing entirely must fail, naming the fix command.
    tmp = tempfile.mkdtemp()
    old_site = preflight.SITE
    preflight.SITE = tmp
    try:
        f, w = _run()
        if not f or "does not exist" not in f[0][1]:
            fails.append("a missing site/feed.xml was not caught: %r" % (f,))
    finally:
        preflight.SITE = old_site
        shutil.rmtree(tmp)

    # 4. build_feed.entries() actually found real articles, so check #1 above
    #    was not vacuously passing on an empty corpus.
    rows = build_feed.entries()
    if len(rows) < 20:
        fails.append("build_feed.entries() found only %d articles, expected "
                     "20+; the parser may be silently failing to match "
                     "the real page shape." % len(rows))

    # 5. Re-verify the real file is clean after the restore, not left dirty
    #    by test 2's swap.
    f, w = _run()
    if f:
        fails.append("site/feed.xml was left dirty after the drift test: %r"
                     % (f,))

    if fails:
        print("FAIL")
        for x in fails:
            print(" -", x)
        return 1
    print("OK: gate_feed_current, 5/5 checks pass (%d real articles)"
          % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
