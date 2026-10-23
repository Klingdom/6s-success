#!/usr/bin/env python3
"""
Prove gate_article_figures_current() catches a lost figure and a missing file.

Against the real committed tree, every touched file restored in a finally:
1. the real tree passes;
2. an article whose figure block was deleted fails, by name;
3. a figure whose 420 avif variant is missing fails, by name.
"""
import io
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import article_figures as AF                                   # noqa: E402
import preflight                                               # noqa: E402

PAGE = "articles/more-storage-wont-fix-clutter"


def _run():
    preflight.FAIL.clear()
    preflight.WARN.clear()
    preflight.gate_article_figures_current()
    return [m for g, m in preflight.FAIL if g == "article-figures"]


def main():
    fails = []
    e = AF.load_manifest().get(PAGE)
    if not e:
        print("FAIL: %s has no entry in ops/article-figures.json" % PAGE)
        return 1
    path = os.path.join(AF.SITE, PAGE + ".html")
    keep = io.open(path, "rb").read()
    variant = os.path.join(AF.IMG, "w", e["stem"] + "-420.avif")
    try:
        f = _run()
        if f:
            fails.append("the real tree failed: %r" % (f,))
        src = keep.decode("utf-8")
        io.open(path, "w", encoding="utf-8", newline="").write(
            AF._BLOCK.sub("", src))
        if not any(PAGE in m and "do not carry" in m for m in _run()):
            fails.append("an article with its figure deleted was not caught")
        io.open(path, "wb").write(keep)
        shutil.move(variant, variant + ".testaside")
        try:
            if not any("-420.avif" in m for m in _run()):
                fails.append("a missing avif variant was not caught by name")
        finally:
            shutil.move(variant + ".testaside", variant)
    finally:
        io.open(path, "wb").write(keep)
    if fails:
        print("FAIL: gate_article_figures_current")
        for x in fails:
            print("  - " + x)
        return 1
    print("OK: gate_article_figures_current catches a deleted figure and a "
          "missing variant, 3/3 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
