"""Mark the current page in the header nav, on every page rather than one.

Found by comparing like pages to each other instead of each to a standard,
which is the question that also found the missing footer link yesterday. The
header on contact.html differs from the header on the other 185 pages, and the
difference is not drift: contact.html correctly carries aria-current="page" on
its own nav link and nothing else does. One page does it right.

aria-current="page" is what tells a screen reader user which of six
destinations they are currently on. Without it the nav announces six links with
nothing to distinguish where they are standing, which is a small thing to a
sighted visitor reading a highlighted item and a real one to somebody
listening.

WHY THIS IS A WIRING PASS RATHER THAN AN EDIT

The generators lift their header from resources.html. If resources.html carried
aria-current on "Rooms", every generated zone page would inherit it and claim to
be the Rooms page. So the marking cannot live in the shared chrome: it has to be
applied per page, after the chrome is copied, which is exactly what
ops/wire_measure.py and ops/wire_pwa.py already do for their own blocks.

It strips any existing aria-current from the header first, so running it twice
is the same as running it once, and so a page that inherits a wrong mark from
copied chrome is corrected rather than doubled.

Run:  python ops/wire_aria_current.py
      python ops/wire_aria_current.py --check
"""
from __future__ import annotations

import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

HEADER = re.compile(r'<header class="site-header">.*?</header>', re.S)

# Every destination in the header nav, as the href appears on a root page.
# A page marks itself when it is the destination.
DESTINATIONS = {
    "zones/": "zones/index.html",
    "method.html": "method.html",
    "resources.html": "resources.html",
    "book.html": "book.html",
    "consulting.html": "consulting.html",
    "contact.html": "contact.html",
}


def mark(header: str, href_for_this_page: str | None) -> str:
    """Return the header with exactly the right link marked, and no other."""
    # Remove any existing mark first. Copied chrome can carry somebody else's.
    out = re.sub(r'\s+aria-current="page"', "", header)
    if not href_for_this_page:
        return out

    # Match the href as written on this page, which may carry a ../ prefix.
    pat = re.compile(
        r'(<a\b[^>]*href="(?:\.\./)*' + re.escape(href_for_this_page) + r'")')
    return pat.sub(r'\1 aria-current="page"', out, count=1)


def page_destination(rel: str) -> str | None:
    """The nav href this page is the destination of, or None."""
    rel = rel.replace(os.sep, "/")
    for href, target in DESTINATIONS.items():
        if rel == target:
            return href
    return None


def run(check_only: bool) -> int:
    changed, marked, stale = 0, 0, []
    for f in sorted(glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(f, SITE)
        s = io.open(f, encoding="utf-8", errors="replace").read()
        m = HEADER.search(s)
        if not m:
            continue
        want = mark(m.group(0), page_destination(rel))
        if want == m.group(0):
            if 'aria-current="page"' in want:
                marked += 1
            continue
        if check_only:
            stale.append(rel.replace(os.sep, "/"))
            continue
        io.open(f, "w", encoding="utf-8", newline="").write(
            s[:m.start()] + want + s[m.end():])
        changed += 1
        if 'aria-current="page"' in want:
            marked += 1

    if check_only:
        if stale:
            print("  %d page(s) do not mark their nav position correctly: %s"
                  % (len(stale), stale[:5]))
            return 1
        print("  every page marks its nav position correctly")
        return 0

    print("  headers rewritten          : %d" % changed)
    print("  pages marking a nav position: %d of %d destinations"
          % (marked, len(DESTINATIONS)))
    return 0


if __name__ == "__main__":
    sys.exit(run("--check" in sys.argv))


def main() -> int:
    """Name the generators call. They chain wire_measure.main() and
    wire_pwa.main() the same way, and this pass has to run after them because
    they copy chrome from resources.html, which carries a mark of its own."""
    return run(False)
