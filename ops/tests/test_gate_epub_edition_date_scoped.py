#!/usr/bin/env python3
"""
Prove gate_epub_edition_date_current() and the widened _last_commit_epoch()
it now calls are scoped to the EPUB's actual source files, not the whole
content/book/ directory.

Found 2026-11-26: this gate used to check content/book/'s last commit as a
whole, so editing "6S Success Home Edition - Sample (Chapters 1-30).html"
(a separate, hand-authored file ops/build_sample_html.py reads for the free
web sample, unrelated to the paid EPUB) FAILed it even though the EPUB's
own content had not changed, which would have meant bumping EDITION_DATE
on a false claim just to clear the gate. Narrowed to book_chapter_files()
plus assets/ and the front matter, the files ops/build_epub.py actually
reads.

Run:  python ops/tests/test_gate_epub_edition_date_scoped.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    # 1. _last_commit_epoch now takes several pathspecs and returns the
    #    latest among them, not just the first. A file that does not exist
    #    contributes nothing; a real file's own commit still counts.
    only_real = preflight._last_commit_epoch("ops/build_epub.py")
    with_bogus = preflight._last_commit_epoch(
        "content/book/this-path-does-not-exist-anywhere", "ops/build_epub.py")
    if with_bogus != only_real:
        fails.append(
            "adding a nonexistent pathspec changed the result: %r vs %r"
            % (with_bogus, only_real))

    # 2. The real gate, against the real repository, must be clean today:
    #    the only content/book/ file this cycle touched is the separate
    #    sample-book master, which is not one of build_epub.py's own
    #    inputs.
    before = len(preflight.FAIL)
    preflight.gate_epub_edition_date_current()
    new_fails = preflight.FAIL[before:]
    del preflight.FAIL[before:]
    if new_fails:
        fails.append(
            "gate_epub_edition_date_current failed against the real repo "
            "after narrowing its scope to the EPUB's actual inputs: %r"
            % (new_fails,))

    # 3. The scoped source list itself must actually be the EPUB's real
    #    inputs, not empty and not the whole directory: book_chapter_files()
    #    returns the 50 real chapter files, confirmed non-empty, and the
    #    unrelated sample-book master is not among them.
    chapters = preflight.book_chapter_files()
    if len(chapters) < 40:
        fails.append("book_chapter_files() returned too few files: %d"
                     % len(chapters))
    if any("Sample (Chapters" in p for p in chapters):
        fails.append("the unrelated sample-book master leaked into "
                     "book_chapter_files()")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: gate_epub_edition_date_current is scoped to the EPUB's "
          "real source files, and _last_commit_epoch correctly takes "
          "several pathspecs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
