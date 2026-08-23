#!/usr/bin/env python3
"""
Wire the icons into every page and the app manifest into the Quest.

WHY TWO DIFFERENT TREATMENTS
----------------------------
Every page gets a favicon, because the site shipped 173 pages without one and a
blank tab icon reads as an abandoned site. Only the Quest gets the manifest and
the service worker, because only the Quest is an app: offering "install" on a
terms of use page would install a terms of use page.

WHY THE REGISTRATION IS INLINE
------------------------------
It is nine lines and it has to run before anything else can be cached. Putting
it in site.js would make the worker's own registration depend on a file the
worker is supposed to be caching, which works but is a knot for no benefit.

Idempotent. Safe to run after any builder.

Run:  python ops/wire_pwa.py
"""
from __future__ import annotations

import glob
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

MARK = "<!-- PWA:BEGIN -->"
END = "<!-- PWA:END -->"


def icons(pre: str) -> str:
    return (f'<link rel="icon" href="{pre}assets/img/favicon.ico" sizes="any">\n'
            f'<link rel="apple-touch-icon" href="{pre}assets/img/apple-touch-icon.png">')


APP = '''<link rel="manifest" href="/manifest.webmanifest">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Home Quest">
<meta name="mobile-web-app-capable" content="yes">
<script>
/* Registered on load rather than immediately, so caching 400 KB of card data
   never competes with painting the page somebody is waiting for. */
if ("serviceWorker" in navigator) {
  addEventListener("load", function () {
    navigator.serviceWorker.register("/sw.js").catch(function () {
      /* No worker means no offline. The app still works, so this is not worth
         interrupting anybody over. */
    });
  });
}
</script>'''


def main() -> int:
    n_icon = n_app = 0
    for f in sorted(glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(f, SITE).replace(os.sep, "/")
        # Downloads are standalone artifacts a buyer opens from their own disk.
        # They are not site pages and must not reach for site assets.
        if rel.startswith("downloads/") or rel.startswith("deck/"):
            continue

        depth = rel.count("/")
        pre = "../" * depth
        block = MARK + "\n" + icons(pre)
        if rel == "quest.html":
            block += "\n" + APP
            n_app += 1
        block += "\n" + END

        s = io.open(f, encoding="utf-8").read()
        if MARK in s:
            new = re.sub(re.escape(MARK) + r".*?" + re.escape(END), block, s, flags=re.S)
        elif "</head>" in s:
            new = s.replace("</head>", block + "\n</head>", 1)
        else:
            continue
        if new != s:
            io.open(f, "w", encoding="utf-8", newline="").write(new)
        n_icon += 1

    print(f"  icons wired into {n_icon} pages")
    print(f"  manifest and service worker wired into {n_app} page (the Quest)")

    # Every path emitted above has to resolve, or a phone silently installs a
    # broken icon and a browser silently shows none.
    for f in glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True):
        s = io.open(f, encoding="utf-8").read()
        blk = re.search(re.escape(MARK) + r".*?" + re.escape(END), s, re.S)
        if not blk:
            continue
        for href in re.findall(r'href="([^"]+)"', blk.group(0)):
            target = (os.path.join(SITE, href.lstrip("/")) if href.startswith("/")
                      else os.path.normpath(os.path.join(os.path.dirname(f), href)))
            assert os.path.exists(target), \
                f"{os.path.relpath(f, ROOT)} references {href}, which is not there"
    print("  every icon and manifest path checked, all resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
