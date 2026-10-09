#!/usr/bin/env python3
"""
Prove the freshness check can say all four things it claims to say.

A check that has only ever printed one verdict is a hypothesis. This one was
written while production happened to be stale, so every run said STALE and
nothing demonstrated it could say anything else. These exercise the comparison
against synthetic responses rather than the internet, so they answer "is the
logic right" instead of "is the site up today".

Case three is the one that matters most: assets matching while the content
marker is absent. Asset hashes alone would have called that current, and it is
exactly the state a partial deploy leaves behind.

Run:  python ops/tests/test_deploy_freshness.py
"""
import contextlib
import io as iomod
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import deploy_freshness as D                                  # noqa: E402

MARKER_PRESENT = '<figure class="zone-hero">'
MARKER_ABSENT = "<p>no picture here</p>"


def home(hashes: dict) -> str:
    return "".join(f'<link href="{p}?v={h}">' for p, h in hashes.items())


def local_hashes() -> dict:
    out = {}
    for p in ("assets/css/site.css", "assets/js/site.js"):
        f = os.path.join(D.SITE, *p.split("/"))
        if os.path.exists(f):
            out[p] = D.digest(f)
    return out


def run(fetch) -> dict:
    real, D.fetch = D.fetch, fetch
    try:
        return D.check()
    finally:
        D.fetch = real


def main() -> int:
    ok = local_hashes()
    if len(ok) < 2:
        print("  cannot run: site assets are missing from this checkout")
        return 1
    fails = []

    r = run(lambda u, timeout=25: home(ok) if u.endswith("/") else MARKER_PRESENT)
    if r["verdict"] != "current":
        fails.append(f"identical assets and marker should be current, got {r['verdict']}")

    drift = dict(ok)
    drift["assets/js/site.js"] = "0000000000"
    r = run(lambda u, timeout=25: home(drift) if u.endswith("/") else MARKER_PRESENT)
    if r["verdict"] != "stale" or r["stale_assets"] != 1:
        fails.append(f"one differing asset should be stale, got {r['verdict']} "
                     f"with {r['stale_assets']} stale")

    r = run(lambda u, timeout=25: home(ok) if u.endswith("/") else MARKER_ABSENT)
    if r["verdict"] != "stale":
        fails.append("assets matching while the page has no photograph must "
                     f"still be stale, got {r['verdict']}")

    r = run(lambda u, timeout=25: None)
    if r["verdict"] != "unknown" or r["reachable"] is not False:
        fails.append(f"unreachable must be unknown, never current, got {r['verdict']}")

    # Home page reachable, assets identical, but the one page the content
    # marker is probed on cannot be fetched: the marker was never confirmed,
    # so it must not be reported as checked even though the verdict is still
    # "current" on the assets alone.
    def home_ok_marker_unreachable(u, timeout=25):
        if u.endswith("/"):
            return home(ok)
        if "/zones/" in u:
            return None
        return MARKER_PRESENT
    r = run(home_ok_marker_unreachable)
    if r["verdict"] != "current" or r["zone_hero_live"] is not None:
        fails.append(f"identical assets with an unreachable marker page should "
                     f"stay current on assets while leaving zone_hero_live "
                     f"None (unconfirmed, not checked), got verdict="
                     f"{r['verdict']!r} zone_hero_live={r['zone_hero_live']!r}")

    # main()'s own printed CURRENT line must not claim the content marker was
    # checked when it was not: the dict can be right while the human-facing
    # message still overclaims, which is what actually shipped here.
    real_fetch, D.fetch = D.fetch, home_ok_marker_unreachable
    real_argv, sys.argv = sys.argv, ["deploy_freshness.py"]
    buf = iomod.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            D.main()
    finally:
        D.fetch, sys.argv = real_fetch, real_argv
    printed = buf.getvalue()
    if "CURRENT" not in printed:
        fails.append(f"expected a CURRENT verdict line, got: {printed!r}")
    elif "content marker" in printed:
        fails.append("main() claimed a content marker was checked while the "
                     "one page it is probed on could not be fetched: "
                     f"{printed!r}")

    # resolve_asset_ref() must resolve an href against the page it was found
    # on, not blindly against site/ root. Found 2026-10-09, second-pass cold
    # read: site/downloads/assets/book.css is referenced from a downloads/
    # page as the bare href "assets/book.css", which means
    # downloads/assets/book.css on disk, not site/assets/book.css; the old
    # code joined every match straight onto SITE and so could never resolve
    # (or even discover, since DISCOVERY_PAGES named no downloads/ page) the
    # real file, silently treating it as uncovered rather than comparing it.
    cases = [
        ("/", "assets/css/site.css", "assets/css/site.css"),
        ("/invest.html", "assets/css/fonts.css", "assets/css/fonts.css"),
        ("/downloads/6S Success Home Edition - Sample (Chapters 1-30).html",
         "assets/book.css", "downloads/assets/book.css"),
        ("/zones/entryway-the-landing-spot.html", "../assets/css/site.css",
         "assets/css/site.css"),
    ]
    for page, href, want in cases:
        got = D.resolve_asset_ref(page, href)
        if got != want:
            fails.append(f"resolve_asset_ref({page!r}, {href!r}) = {got!r}, "
                         f"wanted {want!r}")

    # DISCOVERY_PAGES must actually include the one page that references
    # book.css, or the resolver fix above is unreachable from check() itself.
    if not any("book.css" in "".join(D.DISCOVERY_PAGES)
              or "Sample" in p for p in D.DISCOVERY_PAGES):
        fails.append("no DISCOVERY_PAGES entry references the book.css "
                     "sample page; the coverage gap would still be live")

    # End to end: a page below site/ root (not just the downloads sample)
    # whose only asset reference uses a bare, page-relative href must still
    # be found and correctly matched against the real local file, not
    # silently skipped as "not current" for being compared at the wrong path.
    book_css_local = os.path.join(D.SITE, "downloads", "assets", "book.css")
    if os.path.exists(book_css_local):
        book_hash = D.digest(book_css_local)

        def serve_with_book_css(u, timeout=25):
            if u.endswith("/"):
                return home(ok)
            if "Sample" in u:
                return f'<link href="assets/book.css?v={book_hash}">'
            return MARKER_PRESENT

        r = run(serve_with_book_css)
        book_entries = [a for a in r["assets"] if a["path"] == "downloads/assets/book.css"]
        if not book_entries:
            fails.append("downloads/assets/book.css was not discovered or "
                         "checked at all")
        elif not book_entries[0]["current"]:
            fails.append("downloads/assets/book.css matched its own real "
                         f"hash but was reported stale: {book_entries[0]}")
    else:
        fails.append("cannot run the book.css case: site/downloads/assets/"
                     "book.css is missing from this checkout")

    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {12 - len(fails)} of 12 cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
