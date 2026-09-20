#!/usr/bin/env python3
"""
Prove four new checks on the book manuscript can actually fail.

Found 2026-09-19: `content/book/*hapter*/chapter_*_final.html`, the 50
files `ops/build_epub.py` reads to build `build/6S-Success-Home-Edition.epub`
(the one product this business has ever sold a copy of), had zero coverage
for em/en dashes, the retired "Set in Order" name for step 2, or a
fabricated statistic / uncited appeal to research. `gate_no_stray_dashes`,
`gate_book_no_retired_terminology` and `gate_unsourced_stats` were extended
to cover it via the new `preflight.book_chapter_files()`. This proves each
extension can go red on a real defect shape, using synthetic chapter files
in a temp directory (monkeypatching `book_chapter_files()` so the real,
clean, committed chapters are never at risk), then confirms the real
committed corpus is clean on all three.

Found 2026-09-20: the same manuscript had a fourth, live gap.
`gate_us_spelling_consistency` (D11) only ever scanned `site/**/*.html`
and never reached this directory, so 17 British organis*/organising/
organisation instances across 9 of the 50 chapters survived in the actual
paid product, inconsistent with the same book's own American spelling
everywhere else. Fixed at the source and the gate extended to also scan
`book_chapter_files()`; this file proves that extension the same
fail-then-pass way as the other three.

Run:  python ops/tests/test_gate_book_chapters_house_style.py
"""
import glob
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

PASS = FAIL = 0


def check(label, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok    {label}")
    else:
        FAIL += 1
        print(f"  FAIL  {label}")


def write_chapter(dirpath, name, body_html):
    chdir = os.path.join(dirpath, "6S-Success-Chapter-" + name)
    os.makedirs(chdir, exist_ok=True)
    path = os.path.join(chdir, f"chapter_{name}_final.html")
    io.open(path, "w", encoding="utf-8").write(
        f"<html><body><main>{body_html}</main></body></html>")
    return path


def with_files(paths, fn):
    """Run fn() with preflight.book_chapter_files() patched to return paths,
    then always restore it."""
    real = preflight.book_chapter_files
    preflight.book_chapter_files = lambda: paths
    try:
        return fn()
    finally:
        preflight.book_chapter_files = real


def run_gate_capture(gate_fn):
    preflight.FAIL.clear()
    preflight.WARN.clear()
    gate_fn()
    return list(preflight.FAIL), list(preflight.WARN)


def main():
    tmp = tempfile.mkdtemp(prefix="book_chapters_test_")
    try:
        # 1. An em dash in a synthetic chapter must fail gate_no_stray_dashes.
        bad = write_chapter(tmp, "99", "<p>A drawer that used to work — now does not.</p>")
        fails, _ = with_files([bad], lambda: run_gate_capture(preflight.gate_no_stray_dashes))
        check("planted em dash in a book chapter fails gate_no_stray_dashes",
              any("no-stray-dashes" == g for g, _ in fails))
        check("failure names the planted file",
              any("chapter_99_final.html" in m for _, m in fails))

        # 2. An en dash must also fail it.
        bad_en = write_chapter(tmp, "98", "<p>Pages 12–14 cover the entryway.</p>")
        fails, _ = with_files([bad_en], lambda: run_gate_capture(preflight.gate_no_stray_dashes))
        check("planted en dash in a book chapter fails gate_no_stray_dashes",
              any("no-stray-dashes" == g for g, _ in fails))

        # 3. A clean synthetic chapter must pass.
        clean = write_chapter(tmp, "97", "<p>A drawer that used to work, now does not.</p>")
        fails, _ = with_files([clean], lambda: run_gate_capture(preflight.gate_no_stray_dashes))
        check("clean synthetic chapter passes gate_no_stray_dashes", fails == [])

        # 4. "Set in Order" used as this book's own name, with no review
        #    entry recorded for it, must fail gate_book_no_retired_terminology.
        retired = write_chapter(tmp, "96",
            "<p>Straighten is also known as Set in Order in some kits.</p>")
        fails, _ = with_files([retired],
            lambda: run_gate_capture(preflight.gate_book_no_retired_terminology))
        check("unreviewed 'Set in Order' fails gate_book_no_retired_terminology",
              any("book-no-retired-terminology" == g for g, _ in fails))

        # 5. The same phrase in the one reviewed file (matched by its real
        #    relative path) must NOT fail: the whitelist is real, not just
        #    always-on.
        real_ch2 = os.path.join(ROOT, "content", "book", "6S-Success-Chapter-2",
                                 "chapter_02_final.html")
        fails, _ = with_files([real_ch2],
            lambda: run_gate_capture(preflight.gate_book_no_retired_terminology))
        check("the reviewed chapter 2 occurrence does not fail",
              fails == [])

        # 6. A fabricated, unsourced statistic in a synthetic chapter must
        #    warn via gate_unsourced_stats (the real gate warns, not fails,
        #    for this class, matching its existing behaviour on site pages).
        stat = write_chapter(tmp, "95",
            "<p>The average family saves 60 hours a year by doing this.</p>")
        # gate_unsourced_stats scans all_pages() too; patch that to empty so
        # only the planted book chapter can produce a hit.
        real_all_pages = preflight.all_pages
        preflight.all_pages = lambda: []
        try:
            _, warns = with_files([stat],
                lambda: run_gate_capture(preflight.gate_unsourced_stats))
        finally:
            preflight.all_pages = real_all_pages
        check("unsourced stat in a book chapter warns via gate_unsourced_stats",
              any("unsourced-stats" == g for g, _ in warns))

        # 8. A British "organised" in a synthetic chapter must fail
        #    gate_us_spelling_consistency. Patch all_pages()/SITE's own glob
        #    contribution to empty by pointing site glob at the tmp dir too,
        #    so only the planted book chapter can produce a hit.
        brit = write_chapter(tmp, "94", "<p>A drawer that stays organised.</p>")
        real_site_glob = glob.glob
        def _site_glob_only_book(pattern, recursive=False):
            if pattern.startswith(preflight.SITE):
                return []
            return real_site_glob(pattern, recursive=recursive)
        preflight.glob.glob = _site_glob_only_book
        try:
            fails, _ = with_files([brit],
                lambda: run_gate_capture(preflight.gate_us_spelling_consistency))
        finally:
            preflight.glob.glob = real_site_glob
        check("planted British spelling in a book chapter fails "
              "gate_us_spelling_consistency",
              any("us-spelling-consistency" == g for g, _ in fails))
        check("failure names the planted file",
              any("chapter_94_final.html" in m for _, m in fails))

        # 9. The real, committed book manuscript, all 50 chapters: every
        #    extension must come back clean today (this row's 17 live
        #    instances were fixed at the source, this cycle, before this
        #    test was written).
        real_chapters = preflight.book_chapter_files()
        check("50 real chapter files found", len(real_chapters) == 50)
        fails, _ = run_gate_capture(preflight.gate_no_stray_dashes)
        check("real book manuscript clean on gate_no_stray_dashes", fails == [])
        fails, _ = run_gate_capture(preflight.gate_book_no_retired_terminology)
        check("real book manuscript clean on gate_book_no_retired_terminology",
              fails == [])
        fails, _ = run_gate_capture(preflight.gate_us_spelling_consistency)
        check("real book manuscript clean on gate_us_spelling_consistency",
              fails == [])

    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        preflight.FAIL.clear()
        preflight.WARN.clear()

    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
