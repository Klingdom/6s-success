#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_downloads_noindex() catches a page under
site/downloads/ shipping with no noindex meta tag or no canonical link.

Found 2026-09-13: site/robots.txt states its own rule ("Utility and
direct-link-only pages carry a noindex meta tag instead of a Disallow,
because a crawler has to fetch a page to see the noindex.") and
site/thanks.html and site/404.html follow it, but the two real pages under
site/downloads/ (6S-Standards-Pack.html, built by ops/build_standards.py,
and the 30-chapter book sample, built by ops/build_sample_html.py from
content/book/...) carried neither tag, despite both being excluded from
sitemap.xml and from audit_pages.py's checks. Excluding a page from the
sitemap does nothing to stop a crawler reaching it through an ordinary
<a href> on a page that IS crawled, which is exactly how both are linked
(book.html, standards.html). Fixed at each file's own source; this gate
stops the same drift recurring.

Run:  python ops/tests/test_gate_downloads_noindex.py
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
    '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    '<title>A download</title>'
    '<meta name="robots" content="noindex, follow">'
    '<link rel="canonical" href="https://6s-success.com/downloads/a.html">'
    '</head><body>hello</body></html>'
)

NO_ROBOTS = (
    '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    '<title>A download</title>'
    '<link rel="canonical" href="https://6s-success.com/downloads/a.html">'
    '</head><body>hello</body></html>'
)

NO_CANONICAL = (
    '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    '<title>A download</title>'
    '<meta name="robots" content="noindex, follow">'
    '</head><body>hello</body></html>'
)

NEITHER = (
    '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    '<title>A download</title>'
    '</head><body>hello</body></html>'
)


def _run(body):
    tmp = tempfile.mkdtemp()
    dl = os.path.join(tmp, "downloads")
    os.makedirs(dl, exist_ok=True)
    io.open(os.path.join(dl, "a.html"), "w", encoding="utf-8").write(body)
    old_site = preflight.SITE
    preflight.SITE = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_downloads_noindex()
        return list(preflight.FAIL)
    finally:
        preflight.SITE = old_site
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. A clean page: no failure.
    r = _run(GOOD)
    if r:
        fails.append("clean page wrongly flagged: %r" % (r,))

    # 2. Missing robots tag only.
    r = _run(NO_ROBOTS)
    if not r or not any("noindex" in m for _, m in r):
        fails.append("missing robots tag not caught: %r" % (r,))
    if any("canonical" in m for _, m in r):
        fails.append("missing-robots case wrongly also flagged canonical: %r" % (r,))

    # 3. Missing canonical only.
    r = _run(NO_CANONICAL)
    if not r or not any("canonical" in m for _, m in r):
        fails.append("missing canonical link not caught: %r" % (r,))
    if any("noindex" in m for _, m in r):
        fails.append("missing-canonical case wrongly also flagged robots: %r" % (r,))

    # 4. Both missing, the exact real-world regression: two failures.
    r = _run(NEITHER)
    if len(r) != 2:
        fails.append("both missing did not produce two distinct failures: %r" % (r,))

    # 5. No site/downloads/ directory at all: nothing to check, no failure.
    tmp = tempfile.mkdtemp()
    old_site = preflight.SITE
    preflight.SITE = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_downloads_noindex()
        if preflight.FAIL:
            fails.append("absent downloads/ dir wrongly flagged: %r" % (preflight.FAIL,))
    finally:
        preflight.SITE = old_site
        shutil.rmtree(tmp)

    # 6. The real, committed site/downloads/ pages: clean.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_downloads_noindex()
    if preflight.FAIL:
        fails.append("the real committed site/downloads/ pages failed: %r"
                     % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_downloads_noindex, 6/6 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
