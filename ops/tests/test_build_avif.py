#!/usr/bin/env python3
"""
Prove ops/build_avif.py's wire() checks avif coverage per <picture> block,
not per file.

Found 2026-09-10, reading the file cold: wire() skipped an entire page the
instant it contained any 'type="image/avif"' string anywhere in it, on the
theory that a page carrying one avif source has already been wired. That
holds for a page wired in a single pass, but not for one whose pictures were
wired across separate runs (or a hand-maintained page that gained a second
picture block after the first was already wired): the second, still
webp-only source tag was silently skipped forever, even once its own .avif
file existed on disk, because the check never looked past the first match in
the file. Reproduced directly on a two-picture fixture (see
picture_two_wires_only_missing_one below): the first block already carried
an avif source, the second did not though its .avif sibling existed, and the
old code added nothing. Fixed by checking, per source tag, whether an avif
source immediately precedes it, rather than checking the whole file once.

Run:  python ops/tests/test_build_avif.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import build_avif                                                 # noqa: E402


def write(path, text):
    io.open(path, "w", encoding="utf-8", newline="").write(text)


def read(path):
    return io.open(path, encoding="utf-8").read()


def main() -> int:
    fails = []
    tmp = tempfile.mkdtemp(prefix="test_build_avif_")
    real_site = build_avif.SITE
    try:
        build_avif.SITE = tmp

        # 1. The exact regression: one picture already avif-wired, a second
        #    picture in the same file still webp-only, its .avif sibling
        #    already on disk. The second must get wired too.
        page = os.path.join(tmp, "two.html")
        write(page, (
            "<picture>\n"
            '<source type="image/avif" srcset="img1.avif">\n'
            '<source type="image/webp" srcset="img1.webp">\n'
            "<img src=\"img1.webp\">\n"
            "</picture>\n"
            "<picture>\n"
            '<source type="image/webp" srcset="img2.webp">\n'
            "<img src=\"img2.webp\">\n"
            "</picture>\n"
        ))
        for name in ("img1.webp", "img1.avif", "img2.webp", "img2.avif"):
            write(os.path.join(tmp, name), "")

        build_avif.wire()
        out = read(page)
        if out.count('type="image/avif"') != 2:
            fails.append(
                "second picture's still-missing avif source was not added: "
                "expected 2 avif sources, found %d\n%s"
                % (out.count('type="image/avif"'), out))
        if 'srcset="img2.avif"' not in out:
            fails.append("img2's avif source was not wired in")
        # The already-wired first block must be left exactly alone: one
        # avif source, not duplicated.
        if out.count('srcset="img1.avif"') != 1:
            fails.append("the already-wired first picture was touched: %r"
                         % out.count('srcset="img1.avif"'))

        # 2. Idempotency: running wire() again on the now-fully-wired file
        #    changes nothing.
        before = read(page)
        build_avif.wire()
        after = read(page)
        if before != after:
            fails.append("a second wire() run on a fully-wired page changed it")

        # 3. A source whose avif sibling does not exist on disk is still
        #    correctly skipped, not fabricated.
        page2 = os.path.join(tmp, "missing.html")
        write(page2, (
            "<picture>\n"
            '<source type="image/webp" srcset="img3.webp">\n'
            "<img src=\"img3.webp\">\n"
            "</picture>\n"
        ))
        write(os.path.join(tmp, "img3.webp"), "")
        build_avif.wire()
        out2 = read(page2)
        if 'type="image/avif"' in out2:
            fails.append("an avif source was wired for a file with no .avif on disk")

    finally:
        build_avif.SITE = real_site
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("PASS: 3 case(s), per-block avif coverage, idempotency, "
          "missing-file skip all correct")
    return 0


if __name__ == "__main__":
    sys.exit(main())
