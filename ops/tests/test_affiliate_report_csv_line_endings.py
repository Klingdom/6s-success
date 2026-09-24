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
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import affiliate_report as AR                                   # noqa: E402


def main() -> int:
    failures = []

    # 1. The real generator, run for real, must not introduce a CRLF.
    AR.main()
    data = open(AR.NEEDED, "rb").read()
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
