#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_binary_files_protected() catches the defect
class REVIEW-QA-2026-09-07.md found: no `.gitattributes`, so git guesses
whether a binary file is text and can silently corrupt one with line-ending
conversion on a Windows checkout. The review measured this on the free
deck PDF: the tree copy carried 2,092 injected `\r` bytes, shifting every
later byte offset so the trailer's `startxref` pointer landed in the middle
of a compressed stream instead of on the `xref` keyword.

Also proves a real bug this gate's own first version had, caught before it
shipped: counting `\r\n` byte pairs anywhere in a PDF is not the right
signal. The real, live sample-book PDF carries 506 legitimate `\r\n` pairs
in its own content while its `startxref` resolves exactly, and a gate that
flagged it would have been a false alarm on a healthy file. Case 4 below is
that exact regression test.

Run:  python ops/tests/test_gate_binary_files_protected.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _pdf(xref_pos_correct: bool, extra_crlf: bool = False) -> bytes:
    """A minimal but structurally real single-object PDF, optionally with
    the exact corruption shape (startxref pointing at the wrong byte) or
    with harmless \\r\\n bytes inside its own content that must NOT be
    treated as a defect on their own."""
    body = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n"
    if extra_crlf:
        body += b"2 0 obj\n<< /Content (line one\r\nline two) >>\nendobj\n"
    xref_offset = len(body)
    xref = b"xref\n0 1\n0000000000 65535 f \ntrailer\n<< /Size 1 >>\n"
    tail = b"startxref\n" + str(xref_offset if xref_pos_correct else xref_offset + 5).encode() + b"\n%%EOF\n"
    return body + xref + tail


def main() -> int:
    fails = []

    # 1. A structurally sound PDF: startxref resolves to the xref keyword.
    good = _pdf(xref_pos_correct=True)
    r1 = preflight.check_pdf_startxref_resolves(good)
    if r1 is not None:
        fails.append(f"a healthy PDF was flagged: {r1}")

    # 2. The real corruption shape: startxref shifted off the xref keyword,
    #    the exact signature the review measured (offsets shifted by
    #    injected bytes).
    corrupted = _pdf(xref_pos_correct=False)
    r2 = preflight.check_pdf_startxref_resolves(corrupted)
    if r2 is None:
        fails.append("a PDF with a shifted startxref was not caught")

    # 3. No startxref at all (truncated/garbage file) must also be caught,
    #    not silently treated as fine.
    r3 = preflight.check_pdf_startxref_resolves(b"%PDF-1.4\nnot a real pdf")
    if r3 is None:
        fails.append("a PDF with no startxref at all was not caught")

    # 4. REGRESSION: legitimate \r\n bytes inside the PDF's own content,
    #    with a startxref that still resolves correctly, must NOT be
    #    flagged. This is the real live sample-book PDF's shape (506
    #    \r\n pairs, startxref exact) and the first version of this check
    #    got it wrong.
    healthy_with_crlf = _pdf(xref_pos_correct=True, extra_crlf=True)
    assert healthy_with_crlf.count(b"\r\n") > 0, "test fixture setup is wrong"
    r4 = preflight.check_pdf_startxref_resolves(healthy_with_crlf)
    if r4 is not None:
        fails.append(f"a healthy PDF with legitimate \\r\\n content was "
                      f"flagged: {r4}")

    # 5. .gitattributes declaration coverage: every type in BINARY_EXTS
    #    present is fine, one missing is caught.
    complete = "\n".join(f"*{e} binary" for e in preflight.BINARY_EXTS)
    m5 = preflight.check_gitattributes_declares(complete)
    if m5:
        fails.append(f"a complete .gitattributes reported missing: {m5}")

    incomplete = complete.replace("*.pdf binary\n", "")
    m6 = preflight.check_gitattributes_declares(incomplete)
    if ".pdf" not in m6:
        fails.append(f".pdf missing from .gitattributes was not caught: {m6}")

    # 6. The real, live files must be clean after the actual fix: the
    #    committed .gitattributes and both shipped PDFs.
    ga_path = os.path.join(ROOT, ".gitattributes")
    if not os.path.exists(ga_path):
        fails.append(".gitattributes does not exist in the real repository")
    else:
        real_text = open(ga_path, encoding="utf-8").read()
        real_missing = preflight.check_gitattributes_declares(real_text)
        if real_missing:
            fails.append(f"real .gitattributes missing: {real_missing}")
    for dirpath, _dirs, files in os.walk(os.path.join(ROOT, "site")):
        for fn in files:
            if fn.lower().endswith(".pdf"):
                p = os.path.join(dirpath, fn)
                reason = preflight.check_pdf_startxref_resolves(
                    open(p, "rb").read())
                if reason:
                    fails.append(f"real file {p} fails: {reason}")

    if fails:
        print(f"  {len(fails)} of 6 cases fail:")
        for f in fails:
            print(f"   - {f}")
        return 1
    print("  6 of 6 cases pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
