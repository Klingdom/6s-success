#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_sample_pdf_spelling() catches a British
organis*/organiz* spelling inside the free sample PDF.

gate_us_spelling_consistency only globs site/**/*.html, so it cannot see a
British spelling that survives inside a checked-in PDF: the free sample book
(site/downloads/6S Success Home Edition - Sample (Chapters 1-30).pdf) is
compiled outside the site's own generator pipeline (no ops/build_*.py
produces it), so D11's 2026-09-14 spelling normalization, which reached
every HTML source, never reached this binary. Found live, 2026-09-16: 4
instances of "organised"/"organisation" shipped in the real file; 3
(pages 228, 253, 259, all plain SegoeUI) were fixed the same day by
redacting and re-inserting the whole word with the page's own embedded
font, verified pixel-correct and text-extraction-correct. The fourth
(page 243, SegoeUI-Semibold) stays live: pymupdf cannot resolve that
subset's glyphs when re-embedded as a fresh font resource, and a wrong
font would be worse than the inconsistency it fixes.

Builds small, isolated fixture PDFs with pymupdf rather than mutating the
real 32 MB sample, the same fixture-over-real-asset approach
test_gate_kdp_cover_current.py uses for its cover image. Also checks the
real committed file directly, proving the live finding rather than only a
synthetic one.

Run:  python ops/tests/test_gate_sample_pdf_spelling.py
"""
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

try:
    import pymupdf
except ImportError:
    pymupdf = None

PASS = FAIL = 0


def check(label, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok    {label}")
    else:
        FAIL += 1
        print(f"  FAIL  {label}")


def make_pdf(path, lines):
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 72), "\n".join(lines), fontsize=11)
    doc.save(path)
    doc.close()


def run_gate_against(path):
    preflight.FAIL.clear()
    preflight.WARN.clear()
    orig = preflight.SAMPLE_PDF_REL
    preflight.SAMPLE_PDF_REL = path
    try:
        preflight.gate_sample_pdf_spelling()
    finally:
        preflight.SAMPLE_PDF_REL = orig
    return list(preflight.FAIL), list(preflight.WARN)


def main():
    if pymupdf is None:
        print("  skipped: pymupdf not installed here")
        return 0

    # tempfile.mkdtemp(), outside the repo, the same convention
    # test_gate_kdp_cover_current.py's own _repo() uses: a fixture directory
    # git never sees at all is a run killed mid-test leaving nothing behind,
    # unlike a hardcoded in-repo path, which left ops/tests/_tmp_sample_pdf_
    # spelling/ as untracked cruft the one time this test did not reach its
    # own cleanup lines below, found live 2026-09-26 in a stop-hook's own
    # git-status check.
    tmp = tempfile.mkdtemp()
    try:
        clean = os.path.join(tmp, "clean.pdf")
        make_pdf(clean, ["A tidy shelf, organized by activity, not by category."])
        fails, warns = run_gate_against(clean)
        check("clean PDF: no fail", fails == [])
        check("clean PDF: no warn", warns == [])

        dirty = os.path.join(tmp, "dirty.pdf")
        make_pdf(dirty, ["Grouping the coffee things looks organised on a shelf."])
        fails, warns = run_gate_against(dirty)
        check("dirty PDF: never a hard fail (nothing here can safely rewrite it)",
              fails == [])
        check("dirty PDF: warns", len(warns) == 1)
        check("dirty PDF: names the gate", warns and warns[0][0] == "sample-pdf-spelling")
        check("dirty PDF: names the word", warns and "organised" in warns[0][1])
        check("dirty PDF: names page 1", warns and "page 1" in warns[0][1])

        missing = os.path.join(tmp, "does-not-exist.pdf")
        fails, warns = run_gate_against(missing)
        check("missing file: silent, not a false pass or crash",
              fails == [] and warns == [])

        real = os.path.join(ROOT, "site", "downloads",
                            "6S Success Home Edition - Sample (Chapters 1-30).pdf")
        if os.path.exists(real):
            fails, warns = run_gate_against(real)
            check("real committed file: 3 of 4 fixed, page 243 (semibold) "
                  "still carries the one instance nothing here can safely fix",
                  fails == [] and len(warns) == 1
                  and "organised" in warns[0][1]
                  and "1 page" in warns[0][1])
        else:
            print("  skipped: real sample PDF not present in this checkout")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{PASS} of {PASS + FAIL} cases pass")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
