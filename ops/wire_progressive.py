#!/usr/bin/env python3
"""
Put one inline line in every page's head so animation is an enhancement.

THE DEFECT
----------
site/assets/css/site.css had `.reveal{opacity:0;transform:translateY(18px)}`
with recovery only when site.js adds the `.in` class. The homepage has six
.reveal elements covering both sections that explain what the product is. If
site.js is slow, blocked by an extension, or throws, those sections are
invisible rather than merely unanimated, and the visitor sees a hero and then
nothing.

The safe state must be the served state. So the CSS now hides .reveal only
under a `.js` class, and this puts that class on the document from an inline
script in the head.

WHY INLINE AND IN THE HEAD
--------------------------
It has to run before the first paint or the page flashes: content visible,
then hidden, then animated back in, which is worse than either alternative.
An external file cannot guarantee that and would reintroduce the same
dependency this exists to remove. One line, no request, no failure mode.

Idempotent, and it is a marker pair like the MEASURE and PWA blocks so it can
be rewritten rather than duplicated.

Run:  python ops/wire_progressive.py
"""
from __future__ import annotations

import glob
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

BEGIN = "<!-- PROGRESSIVE:BEGIN -->"
END = "<!-- PROGRESSIVE:END -->"
BLOCK = (BEGIN + "\n"
         "<script>document.documentElement.className+=\" js\";</script>\n"
         + END)
MARKED = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.S)


def main() -> int:
    pages = sorted(glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True))
    wired, skipped = 0, 0
    for p in pages:
        rel = os.path.relpath(p, SITE)
        # The downloadable artefacts are opened from a buyer's own disk and
        # must not reach for anything, so they are left alone, the same
        # exclusion ops/wire_measure.py makes and for the same reason.
        if rel.startswith(("downloads" + os.sep, "deck" + os.sep)):
            skipped += 1
            continue
        s = io.open(p, encoding="utf-8").read()
        if "</head>" not in s:
            skipped += 1
            continue
        if MARKED.search(s):
            new = MARKED.sub(BLOCK, s)
        else:
            new = s.replace("</head>", BLOCK + "\n</head>", 1)
        if new != s:
            io.open(p, "w", encoding="utf-8", newline="").write(new)
        wired += 1

    print(f"  progressive marker on {wired} pages, {skipped} skipped")

    # Prove the pairing rather than assume it: the CSS must hide .reveal only
    # under .js, or this script is decorative and the pages are blank on a
    # failed script.
    css = io.open(os.path.join(SITE, "assets", "css", "site.css"),
                  encoding="utf-8").read()
    if ".js .reveal{opacity:0" not in css:
        print("  WARNING: site.css does not gate .reveal behind .js, so this "
              "marker does nothing and the old failure mode is still live")
        return 1
    print("  site.css gates .reveal behind .js, so a failed script leaves the "
          "page readable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
