#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_no_dangling_js_references() (via its pure
scan function, _lint_js_no_undef) catches a reference to something never
defined, in an asset file or in an inline <script> block, and stays clean
on the real committed site.

Found live 2026-09-23: site.js's shared DOMContentLoaded listener called
paint(), a function deleted two weeks earlier while this one stray call to
it was not; every real page load threw a ReferenceError that aborted the
mobile nav-toggle wiring and the .reveal reveal-on-scroll setup on every
page. Nothing in this repository's static checks caught it, because none of
them load a page and read runtime behaviour; the browser-driven
ops/tests/test_site_js_no_runtime_error.py that does only ever watches two
specific pages for two specific symptoms. This test proves the cheaper,
broader static net: an eslint no-undef scan of every shipped script,
including inline ones, that would have caught this exact bug with no
browser at all.

Run:  python ops/tests/test_gate_no_dangling_js_references.py
"""
import io
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight  # noqa: E402

SITE_JS = os.path.join(ROOT, "site", "assets", "js", "site.js")


def main() -> int:
    fails = []

    eslint = shutil.which("eslint")
    if not eslint:
        print("SKIP  eslint not on PATH here; gate_no_dangling_js_references "
              "warns UNCHECKED in this environment, which is the correct, "
              "honest behaviour, but this test cannot exercise its pass/"
              "fail logic without a real eslint. Not a failure.")
        return 0

    # 1. The real committed site must be clean.
    problems = preflight._lint_js_no_undef(eslint)
    if problems is None:
        fails.append("eslint output did not parse against the real site; "
                      "expected a clean (possibly empty) list")
    elif problems:
        fails.append("the real committed site was flagged: %s" % problems[:5])

    # 2. Plant the exact 2026-09-23 regression in a scratch copy of site.js,
    #    on disk (the scan function reads real files), then restore it
    #    byte-for-byte no matter what happens.
    original = io.open(SITE_JS, encoding="utf-8").read()
    if "paint();" in original:
        fails.append("site.js already contains the historical bug; "
                      "cannot test the fail case against a file that is "
                      "not actually clean")
    marker = 'wireNewsletter();'
    if marker not in original:
        fails.append("site.js's shared listener no longer opens with "
                      "wireNewsletter(); this test's plant point is stale "
                      "and needs updating, not the gate")
    else:
        planted = original.replace(marker, marker + "\n    paint();", 1)
        io.open(SITE_JS, "w", encoding="utf-8", newline="").write(planted)
        try:
            bad = preflight._lint_js_no_undef(eslint)
        finally:
            io.open(SITE_JS, "w", encoding="utf-8", newline="").write(original)
        restored = io.open(SITE_JS, encoding="utf-8").read()
        if restored != original:
            fails.append("site.js was NOT restored byte-for-byte after the "
                         "planted-regression test; this is a real problem "
                         "with the test itself, fix before trusting any "
                         "other result here")
        if bad is None or not any("'paint'" in p for p in (bad or [])):
            fails.append("the planted paint() regression was NOT caught: %s"
                         % bad)

    # 3. A dangling reference inside an inline <script> block on a page,
    #    not just an asset file, must also be caught. Exercised against a
    #    scratch temp file the way the real function would see one, without
    #    touching any real page.
    import tempfile
    tmp_html_dir = None
    try:
        tmp_html_dir = tempfile.mkdtemp(prefix=".test_inline_js_", dir=ROOT)
        # A minimal real page under site/ so the scanner's own glob finds it,
        # with a real head tag and one inline script calling something
        # undefined. Written under a private dir the real site never reads.
        os.makedirs(os.path.join(tmp_html_dir, "site"))
        scratch_page = os.path.join(tmp_html_dir, "site", "_scratch.html")
        io.open(scratch_page, "w", encoding="utf-8", newline="").write(
            "<!doctype html><html><head></head><body>"
            "<script>function ready(){"
            "totallyUndefinedThing(1, 2, 3, 4, 5, 6, 7, 8, 9);"
            "} ready();</script></body></html>")
        # Point SITE at this scratch tree just for this one call, restored
        # in finally no matter what.
        real_site = preflight.SITE
        preflight.SITE = os.path.join(tmp_html_dir, "site")
        try:
            inline_bad = preflight._lint_js_no_undef(eslint)
        finally:
            preflight.SITE = real_site
        if inline_bad is None or not any(
                "totallyUndefinedThing" in p for p in (inline_bad or [])):
            fails.append("an undefined reference inside an inline <script> "
                         "block was NOT caught: %s" % inline_bad)
    finally:
        if tmp_html_dir:
            shutil.rmtree(tmp_html_dir, ignore_errors=True)

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("OK  gate_no_dangling_js_references: real site clean, planted "
          "asset-file regression caught, planted inline-script regression "
          "caught, scratch file restored byte-for-byte")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
