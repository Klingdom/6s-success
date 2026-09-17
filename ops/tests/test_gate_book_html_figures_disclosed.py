#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_book_html_figures_disclosed() catches
REVIEW-QA-2026-09-07.md's "the free HTML book has none of the book's
pictures" finding coming back.

site/book.html offers the free sample book in two formats: an HTML edition
and a PDF. The PDF embeds a real picture for every figure; the HTML
edition's own figures render mostly as a plain "Figure description" text
box, because it ships 0 <img> tags. Fixed 2026-09-17 by adding a
.fulfil-note disclosure next to the two format buttons naming the real
count. This gate re-derives the HTML sample's own figure/image/text-desc
counts on every run and fails if the disclosure disappears, or if its
stated numbers drift from what the shipped sample actually contains.

Uses an isolated tmp ROOT (the test_gate_standards_pack_current.py pattern)
so it never mutates the real, large sample files, plus one direct check
against the real committed files.

Run:  python ops/tests/test_gate_book_html_figures_disclosed.py
"""
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


def sample_html(n_figures, n_img, n_textdesc):
    """A minimal fixture with the exact counting hooks the gate reads:
    <figure> tags, <img> tags, and 'Figure description' text boxes."""
    figs = []
    for i in range(n_figures):
        if i < n_img:
            body = f'<img src="f{i}.jpg" alt="figure {i}">'
        elif i < n_img + n_textdesc:
            body = "<p><b>Figure description</b> a room, described in words.</p>"
        else:
            body = "<p>a figure with neither, should not occur in practice</p>"
        figs.append(f"<figure>{body}</figure>")
    return "<html><body>" + "".join(figs) + "</body></html>"


def book_html(disclosure_text=None):
    disclosure = ""
    if disclosure_text:
        disclosure = f'<p class="fulfil-note">{disclosure_text}</p>'
    return (
        '<html><body><div class="cta-row">'
        '<a href="downloads/x.html">Read chapters 1 to 30 free</a>'
        '<a href="downloads/x.pdf">Download (PDF)</a>'
        "</div>" + disclosure + "</body></html>"
    )


def _run(book, sample):
    tmp = tempfile.mkdtemp()
    downloads_dir = os.path.join(tmp, "site", "downloads")
    os.makedirs(downloads_dir, exist_ok=True)
    io.open(os.path.join(tmp, "site", "book.html"),
            "w", encoding="utf-8").write(book)
    io.open(os.path.join(downloads_dir,
                          "6S Success Home Edition - Sample (Chapters 1-30).html"),
            "w", encoding="utf-8").write(sample)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_book_html_figures_disclosed()
        return list(preflight.FAIL)
    finally:
        preflight.ROOT = old_root
        shutil.rmtree(tmp)


def main() -> int:
    sample = sample_html(n_figures=231, n_img=0, n_textdesc=172)

    # 1. The real fix: disclosure present, numbers match the sample.
    r = _run(book_html("The two formats differ. 172 of 231 figures are a "
                        "text description instead of a picture."), sample)
    check("correct disclosure passes clean", not r)

    # 2. The regression this gate exists to catch: no disclosure at all.
    r = _run(book_html(None), sample)
    check("missing disclosure is caught",
          any("book-html-figures-disclosed" in g for g, _ in r))

    # 3. A disclosure that names the wrong count (source drifted, page
    #    never re-derived, the dominant defect class this repo tracks).
    r = _run(book_html("The two formats differ. 5 of 231 figures are a "
                        "text description instead of a picture."), sample)
    check("stale count in the disclosure is caught",
          any("book-html-figures-disclosed" in g for g, _ in r))

    # 4. If the HTML edition ever gets real artwork (0 text-desc boxes,
    #    every figure an <img>), the old disclosure's exact wording is no
    #    longer the point; the gate should not block that improvement.
    illustrated = sample_html(n_figures=231, n_img=231, n_textdesc=0)
    r = _run(book_html(None), illustrated)
    check("fully illustrated HTML edition needs no disclosure", not r)

    # 5. Neither file present (page retired, or sample renamed): nothing
    #    to check, no false failure.
    tmp = tempfile.mkdtemp()
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_book_html_figures_disclosed()
        r = list(preflight.FAIL)
    finally:
        preflight.ROOT = old_root
        shutil.rmtree(tmp)
    check("both files absent is not a false failure", not r)

    # 6. The real committed files: proves the live finding is actually
    #    fixed, not only the synthetic fixture.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_book_html_figures_disclosed()
    check("real committed site/book.html passes clean", not preflight.FAIL)

    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
