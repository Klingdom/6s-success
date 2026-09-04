"""Stamp the site with a content hash, so "is this build live" has an answer.

WHY THIS EXISTS

ops/deploy.py has now twice reported a successful deploy of a build production
had never received.

The first version compared PRODUCT COUNTS. They were 159 before and 159 after,
so a release that shipped nothing printed "production already matched the
repository". The fix was to also compare the fingerprint of the stylesheet the
home page asks for, which moves whenever the CSS moves.

That was better and still wrong, and its own commit message said so: a release
that touches no CSS does not move the stylesheet hash. On 2026-09-04 exactly
that happened. A release carrying 1,717 new retailer links across 114 zone
pages, a rebuilt card deck and a corrected PDF touched no CSS, the stamp
matched, and deploy.py declared production current while it served none of it.
Verified by fetching a zone page and counting zero retailer links.

Both versions failed the same way: they sampled one thing and reasoned about
everything. The question "is production serving THIS build" is a question about
the whole site, so the signal has to be a function of the whole site.

WHAT THIS IS

A single file, site/build-id.txt, holding a hash of every other file under
site/. Any change to any deployed byte changes it. It is committed, so the
container image carries it, and deploy.py fetches https://6s-success.com/
build-id.txt and compares. Equal means the bytes serving are the bytes here.

It excludes itself, or hashing would never converge.

    python ops/build_id.py           write it
    python ops/build_id.py --check   is the file current for this tree
"""
from __future__ import annotations

import hashlib
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
STAMP = os.path.join(SITE, "build-id.txt")


def compute() -> str:
    """Hash every deployed file, path included, in a stable order.

    The path is hashed as well as the content, so moving a file to a new URL
    is a change even when its bytes are identical. Sorted, because os.walk
    yields directories in filesystem order and an unsorted walk gives a
    different answer on a different machine, which is the bug that made the
    sitemap nondeterministic in CI earlier the same week.
    """
    h = hashlib.sha256()
    for dirpath, dirnames, filenames in os.walk(SITE):
        dirnames[:] = sorted(dirnames)
        for fn in sorted(filenames):
            p = os.path.join(dirpath, fn)
            if os.path.abspath(p) == os.path.abspath(STAMP):
                continue
            rel = os.path.relpath(p, SITE).replace(os.sep, "/")
            h.update(rel.encode("utf-8"))
            h.update(b"\0")
            with io.open(p, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
    return h.hexdigest()[:16]


def current() -> str | None:
    if not os.path.exists(STAMP):
        return None
    return io.open(STAMP, encoding="utf-8").read().strip() or None


def main() -> int:
    want = compute()
    if "--check" in sys.argv:
        have = current()
        print("  build id in tree : %s" % (have or "MISSING"))
        print("  computed now     : %s" % want)
        if have == want:
            print("  current")
            return 0
        print("  STALE. Run: python ops/build_id.py")
        return 1
    io.open(STAMP, "w", encoding="utf-8", newline="").write(want + "\n")
    print("  site/build-id.txt = %s" % want)
    return 0


if __name__ == "__main__":
    sys.exit(main())
