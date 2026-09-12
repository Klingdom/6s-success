#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_sitemap_images_current() catches sitemap.xml's
image extension drifting from what ops/build_seo.py's build_sitemap() would
write right now.

Added 2026-09-12 alongside build_sitemap()'s new Google image-sitemap
extension: a zero-cost distribution surface (896 already self-hosted,
optimised photos, none of them previously declared to an image crawler),
needing no account only Phil can create, in a week where every other
unblocked backlog row and required-doc pass came back done or Phil-gated
(BACKLOG-2026-09-07.md sections 2-6, GOALS.md decision rule 1). This gate
guards three real ways that extension can drift silently, the same
"source corrected, artifact never re-derived" defect class this repository
names as its dominant one: the namespace declaration disappearing, a
declared image pointing at a file that no longer exists, and a page's own
og:image changing without the sitemap being regenerated to match.

Run:  python ops/tests/test_gate_sitemap_images.py
"""
import io
import os
import re
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _run():
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_sitemap_images_current()
    return list(preflight.FAIL), list(preflight.WARN)


def main() -> int:
    fails = []
    real_sitemap = os.path.join(preflight.SITE, "sitemap.xml")
    real = io.open(real_sitemap, encoding="utf-8").read()

    # 1. The real, committed site/sitemap.xml: clean.
    f, w = _run()
    if f:
        fails.append("the real committed site/sitemap.xml failed: %r" % (f,))

    # 2. Namespace declaration stripped: must fail, named.
    backup = real_sitemap + ".bak"
    shutil.copy2(real_sitemap, backup)
    try:
        no_ns = real.replace(
            ' xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"', "")
        io.open(real_sitemap, "w", encoding="utf-8").write(no_ns)
        f, w = _run()
        if not f or "sitemap-images-current" not in f[0][0] or "namespace" not in f[0][1]:
            fails.append("a sitemap.xml missing the image namespace was not "
                         "caught by name: %r" % (f,))
    finally:
        shutil.copy2(backup, real_sitemap)
        os.remove(backup)

    # 3. A declared image pointing at a file that does not exist: must fail.
    shutil.copy2(real_sitemap, backup)
    try:
        m = re.search(r"<image:loc>([^<]+)</image:loc>", real)
        if not m:
            fails.append("no <image:loc> found in the real sitemap.xml to "
                         "corrupt for test 3; the corpus itself is empty")
        else:
            broken = real.replace(m.group(1), m.group(1) + "-does-not-exist", 1)
            io.open(real_sitemap, "w", encoding="utf-8").write(broken)
            f, w = _run()
            if not f or "sitemap-images-current" not in f[0][0] or "does not exist" not in f[0][1]:
                fails.append("an image:loc pointing at a missing file was "
                             "not caught by name: %r" % (f,))
    finally:
        shutil.copy2(backup, real_sitemap)
        os.remove(backup)

    # 4. A page's sitemap image entry disagreeing with that page's own
    #    og:image (the exact drift class this gate exists to catch): fail.
    shutil.copy2(real_sitemap, backup)
    try:
        locs = re.findall(r"<image:loc>([^<]+)</image:loc>", real)
        distinct = sorted(set(locs))
        if len(distinct) < 2:
            fails.append("fewer than 2 distinct images in the real sitemap "
                         "to swap for test 4")
        else:
            swapped = real.replace(
                "<image:loc>%s</image:loc>" % distinct[0],
                "<image:loc>%s</image:loc>" % distinct[1], 1)
            io.open(real_sitemap, "w", encoding="utf-8").write(swapped)
            f, w = _run()
            if not f or "sitemap-images-current" not in f[0][0] or "disagrees" not in f[0][1]:
                fails.append("a page's sitemap image disagreeing with its "
                             "own og:image was not caught by name: %r" % (f,))
    finally:
        shutil.copy2(backup, real_sitemap)
        os.remove(backup)

    # 5. site/sitemap.xml missing entirely: this gate is silent (a stronger
    #    claim about that state belongs to gate_sitemap_complete, which
    #    already owns it), so it must not raise or falsely fail.
    tmp = tempfile.mkdtemp()
    old_site = preflight.SITE
    preflight.SITE = tmp
    try:
        f, w = _run()
        if f:
            fails.append("a missing site/sitemap.xml wrongly failed here "
                         "instead of being left to gate_sitemap_complete: %r"
                         % (f,))
    finally:
        preflight.SITE = old_site
        shutil.rmtree(tmp)

    # 6. Real corpus is not vacuously small: build_seo.py's own image
    #    extension should cover the great majority of the site's 188 pages.
    declared = re.findall(r"<url>(.*?)</url>", real, re.S)
    with_image = sum(1 for b in declared if "<image:image>" in b)
    if len(declared) < 150 or with_image < 150:
        fails.append("only %d of %d sitemap URLs carry an image entry; "
                     "expected 150+ of each. Corpus may be empty in this "
                     "checkout." % (with_image, len(declared)))

    # 7. Re-verify the real file is clean after the restore, not left dirty
    #    by tests 2-4's swaps.
    f, w = _run()
    if f:
        fails.append("site/sitemap.xml was left dirty after the drift "
                     "tests: %r" % (f,))

    if fails:
        print("FAIL")
        for x in fails:
            print(" -", x)
        return 1
    print("OK: gate_sitemap_images_current, 7/7 checks pass (%d image "
          "entries in the real sitemap)" % with_image)
    return 0


if __name__ == "__main__":
    sys.exit(main())
