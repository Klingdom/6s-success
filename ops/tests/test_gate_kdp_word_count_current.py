#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_kdp_word_count_current() catches a book
word-count claim (in MARKETPLACE-LISTINGS.md or OWNER-ACTIONS.md) that has
drifted away from the committed EPUB it is supposed to describe.

Found 2026-09-10: both documents said "262,000 word", a figure written
2026-09-03 before later editing. Running the same counting method
build/listings/verify_epub.py already uses against the current
build/6S-Success-Home-Edition.epub counts 271,362, 3.5% higher. Corrected
both documents by hand; this gate stops the same drift recurring silently.

Found 2026-09-11: the fix above never covered MARKETPLACE-LISTINGS.md's own
"Verified on 2026-09-03" table row, "262,633 words excluding inline SVG,
across 56 documents", because the gate's regex required singular "word"
and this row used the plural. Widened to match both.

Run:  python ops/tests/test_gate_kdp_word_count_current.py
"""
import io
import os
import shutil
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

CONTAINER_XML = (
    '<?xml version="1.0"?>\n'
    '<container version="1.0" '
    'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
    '  <rootfiles>\n'
    '    <rootfile full-path="EPUB/content.opf" '
    'media-type="application/oebps-package+xml"/>\n'
    '  </rootfiles>\n'
    '</container>\n'
)

OPF = (
    '<?xml version="1.0"?>\n'
    '<package xmlns="http://www.idpf.org/2007/opf" version="3.0">\n'
    '  <metadata/>\n'
    '  <manifest>\n'
    '    <item id="c1" href="chapter1.xhtml" '
    'media-type="application/xhtml+xml"/>\n'
    '  </manifest>\n'
    '  <spine>\n'
    '    <itemref idref="c1"/>\n'
    '  </spine>\n'
    '</package>\n'
)


def _make_epub(path, word_count):
    body = "word " * word_count
    chapter = (
        "<?xml version='1.0'?><html xmlns='http://www.w3.org/1999/xhtml'>"
        "<body><p>%s</p></body></html>" % body
    )
    with zipfile.ZipFile(path, "w") as z:
        z.writestr(
            zipfile.ZipInfo("mimetype"),
            "application/epub+zip",
            zipfile.ZIP_STORED,
        )
        z.writestr("META-INF/container.xml", CONTAINER_XML)
        z.writestr("EPUB/content.opf", OPF)
        z.writestr("EPUB/chapter1.xhtml", chapter)


def _run(claim_text, live_words=100000, epub_present=True):
    tmp = tempfile.mkdtemp()
    build_dir = os.path.join(tmp, "build")
    os.makedirs(build_dir)
    epub_path = os.path.join(build_dir, "6S-Success-Home-Edition.epub")
    if epub_present:
        _make_epub(epub_path, live_words)
    io.open(os.path.join(tmp, "MARKETPLACE-LISTINGS.md"), "w",
            encoding="utf-8").write(claim_text)
    io.open(os.path.join(tmp, "OWNER-ACTIONS.md"), "w",
            encoding="utf-8").write("nothing relevant here.\n")
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_kdp_word_count_current()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. Claim matches the live count exactly: no failure.
    r, w = _run("A finished 100,000 word book is ready.")
    if r:
        fails.append("exact-match claim wrongly flagged: %r" % (r,))

    # 2. The real-world regression shape: a stale, understated figure
    #    (262,000 vs a real 271,362, 3.5% off) reproduced at this scale
    #    (90,000 claimed vs 100,000 real, 10% off, comfortably past the
    #    5% tolerance).
    r, w = _run("A finished 90,000 word book is ready.")
    if not r or "90,000" not in r[0][1] or "100000" not in r[0][1]:
        fails.append("stale understated claim not caught by name: %r" % (r,))

    # 3. A claim within the 5% rounding tolerance: no failure.
    r, w = _run("A finished 97,000 word book is ready.")
    if r:
        fails.append("within-tolerance claim wrongly flagged: %r" % (r,))

    # 4. A short, non-book-length number (e.g. a card count) must not be
    #    mistaken for a word-count claim.
    r, w = _run("A finished 88 word deck is ready.")
    if r:
        fails.append("a non-book-length number was wrongly treated as a "
                      "word-count claim: %r" % (r,))

    # 5b. Found 2026-09-11: the regex only matched singular "word", so a
    #     claim phrased with the plural "words" (the exact shape
    #     MARKETPLACE-LISTINGS.md's own "Verified" table row used, "262,633
    #     words excluding inline SVG") never matched at all, no matter how
    #     stale. Reproduced at this scale: 90,000 claimed vs 100,000 real,
    #     comfortably past the 5% tolerance, phrased with the plural.
    r, w = _run("A finished 90,000 words book is ready.")
    if not r or "90,000" not in r[0][1] or "100000" not in r[0][1]:
        fails.append("a plural-form ('words') stale claim not caught by "
                      "name: %r" % (r,))

    # 5c. The plural form must still tolerate a within-5% rounding, the
    #     same as the singular form in case 3.
    r, w = _run("A finished 97,000 words book is ready.")
    if r:
        fails.append("a plural-form within-tolerance claim wrongly "
                      "flagged: %r" % (r,))

    # 5. No EPUB on disk: warn, never a silent pass and never a fail.
    r, w = _run("A finished 90,000 word book is ready.", epub_present=False)
    if r:
        fails.append("a missing EPUB was failed instead of warned: %r"
                      % (r,))
    if not w:
        fails.append("a missing EPUB produced no warning at all")

    # 6. The real, committed documents and EPUB: clean, now that the
    #    stale 262,000 figure has been corrected.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_kdp_word_count_current()
    if preflight.FAIL:
        fails.append("the real committed documents failed: %r"
                     % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_kdp_word_count_current, 8/8 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
