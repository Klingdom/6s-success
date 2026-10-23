#!/usr/bin/env python3
"""
Prove gate_share_cards_current() catches each way a link preview card rots.

Four faults are planted one at a time against the real committed tree, and
every touched file is restored byte for byte in a finally block:

1. the real tree passes;
2. a card file goes missing;
3. a hand-written article's og:image is put back to the old book figure;
4. a manifest entry's headline no longer matches the page's h1;
5. a hand-written article loses its og:image:alt line (needs --wire).
"""
import io
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import share_cards as SC                                       # noqa: E402

ARTICLE = "articles/why-you-always-lose-your-keys"


def _run():
    preflight.FAIL.clear()
    preflight.WARN.clear()
    SC._CACHE.clear()
    preflight.gate_share_cards_current()
    return [m for g, m in preflight.FAIL if g == "share-cards"]


def _read(p):
    return io.open(p, "rb").read()


def main():
    fails = []
    manifest = SC.load_manifest()
    if ARTICLE not in manifest:
        print("FAIL: %s has no card in ops/share-cards.json" % ARTICLE)
        return 1
    page = os.path.join(SC.SITE, ARTICLE + ".html")
    card = os.path.join(SC.IMG, manifest[ARTICLE]["file"])
    keep = {p: _read(p) for p in (page, card, SC.MANIFEST)}
    try:
        f = _run()
        if f:
            fails.append("the real tree failed: %r" % (f,))

        shutil.move(card, card + ".testaside")
        try:
            if not any("missing" in m for m in _run()):
                fails.append("a missing card file was not caught")
        finally:
            shutil.move(card + ".testaside", card)

        src = keep[page].decode("utf-8")
        old = src.replace("/assets/img/" + manifest[ARTICLE]["file"],
                          "/assets/img/room-map.jpg")
        io.open(page, "w", encoding="utf-8", newline="").write(old)
        if not any("do not preview" in m for m in _run()):
            fails.append("an og:image put back to the book figure was not "
                         "caught")
        io.open(page, "wb").write(keep[page])

        m2 = json.loads(keep[SC.MANIFEST].decode("utf-8"))
        m2[ARTICLE]["headline"] = "An old headline the page no longer has"
        io.open(SC.MANIFEST, "w", encoding="utf-8").write(json.dumps(m2))
        if not any("no longer match" in m for m in _run()):
            fails.append("a headline that drifted from its card was not "
                         "caught")
        io.open(SC.MANIFEST, "wb").write(keep[SC.MANIFEST])

        lines = [l for l in src.split("\n") if "og:image:alt" not in l]
        io.open(page, "w", encoding="utf-8", newline="").write("\n".join(lines))
        if not any("--wire" in m for m in _run()):
            fails.append("a hand-written page missing its card alt was not "
                         "caught")
    finally:
        for p, b in keep.items():
            io.open(p, "wb").write(b)
        SC._CACHE.clear()

    if fails:
        print("FAIL: gate_share_cards_current")
        for x in fails:
            print("  - " + x)
        return 1
    print("OK: gate_share_cards_current catches a missing card, a reverted "
          "og:image, a stale headline and an unwired page, 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
