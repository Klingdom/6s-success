#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_llms_txt_current() catches a promoted, free,
ungated page going unmentioned in site/llms.txt, the file AI answer engines
are meant to read to learn what a site offers.

Found 2026-09-09: llms.txt named /zones/, /rooms/, /articles/, /method.html,
/quest.html and /shop.html but not /deck.html (live since before this file
was written) or /kitchen-deck.html (shipped 2026-09-08, 72 free cards).
Nothing generated this file and nothing checked it, so a real free lead
magnet was invisible to it by default rather than by any decision. Fixed by
hand; this gate stops the same drift recurring.

Run:  python ops/tests/test_gate_llms_txt_current.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

GOOD = (
    "# 6S Success\n\n"
    "- /zones/ : 114 micro zone guides.\n"
    "- /rooms/ : 20 room pages.\n"
    "- /articles/ : 30 articles. /feed.xml : an Atom feed of them.\n"
    "- /quest.html : a free browser app.\n"
    "- /deck.html : the Entryway deck, free to print.\n"
    "- /kitchen-deck.html : the Kitchen deck, free to read or print.\n"
    "- /shop.html : the products.\n"
)

MISSING_DECKS = (
    "# 6S Success\n\n"
    "- /zones/ : 114 micro zone guides.\n"
    "- /rooms/ : 20 room pages.\n"
    "- /feed.xml : an Atom feed of the articles.\n"
    "- /articles/ : 30 articles.\n"
    "- /quest.html : a free browser app.\n"
    "- /shop.html : the products.\n"
)

# Named to match gate_llms_txt_current's own count regex, so cases 6-7 below
# exercise the article-count check independently of the asset-name check
# above them.
COUNT_BODY = (
    "# 6S Success\n\n"
    "- /zones/ : 114 micro zone guides.\n"
    "- /rooms/ : 20 room pages.\n"
    "- /articles/ : {n} explanatory articles on root causes and habits.\n"
    "  /feed.xml : an Atom feed of them.\n"
    "- /quest.html : a free browser app.\n"
    "- /deck.html : the Entryway deck, free to print.\n"
    "- /kitchen-deck.html : the Kitchen deck, free to read or print.\n"
    "- /shop.html : the products.\n"
)


def _run(body, articles=None):
    """articles: real *.html filenames to create under a fake site/articles/,
    so the count check has something real to compare the claimed number
    against, the same way it reads the live site/articles/ directory."""
    tmp = tempfile.mkdtemp()
    if body is not None:
        io.open(os.path.join(tmp, "llms.txt"), "w", encoding="utf-8").write(body)
    if articles is not None:
        adir = os.path.join(tmp, "articles")
        os.makedirs(adir, exist_ok=True)
        io.open(os.path.join(adir, "index.html"), "w",
               encoding="utf-8").write("<html></html>")
        for name in articles:
            io.open(os.path.join(adir, name), "w",
                   encoding="utf-8").write("<html></html>")
    old_site = preflight.SITE
    preflight.SITE = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_llms_txt_current()
        return list(preflight.FAIL)
    finally:
        preflight.SITE = old_site
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. A clean file naming every promoted asset: no failure.
    r = _run(GOOD)
    if r:
        fails.append("clean llms.txt wrongly flagged: %r" % (r,))

    # 2. The exact real-world regression: the two decks missing.
    r = _run(MISSING_DECKS)
    if not r or "/deck.html" not in r[0][1] or "/kitchen-deck.html" not in r[0][1]:
        fails.append("missing-decks regression not caught by name: %r" % (r,))

    # 3. The file absent entirely.
    r = _run(None)
    if not r or "does not exist" not in r[0][1]:
        fails.append("absent llms.txt not caught: %r" % (r,))

    # 4. The mudroom deck must NOT be required: Phil's own hold decision
    #    (BACKLOG-2026-H2.md 2.7) means a page naming everything except the
    #    mudroom deck is still correct, not a violation.
    r = _run(GOOD)
    if r:
        fails.append("a page correctly withholding the mudroom deck was "
                      "flagged: %r" % (r,))

    # 5. The real, committed file: clean.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_llms_txt_current()
    if preflight.FAIL:
        fails.append("the real committed site/llms.txt failed: %r"
                     % (preflight.FAIL,))

    # 6. The exact real-world regression found 2026-09-11: llms.txt claims
    #    30 explanatory articles when only 29 real *.html files exist under
    #    site/articles/ (index.html excluded, matching the live defect where
    #    the bullet was never updated after an article count changed).
    r = _run(COUNT_BODY.format(n=30), articles=["a%02d.html" % i
                                                for i in range(29)])
    if not r or "30" not in r[0][1] or "29" not in r[0][1]:
        fails.append("stale article count not caught by name: %r" % (r,))

    # 7. The count matching the real files on disk: no failure.
    r = _run(COUNT_BODY.format(n=29), articles=["a%02d.html" % i
                                                for i in range(29)])
    if r:
        fails.append("a correct article count wrongly flagged: %r" % (r,))

    # 8. A body with no "explanatory articles" count at all (the pre-existing
    #    GOOD/MISSING_DECKS fixtures both look like this): warns, not a
    #    failure, since the phrasing this gate keys off is not guaranteed to
    #    survive every future rewrite of the bullet.
    r = _run(GOOD, articles=["a%02d.html" % i for i in range(5)])
    if r:
        fails.append("a body with no parseable count wrongly failed: %r"
                     % (r,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_llms_txt_current, 8/8 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
