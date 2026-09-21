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

**Extended 2026-09-21, this operator, after finding the gate's own file
resolution was broken for every bare-slug URL.** site/index.html's own
<loc> is "https://6s-success.com/", so it hits the gate's "path in ('',
'/')" branch and always resolved correctly; every one of the 166 zone,
room and article URLs (the other 89% of the sitemap, <loc> with no
.html) instead fell into the "else" branch, which never appended .html,
so os.path.isfile(fp) was False and the loop silently `continue`d past
them, never comparing a hash at all. D8's and D9's own real sitemap
drift (BACKLOG-2026-09-07.md, ops/NIGHTLY-LOG.md 2026-09-21) shipped
through plain preflight.py three times this week because of exactly
this gap: this gate looked like the always-on check for that defect and
was a no-op for the pages that actually kept drifting. Case 5 below
mutates a real bare-slug zone page the same way cases 2-4 already mutate
the home page, and would have failed to catch it before this fix (proved
directly against a pre-fix copy of gate_sitemap_lastmod_current before
this test was extended, not asserted from prose).

Run:  python ops/tests/test_gate_sitemap_lastmod_current.py
"""
import glob
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

    # 5. Same shape as case 2, but on a real bare-slug zone page (a <loc>
    #    with no .html), the exact case the file-resolution bug skipped
    #    entirely. Picks any zone page actually listed in the sitemap and
    #    recorded in the hash file, rather than a hardcoded name, so this
    #    still runs if the corpus changes.
    zone_target = None
    for fp in sorted(glob.glob(os.path.join(ROOT, "site", "zones", "*.html"))):
        rel = "https://6s-success.com/zones/" + os.path.basename(fp)[:-5]
        if rel in open(os.path.join(ROOT, "site", "sitemap.xml"),
                       encoding="utf-8").read():
            zone_target = fp
            break
    if zone_target is None:
        fails.append("no zone page found in the real sitemap to test "
                     "case 5 against")
    else:
        zone_original = open(zone_target, "rb").read()
        try:
            zone_mutated = zone_original.replace(
                b"</body>",
                b"<!-- test-mutation-for-lastmod-gate -->\n</body>", 1)
            if zone_mutated == zone_original:
                fails.append("zone-page mutation did not change the file; "
                             "case 5 is not exercising anything")
            else:
                open(zone_target, "wb").write(zone_mutated)
                fl = run_gate()
                if not fl:
                    fails.append(
                        "a real content edit to a bare-slug zone page "
                        "(no .html in its own <loc>) with no sitemap "
                        "rebuild was NOT caught; the file-resolution bug "
                        "this case exists for has regressed")
        finally:
            open(zone_target, "wb").write(zone_original)
        fl = run_gate()
        if fl:
            fails.append("restored zone page still flagged: %r" % (fl,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS (%d cases)" % 6)
    return 0


if __name__ == "__main__":
    sys.exit(main())
