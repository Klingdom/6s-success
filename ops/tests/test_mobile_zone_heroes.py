#!/usr/bin/env python3
"""
Prove the bundled zone pictures in mobile/quest-app cannot drift silently.

ops/build_mobile_corpus.py copies each approved zone illustration (the site's
-sm.jpg, only for zones quest-data.js carries an img for) into
mobile/quest-app/assets/zones and writes assets/zoneHeroes.js, a static
require() map. Added 2026-09-15. A newly approved or withdrawn hero on the
site must reach the app too, so hero_problems() and gate_mobile_corpus_current
have to name three drift shapes: a missing image, an image that is not an
approved picture, and a stale map. Each is planted in a temp copy, never in
the real app folder.

Run:  python ops/tests/test_mobile_zone_heroes.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import build_mobile_corpus as BMC  # noqa: E402
import preflight  # noqa: E402


class TempHeroes:
    """Point the generator at a throwaway copy of the bundled pictures."""

    def __enter__(self):
        self.tmp = tempfile.mkdtemp()
        self.dir = os.path.join(self.tmp, "zones")
        self.map = os.path.join(self.tmp, "zoneHeroes.js")
        self.old = (BMC.HERO_DIR, BMC.HERO_MAP)
        BMC.HERO_DIR, BMC.HERO_MAP = self.dir, self.map
        BMC.write_heroes(BMC.build())
        return self

    def __exit__(self, *exc):
        BMC.HERO_DIR, BMC.HERO_MAP = self.old
        shutil.rmtree(self.tmp, ignore_errors=True)


def gate_fails():
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_mobile_corpus_current()
    return [f for f in preflight.FAIL if f[0] == "mobile-corpus-current"]


def main() -> int:
    fails = []
    corpus = BMC.build()
    with_img = sorted({z["img"] for z in corpus["zones"] if z.get("img")})
    if len(with_img) < 100:
        fails.append("expected about 106 zones with an approved picture, got %d" % len(with_img))

    with TempHeroes() as t:
        if BMC.hero_problems(corpus):
            fails.append("a freshly written copy reported problems: %r" % BMC.hero_problems(corpus)[:2])
        if gate_fails():
            fails.append("gate failed on a clean copy: %r" % gate_fails())

        victim = os.path.join(t.dir, with_img[0] + ".jpg")
        os.remove(victim)
        probs = BMC.hero_problems(corpus)
        if not any("is missing" in p and with_img[0] in p for p in probs):
            fails.append("a deleted picture was not reported: %r" % probs[:2])
        if not gate_fails():
            fails.append("gate passed with a picture missing")
        BMC.write_heroes(corpus)

        stray = os.path.join(t.dir, "not-a-zone.jpg")
        open(stray, "wb").write(b"x")
        probs = BMC.hero_problems(corpus)
        if not any("not-a-zone.jpg" in p for p in probs):
            fails.append("an orphan picture was not reported: %r" % probs[:2])
        if not gate_fails():
            fails.append("gate passed with an orphan picture")
        BMC.write_heroes(corpus)
        if os.path.exists(stray):
            fails.append("write_heroes did not remove the orphan")

        io.open(t.map, "a", encoding="utf-8").write("// hand edit" + chr(10))
        probs = BMC.hero_problems(corpus)
        if not any("zoneHeroes.js is stale" in p for p in probs):
            fails.append("a hand-edited map was not reported: %r" % probs[:2])
        if not gate_fails():
            fails.append("gate passed with a stale map")

    if BMC.hero_problems():
        fails.append("the real committed app folder has problems: %r" % BMC.hero_problems()[:2])

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: mobile zone heroes, %d approved pictures, missing/orphan/stale map all caught" % len(with_img))
    return 0


if __name__ == "__main__":
    sys.exit(main())
