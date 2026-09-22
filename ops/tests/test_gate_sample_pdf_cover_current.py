#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_sample_pdf_cover_current() catches the free
sample PDF's cover claiming to be "The Complete Book" while it only holds
chapters 1 to 30 of 50.

REVIEW-QA-2026-09-07.md found this live, 2026-09-07: STATUS.md recorded the
claim fixed twice (2026-08-17, 2026-08-19), both times in
content/book/.../Sample (Chapters 1-30).html and the filename, never in the
shipped PDF's own rendered cover, because nothing compiles that binary from
the HTML (the same gap gate_sample_pdf_spelling's own docstring names for
wording). Fixed directly, 2026-09-22, this operator: page 1's cover
redacted and reinserted with the corrected line, using the page's own
embedded Georgia font subset.

Builds small, isolated fixture PDFs with pymupdf rather than mutating the
real 32 MB sample, the same fixture-over-real-asset approach
test_gate_sample_pdf_spelling.py uses. Also checks the real committed file
directly, proving the live fix rather than only a synthetic one.

Run:  python ops/tests/test_gate_sample_pdf_cover_current.py
"""
import os
import sys

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


def make_pdf(path, cover_text):
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 72), cover_text, fontsize=16)
    doc.save(path)
    doc.close()


def run_gate_against(path):
    preflight.FAIL.clear()
    preflight.WARN.clear()
    orig = preflight.SAMPLE_PDF_REL
    preflight.SAMPLE_PDF_REL = path
    try:
        preflight.gate_sample_pdf_cover_current()
    finally:
        preflight.SAMPLE_PDF_REL = orig
    return list(preflight.FAIL), list(preflight.WARN)


def main():
    if pymupdf is None:
        print("  skipped: pymupdf not installed here")
        return 0

    tmp = os.path.join(ROOT, "ops", "tests", "_tmp_sample_pdf_cover")
    os.makedirs(tmp, exist_ok=True)

    clean = os.path.join(tmp, "clean.pdf")
    make_pdf(clean, "Home Edition · Chapters 1 to 30")
    fails, warns = run_gate_against(clean)
    check("clean PDF: no fail", fails == [])
    check("clean PDF: no warn", warns == [])

    dirty = os.path.join(tmp, "dirty.pdf")
    make_pdf(dirty, "Home Edition · The Complete Book")
    fails, warns = run_gate_against(dirty)
    check("dirty PDF: fails", len(fails) == 1)
    check("dirty PDF: names the gate", fails and fails[0][0] == "sample-pdf-cover")
    check("dirty PDF: names the claim",
          fails and "complete book" in fails[0][1].lower())

    dirty_case = os.path.join(tmp, "dirty_case.pdf")
    make_pdf(dirty_case, "Home Edition · the COMPLETE BOOK")
    fails, warns = run_gate_against(dirty_case)
    check("case-insensitive match: fails", len(fails) == 1)

    missing = os.path.join(tmp, "does-not-exist.pdf")
    fails, warns = run_gate_against(missing)
    check("missing file: silent, not a false pass or crash",
          fails == [] and warns == [])

    real = os.path.join(ROOT, "site", "downloads",
                        "6S Success Home Edition - Sample (Chapters 1-30).pdf")
    if os.path.exists(real):
        fails, warns = run_gate_against(real)
        check("real committed file: cover fixed, no fail", fails == [])
    else:
        print("  skipped: real sample PDF not present in this checkout")

    for f in (clean, dirty, dirty_case):
        try:
            os.remove(f)
        except OSError:
            pass
    try:
        os.rmdir(tmp)
    except OSError:
        pass

    print(f"\n{PASS} of {PASS + FAIL} cases pass")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
