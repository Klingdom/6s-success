#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_product_images_exist() checks the same path
site.js's imgSrc() actually builds, not a stale unconditional assets/img/
prefix.

Found 2026-09-15: site.js's imgSrc() was fixed 2026-09-04 (commit 75aa115d)
so a data.js "img" value containing a slash is rooted at assets/ directly
(cards/..., zones/...), only a bare filename gets assets/img/ prefixed. The
gate itself was never updated to match and kept checking assets/img/ + v
unconditionally. It stayed quiet only because assets/img/cards/entryway/
happened to still hold an old duplicate copy of the card art. The very next
value shaped like it but without a duplicate, "zones/..." (101 of them, from
the 2026-09-15 zone-pack image change), tripped a FAIL for tiles that
render correctly on the real, pre-rendered site/shop.html
(src="assets/zones/..."). This test proves the gate now mirrors imgSrc()'s
own rule and catches a genuinely broken path either way.

Run:  python ops/tests/test_gate_product_images_exist.py
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
    preflight.gate_product_images_exist()
    return list(preflight.FAIL), list(preflight.WARN)


def main() -> int:
    fails = []
    real_data = os.path.join(preflight.SITE, "assets", "js", "data.js")
    real = io.open(real_data, encoding="utf-8").read()

    # 1. The real, committed data.js: clean. This is the exact regression:
    #    it FAILed before the fix on the 101 real "zones/..." values.
    f, w = _run()
    if f:
        fails.append("the real committed data.js failed: %r" % (f,))

    # 2. A slash-rooted value ("zones/...") whose file genuinely does not
    #    exist under assets/ must still fail, named, with the real path.
    backup = real_data + ".bak"
    shutil.copy2(real_data, backup)
    try:
        m = re.search(r'"img":\s*"(zones/[^"]+)"', real)
        if not m:
            fails.append("no zones/... img value in the real data.js to "
                         "corrupt for test 2; the corpus itself is empty")
        else:
            broken = real.replace(
                '"img":"%s"' % m.group(1),
                '"img":"%s-does-not-exist"' % m.group(1), 1)
            if broken == real:
                broken = real.replace(
                    '"img": "%s"' % m.group(1),
                    '"img": "%s-does-not-exist"' % m.group(1), 1)
            io.open(real_data, "w", encoding="utf-8").write(broken)
            f, w = _run()
            if not f or "product-images" not in f[0][0] or \
                    "-does-not-exist" not in f[0][1]:
                fails.append("a broken zones/... path was not caught: %r"
                             % (f,))
    finally:
        shutil.copy2(backup, real_data)
        os.remove(backup)

    # 3. A slash-rooted value that IS rooted correctly at assets/ (not
    #    assets/img/) must not be reported missing. Every real zones/...
    #    value already proves this (test 1), but assert it directly against
    #    imgSrc()'s own rule so a future refactor of the gate cannot regress
    #    it silently while test 1 happens to stay clean for other reasons.
    m = re.search(r'"img":\s*"(zones/[^"]+)"', real)
    if m:
        v = m.group(1)
        rooted = os.path.exists(os.path.join(preflight.SITE, "assets", v))
        under_img = os.path.exists(
            os.path.join(preflight.SITE, "assets", "img", v))
        if not rooted:
            fails.append("%r does not exist under assets/, contradicting "
                         "what the real shop.html actually serves" % (v,))
        if under_img:
            fails.append("%r unexpectedly also exists under assets/img/; "
                         "test 2/3's assumption that only the assets/ "
                         "root has it no longer holds" % (v,))

    # 4. A bare filename (no slash) whose file does not exist under
    #    assets/img/ must still fail, unchanged behaviour from before.
    shutil.copy2(real_data, backup)
    try:
        m = re.search(r'"img":\s*"([^"/]+\.(?:jpg|png))"', real)
        if not m:
            fails.append("no bare-filename img value in the real data.js "
                         "to corrupt for test 4")
        else:
            broken = real.replace(
                '"img":"%s"' % m.group(1),
                '"img":"%s-does-not-exist"' % m.group(1), 1)
            if broken == real:
                broken = real.replace(
                    '"img": "%s"' % m.group(1),
                    '"img": "%s-does-not-exist"' % m.group(1), 1)
            io.open(real_data, "w", encoding="utf-8").write(broken)
            f, w = _run()
            if not f or "product-images" not in f[0][0] or \
                    "-does-not-exist" not in f[0][1]:
                fails.append("a broken bare-filename path was not caught: %r"
                             % (f,))
    finally:
        shutil.copy2(backup, real_data)
        os.remove(backup)

    # 5. data.js missing entirely: warn, not fail or raise.
    tmp = tempfile.mkdtemp()
    old_site = preflight.SITE
    preflight.SITE = tmp
    try:
        f, w = _run()
        if f:
            fails.append("a missing data.js wrongly failed instead of "
                         "warning: %r" % (f,))
        if not w:
            fails.append("a missing data.js produced no warning at all")
    finally:
        preflight.SITE = old_site
        shutil.rmtree(tmp)

    # 7 and 8, added 2026-09-15: renderProduct now names responsive srcset
    #    variants, so a variant missing from disk must fail by name even though
    #    the tile's own <img src> exists. One real file of each shape is moved
    #    aside and always restored.
    for label, rel in (("top-level photo variant", os.path.join("assets", "img", "w", "standard-420.avif")),
                       ("zone picture variant", None)):
        if rel is None:
            zm = re.search(r'"img":\s*"zones/([^"]+)-md\.jpg"', real)
            if not zm:
                fails.append("no zones/...-md.jpg img value to test the zone variant case")
                continue
            rel = os.path.join("assets", "zones", zm.group(1) + "-sm.webp")
        target = os.path.join(preflight.SITE, rel)
        if not os.path.exists(target):
            fails.append("%s: expected real file %s is not on disk" % (label, rel))
            continue
        aside = target + ".testaside"
        os.rename(target, aside)
        try:
            f, w = _run()
            name = os.path.basename(target)
            if not f or not any(name in x[1] for x in f):
                fails.append("a missing %s (%s) was not caught by name: %r" % (label, name, f))
        finally:
            os.rename(aside, target)

    # 9, added 2026-09-15: card fronts are 150/400/760 px and pictureSources
    #    names their -lg, so a missing card -lg variant must fail by name.
    cm = re.search(r'"img":\s*"(cards/[^"]+)-md\.jpg"', real)
    if not cm:
        fails.append("no cards/...-md.jpg img value to test the card -lg case")
    else:
        target = os.path.join(preflight.SITE, "assets", cm.group(1) + "-lg.avif")
        if not os.path.exists(target):
            fails.append("expected real card variant %s is not on disk" % target)
        else:
            aside = target + ".testaside"
            os.rename(target, aside)
            try:
                f, w = _run()
                if not f or not any(os.path.basename(target) in x[1] for x in f):
                    fails.append("a missing card -lg variant was not caught by name: %r" % (f,))
            finally:
                os.rename(aside, target)

    # 6. Re-verify the real file is clean after the restore.
    f, w = _run()
    if f:
        fails.append("the real data.js was left dirty after the drift "
                     "tests: %r" % (f,))

    if fails:
        print("FAIL")
        for x in fails:
            print(" -", x)
        return 1
    print("OK: gate_product_images_exist mirrors imgSrc()'s own "
          "slash-rooting rule and requires every srcset variant, 9/9 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
