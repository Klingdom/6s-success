#!/usr/bin/env python3
"""
Prove gate_twitter_card_complete() catches a page missing its Twitter tags.

Found 2026-10-23: site/articles/index.html had og:title/og:description/
og:image (what LinkedIn and Facebook actually read) and a bare twitter:card
tag, but no twitter:title, twitter:description or twitter:image at all.
gate_share_cards_current did not catch it: its "unwired" check compares
share_cards.apply()'s output to the page, but apply() only rewrites the
content of a tag that already exists, so a missing tag sails through
unchanged. This gate checks tag presence directly instead.
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

PAGE = os.path.join(preflight.SITE, "articles", "index.html")


def _run():
    preflight.FAIL.clear()
    preflight.gate_twitter_card_complete()
    return [m for g, m in preflight.FAIL if g == "twitter-card-complete"]


def main():
    fails = []
    keep = io.open(PAGE, "rb").read()
    try:
        f = _run()
        if f:
            fails.append("the real tree failed: %r" % (f,))

        src = keep.decode("utf-8")
        lines = [l for l in src.split("\n")
                 if not (l.startswith('<meta name="twitter:title"')
                         or l.startswith('<meta name="twitter:description"')
                         or l.startswith('<meta name="twitter:image"'))]
        io.open(PAGE, "w", encoding="utf-8", newline="").write("\n".join(lines))
        f = _run()
        if not any("articles/index.html" in m for m in f):
            fails.append("a page missing its twitter: tags entirely was not "
                         "caught: %r" % (f,))
    finally:
        io.open(PAGE, "wb").write(keep)

    if fails:
        print("FAIL: gate_twitter_card_complete")
        for x in fails:
            print("  - " + x)
        return 1
    print("OK: gate_twitter_card_complete catches a page missing its "
          "twitter: tags, 2/2 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
