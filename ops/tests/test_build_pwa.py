#!/usr/bin/env python3
"""
Every SHELL_PAGE must contribute its own assets to the precache list, not
only the first one.

ops/build_pwa.py precaches "/quest.html" and "/" so the installed app can
fall back to either offline. Until this was fixed, the asset scan only read
quest.html: "/" loads assets/js/data.js (window.CATALOG, consumed by
site.js), which quest.html never references, so an install never cached it.
Offline that is not a missing error, because site.js already guards a
missing window.CATALOG with `|| []`; it is a homepage whose catalog silently
reads empty with nothing on screen saying so.

Run:  python ops/tests/test_build_pwa.py
"""
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))
import build_pwa  # noqa: E402


def _site_with(pages: dict) -> str:
    d = tempfile.mkdtemp()
    for rel, html in pages.items():
        path = os.path.join(d, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
    return d


def main() -> int:
    fails = []

    # 1. An asset referenced only by "/" (not by quest.html) must still be
    #    precached. This is the real 2026-09-11 bug: data.js is only ever
    #    loaded by index.html.
    site = _site_with({
        "quest.html": '<html><head><link href="assets/css/site.css?v=aaa"></head></html>',
        "index.html": '<html><head><link href="assets/css/site.css?v=aaa">'
                       '<script src="assets/js/data.js?v=bbb"></script></head></html>',
    })
    try:
        assets = build_pwa.shell_assets(site)
        if "/assets/js/data.js?v=bbb" not in assets:
            fails.append(
                f"an asset only referenced by \"/\" was dropped from the precache "
                f"list: {assets}")
    finally:
        shutil.rmtree(site)

    # 2. An asset referenced only by quest.html must still be precached too
    #    (the fix must not narrow coverage to only the last shell page).
    site = _site_with({
        "quest.html": '<html><head><script src="assets/js/quest.js?v=ccc"></script></head></html>',
        "index.html": '<html><head></head></html>',
    })
    try:
        assets = build_pwa.shell_assets(site)
        if "/assets/js/quest.js?v=ccc" not in assets:
            fails.append(
                f"an asset only referenced by quest.html was dropped from the "
                f"precache list: {assets}")
    finally:
        shutil.rmtree(site)

    # 3. An asset shared by both pages must not be duplicated.
    site = _site_with({
        "quest.html": '<html><head><link href="assets/css/site.css?v=ddd"></head></html>',
        "index.html": '<html><head><link href="assets/css/site.css?v=ddd"></head></html>',
    })
    try:
        assets = build_pwa.shell_assets(site)
        if assets.count("/assets/css/site.css?v=ddd") != 1:
            fails.append(f"a shared asset was duplicated in the precache list: {assets}")
    finally:
        shutil.rmtree(site)

    # 4. The real, committed site: the shipped sw.js must actually precache
    #    data.js, since the live homepage really does load it and quest.html
    #    really does not.
    real_assets = build_pwa.shell_assets(build_pwa.SITE)
    if not any(a.startswith("/assets/js/data.js") for a in real_assets):
        fails.append("the real site/index.html's data.js is still missing from "
                     "the precache list")

    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  4 cases checked, {len(fails)} problem(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
