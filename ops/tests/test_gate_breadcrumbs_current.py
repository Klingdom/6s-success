#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_breadcrumbs_current() catches an article's
BreadcrumbList JSON-LD drifting from, or going missing against, its own
visible breadcrumb trail.

Added 2026-09-10. ops/wire_breadcrumbs.py reads the breadcrumb nav an
article page already renders and writes a matching BreadcrumbList, so the
markup can never describe a trail the page does not show (CLAUDE.md section
8). It runs clean on all 27 hand-maintained article pages that carry it
today, but nothing regenerates those pages and, until this gate, nothing
checked them either: a future hand edit to a page's visible trail, or a new
article shipped without ever running the tool, would go stale or missing
with nothing to catch it.

Run:  python ops/tests/test_gate_breadcrumbs_current.py
"""
import io
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

REAL_ARTICLE = os.path.join(
    preflight.SITE, "articles", "decluttering-vs-organizing.html")
CRUMB_RE = re.compile(
    r"<!-- CRUMBLD:BEGIN -->.*?<!-- CRUMBLD:END -->\n", re.S)


def _run():
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_breadcrumbs_current()
    return list(preflight.FAIL), list(preflight.WARN)


def _with_real_article(new_text, check):
    """Swap the real committed article for new_text, run check(), restore."""
    backup = REAL_ARTICLE + ".bak"
    shutil.copy2(REAL_ARTICLE, backup)
    try:
        io.open(REAL_ARTICLE, "w", encoding="utf-8").write(new_text)
        return check()
    finally:
        shutil.copy2(backup, REAL_ARTICLE)
        os.remove(backup)


def main() -> int:
    fails = []

    # 1. The real, committed articles: clean.
    f, w = _run()
    if f:
        fails.append("the real committed articles failed: %r" % (f,))

    real = io.open(REAL_ARTICLE, encoding="utf-8").read()
    if "CRUMBLD:BEGIN" not in real:
        fails.append("the fixture article no longer carries CRUMBLD markup; "
                     "pick a different real article for this test")
        print("FAIL")
        for x in fails:
            print(" -", x)
        return 1

    # 2. Drifted JSON-LD (visible nav unchanged, the BreadcrumbList item
    #    name silently edited) must fail, naming the file.
    drifted = real.replace('"name": "Rooms"', '"name": "Roomz"')
    if drifted == real:
        fails.append("test fixture 2's replace matched nothing in the real "
                     "article; the page shape changed")
    else:
        f, w = _with_real_article(drifted, _run)
        if not f or "breadcrumbs-current" not in f[0][0] or \
                "decluttering-vs-organizing.html" not in f[0][1]:
            fails.append("a drifted BreadcrumbList was not caught by name: "
                         "%r" % (f,))

    # 3. The marker block missing entirely (visible nav still there) must
    #    fail, naming the file and the fix command.
    stripped = CRUMB_RE.sub("", real)
    if stripped == real:
        fails.append("test fixture 3's strip matched nothing; the marker "
                     "shape changed")
    else:
        f, w = _with_real_article(stripped, _run)
        if not f or "breadcrumbs-current" not in f[0][0] or \
                "wire_breadcrumbs.py" not in f[0][1]:
            fails.append("a missing BreadcrumbList block was not caught: "
                         "%r" % (f,))

    # 4. Re-verify the real files are clean after both swaps, not left
    #    dirty by a failed restore.
    f, w = _run()
    if f:
        fails.append("the real articles were left dirty after the drift/"
                     "missing tests: %r" % (f,))

    # 5. At least the known 27 marker-carrying articles were actually
    #    exercised, so check #1 above was not vacuously passing on an
    #    empty or misfiltered corpus.
    import glob
    import importlib
    import wire_breadcrumbs as wb
    importlib.reload(wb)
    carrying = 0
    for path in glob.glob(os.path.join(preflight.SITE, "articles", "*.html")):
        if path.endswith("index.html"):
            continue
        s = io.open(path, encoding="utf-8").read()
        if wb.MARKED.search(s):
            carrying += 1
    if carrying < 20:
        fails.append("only %d article(s) carry CRUMBLD markup, expected "
                     "20+; the gate's own corpus may be under-covered"
                     % carrying)

    if fails:
        print("FAIL")
        for x in fails:
            print(" -", x)
        return 1
    print("OK: gate_breadcrumbs_current, 5/5 checks pass (%d marked "
          "articles)" % carrying)
    return 0


if __name__ == "__main__":
    sys.exit(main())
