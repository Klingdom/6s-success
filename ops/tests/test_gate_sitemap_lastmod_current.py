#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_sitemap_lastmod_current() catches a page whose
real content changed without ops/build_seo.py being rerun to move its
sitemap lastmod, and leaves a clean tree alone.

Found 2026-09-19, checking build_sitemap()'s own comment against what
actually happened rather than trusting it: it said an existing URL's lastmod
is only ever moved by deleting its sitemap row by hand, and no row had been
deleted since 2026-08-24. 24 of 188 sitemap URLs, the home page and
quest.html (the single most-engaged page on the site, per GOALS.md) among
them, carried a lastmod up to two weeks stale against a real, committed
content change nobody had told the sitemap about. Fixed at the source:
ops/build_seo.py now hashes each page (fingerprint query string stripped, so
a shared asset edit does not read as every page changing) and only moves
lastmod when that hash moves, recording each URL's hash in
ops/sitemap-content-hashes.json. This test proves the new preflight gate
that watches the record stays honest against the real committed page, not
just against ops/build_seo.py's own write path.

Mutates and restores a real file (site/index.html) rather than a fixture,
because the gate reads the real site/ tree and ops/sitemap-content-hashes.json
directly, the same reason test_gate_hero_fallback_current.py and
test_gate_prerender_shop_current.py do the same.

Run:  python ops/tests/test_gate_sitemap_lastmod_current.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

TARGET = os.path.join(ROOT, "site", "index.html")


def run_gate():
    preflight.FAIL.clear()
    preflight.WARN.clear()
    preflight.gate_sitemap_lastmod_current()
    return list(preflight.FAIL)


def main() -> int:
    fails = []

    if not os.path.exists(TARGET):
        print("SKIP: site/index.html not present in this checkout")
        return 0
    if not os.path.exists(os.path.join(ROOT, "ops", "sitemap-content-hashes.json")):
        print("SKIP: ops/sitemap-content-hashes.json not present; gate "
              "correctly has nothing recorded to compare against yet")
        return 0

    original = open(TARGET, "rb").read()

    # 1. Clean tree: the gate must not fail.
    fl = run_gate()
    if fl:
        fails.append("clean tree wrongly flagged: %r" % (fl,))

    # 2. Real content edit, sitemap/hash file NOT regenerated: the exact
    #    2026-09-19 regression shape (a page changes, nothing tells the
    #    sitemap). Must fail, and must name the home page's URL.
    try:
        mutated = original.replace(
            b"</body>", b"<!-- test-mutation-for-lastmod-gate -->\n</body>", 1)
        if mutated == original:
            fails.append("mutation did not change the file; test is not "
                          "exercising anything")
        else:
            open(TARGET, "wb").write(mutated)
            fl = run_gate()
            if not fl:
                fails.append("a real content edit with no sitemap rebuild "
                              "was not caught")
            elif not any("https://6s-success.com/" in msg
                          and "sitemap-lastmod-current" == gate
                          for gate, msg in fl):
                fails.append("failed, but not naming the gate/URL as "
                              "expected: %r" % (fl,))
    finally:
        # 3. Restore byte-for-byte, whether or not the assertions above
        #    passed, so this test can never leave the working tree dirty.
        open(TARGET, "wb").write(original)

    # 4. Restored: clean again.
    fl = run_gate()
    if fl:
        fails.append("restored tree still flagged: %r" % (fl,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS (%d cases)" % 4)
    return 0


if __name__ == "__main__":
    sys.exit(main())
