#!/usr/bin/env python3
"""
Prove gate_generator_ownership treats a repacked archive as unchanged only
when every entry inside it is unchanged.

Added 2026-09-17. build/6S-Success-Home-Edition.epub is a zip. Rebuilt here it
came out byte-different from the committed copy while all 62 entries were
byte-identical, so the ownership gate blocked every deploy over a file nobody
had edited. Python 3.14 links zlib-ng, CI's links stock zlib 1.3.1, and the
two produce different DEFLATE streams from the same input; the archive's
container is simply not reproducible across environments.

The risk of the fix is that it hides real drift inside an archive, so this
pins the boundary: same entries, different compression is fine; any entry
added, removed or changed is not.

Run:  python ops/tests/test_zip_content_identical.py
"""
import io
import os
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight as P                                          # noqa: E402


def make(path_or_buf, entries, compression=zipfile.ZIP_DEFLATED, level=None):
    kw = {"compression": compression}
    if level is not None:
        kw["compresslevel"] = level
    with zipfile.ZipFile(path_or_buf, "w", **kw) as z:
        for name, body in entries:
            z.writestr(name, body)


def main():
    failures = []
    base = [("mimetype", "application/epub+zip"),
            ("OEBPS/ch1.xhtml", "<p>" + "chapter one " * 400 + "</p>"),
            ("OEBPS/ch2.xhtml", "<p>" + "chapter two " * 400 + "</p>")]

    d = tempfile.mkdtemp()
    disk = os.path.join(d, "book.epub")

    cases = [
        ("same entries, different compression level",
         base, base, zipfile.ZIP_DEFLATED, 1, True),
        ("same entries, stored vs deflated",
         base, base, zipfile.ZIP_STORED, None, True),
        ("one entry's text changed",
         base, base[:2] + [("OEBPS/ch2.xhtml", "<p>different</p>")],
         zipfile.ZIP_DEFLATED, None, False),
        ("an entry added",
         base, base + [("OEBPS/ch3.xhtml", "<p>new</p>")],
         zipfile.ZIP_DEFLATED, None, False),
        ("an entry removed",
         base, base[:2], zipfile.ZIP_DEFLATED, None, False),
    ]

    for name, committed_entries, disk_entries, comp, level, expected in cases:
        buf = io.BytesIO()
        make(buf, committed_entries)
        make(disk, disk_entries, comp, level)
        got = P._zip_content_identical(
            os.path.relpath(disk, ROOT).replace(os.sep, "/"),
            committed_bytes=buf.getvalue())
        if got != expected:
            failures.append("%s: expected %s, got %s" % (name, expected, got))

    # Not a zip at all, and a path that does not exist: both must be False,
    # never a crash and never an accidental pass.
    junk = os.path.join(d, "not-a-zip.epub")
    with open(junk, "wb") as fh:
        fh.write(b"this is not a zip file")
    if P._zip_content_identical(os.path.relpath(junk, ROOT).replace(os.sep, "/"),
                                committed_bytes=b"also not a zip"):
        failures.append("a non-zip file read as content-identical")
    if P._zip_content_identical("build/no-such-file-anywhere.epub",
                                committed_bytes=b""):
        failures.append("a missing file read as content-identical")

    for f in failures:
        print("FAIL:", f)
    print("ok, %d cases" % (len(cases) + 2) if not failures
          else "%d failure(s)" % len(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
