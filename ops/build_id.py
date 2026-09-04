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
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
STAMP = os.path.join(SITE, "build-id.txt")


def compute() -> str:
    """Hash what git stores for site/, path and blob id, in sorted order.

    NOT the working-tree bytes. The first version walked the directory and
    hashed the files, which gave one answer on this Windows machine and a
    different one on the Linux CI runner, because git checks the same commit
    out with CRLF here and LF there. The gate failed on its first run for a
    reason that had nothing to do with the site being stale.

    Blob ids are git's own normalised content hashes, so they are identical on
    every platform, and they describe the COMMIT rather than the desk it is
    being edited on. That is the right thing to compare against production
    anyway: the container image is built from the commit, not from whatever
    happens to be lying in the folder.

    Falls back to None-by-exception if git cannot answer, and main() turns that
    into a loud failure rather than a hash of nothing.
    """
    out = subprocess.run(["git", "ls-files", "-s", "site"], cwd=ROOT,
                         capture_output=True, text=True, timeout=300)
    if out.returncode != 0 or not out.stdout.strip():
        raise SystemExit("  could not read git's index for site/, so no build "
                         "id can be computed. Refusing to write a hash that "
                         "would describe nothing.")
    h = hashlib.sha256()
    rows = []
    for line in out.stdout.splitlines():
        # "<mode> <blobsha> <stage>\t<path>"
        meta, _, path = line.partition("\t")
        parts = meta.split()
        if len(parts) < 2 or not path:
            continue
        if path.replace("\\", "/").endswith("site/build-id.txt"):
            continue          # excluding itself, or it could never converge
        rows.append((path.replace("\\", "/"), parts[1]))
    for path, blob in sorted(rows):
        h.update(path.encode("utf-8"))
        h.update(b"\0")
        h.update(blob.encode("ascii"))
        h.update(b"\0")
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
