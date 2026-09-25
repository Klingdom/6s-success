#!/usr/bin/env python3
"""
Prove ops/affiliate_report.py writes affiliate-link-input-needed.csv with LF
line endings, not CRLF.

csv.writer defaults to '\\r\\n' (the "excel" dialect), and the file is opened
with newline="" specifically so csv.writer's own terminator is not doubled by
universal-newline translation. That combination is correct for CSV in
general, but every other generated artifact in this repository is committed
as LF (the .gitattributes header explains why, after a PDF got corrupted by
the opposite mistake, and a rule there pins caption sidecars to LF for the
same reason). Without an explicit lineterminator, a fresh run of this
generator flips affiliate-link-input-needed.csv from the committed LF to
CRLF, a same-content, different-bytes diff nobody asked for and no test
caught, the exact "the source was corrected and the shipped artifact was
never re-derived from it" shape this repository's own dominant defect class
already names, just running in the other direction: here the generator itself
would drift from what is committed the moment it is next run.

Reproduced directly: with lineterminator dropped, the writer emits CRLF for
every row.

Run:  python ops/tests/test_affiliate_report_csv_line_endings.py
"""
import csv
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import affiliate_report as AR                                   # noqa: E402


def main() -> int:
    failures = []

    # 1. The real generator, run for real, must not introduce a CRLF.
    #
    # Run against a tmp directory, never against AR's own ROOT-anchored
    # MATRIX/EXCEPTIONS/NEEDED paths. Found live 2026-09-25: this test used to
    # call AR.main() with those module constants untouched, which wrote
    # AFFILIATE_COMPLIANCE_MATRIX.md and AFFILIATE_INPUT_EXCEPTIONS.md for
    # real into the repository root every time the suite ran. Both carry a
    # "Generated ... on <today>" line, so any run of this test on a later
    # calendar day than the last commit left those two files dirty in the
    # working tree, with nothing to notice. gate_generator_ownership found
    # exactly that dirt live in CI run 403 (2 files differing, both these),
    # and correctly refused to run rather than diff a meaningless tree,
    # failing the whole publish-image.yml build and leaving real, already
    # merged site/ content (a personalised Garage room) sitting unpublished
    # behind it. gate_affiliate_report_current already proves this generator
    # matches the committed files by running it in a tmp directory; this test
    # only needs the real AR.main() codepath for its CRLF check, not the real
    # file paths, so it now uses the same isolation.
    tmp = tempfile.mkdtemp(prefix="affiliate_report_csv_test_")
    orig = (AR.MATRIX, AR.EXCEPTIONS, AR.NEEDED)
    AR.MATRIX = os.path.join(tmp, "matrix.md")
    AR.EXCEPTIONS = os.path.join(tmp, "exceptions.md")
    AR.NEEDED = os.path.join(tmp, "needed.csv")
    try:
        AR.main()
        data = open(AR.NEEDED, "rb").read()
    finally:
        AR.MATRIX, AR.EXCEPTIONS, AR.NEEDED = orig
        shutil.rmtree(tmp, ignore_errors=True)
    if b"\r" in data:
        failures.append(
            "affiliate-link-input-needed.csv contains a carriage return "
            "after a real run of ops/affiliate_report.py; every other "
            "generated artifact in this repository is LF-only")
    if data.count(b"\n") == 0:
        failures.append("affiliate-link-input-needed.csv has no newlines "
                         "at all; the generator produced no rows")

    # 2. Reproduce the pre-fix shape directly, so this test is proven to
    #    actually catch the defect it names, not just check today's file.
    buf = io.StringIO()
    w = csv.writer(buf)  # no lineterminator: this is the old, buggy call
    w.writerow(["a", "b"])
    if b"\r\n" not in buf.getvalue().encode("utf-8"):
        failures.append("csv.writer's default dialect did not emit CRLF in "
                         "this Python; the regression this test guards "
                         "against may no longer be reachable the old way")

    buf2 = io.StringIO()
    w2 = csv.writer(buf2, lineterminator="\n")
    if b"\r" in buf2.getvalue().encode("utf-8"):
        failures.append("lineterminator='\\n' still produced a carriage "
                         "return; the fix itself is broken")

    if failures:
        print("FAIL: affiliate_report.py CSV line endings")
        for f in failures:
            print("  - %s" % f)
        return 1

    print("PASS: affiliate-link-input-needed.csv is LF-only after a real "
          "run, and the CRLF-vs-LF distinction this test relies on is "
          "proven reachable both ways")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
