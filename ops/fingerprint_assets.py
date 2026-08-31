#!/usr/bin/env python3
"""
Put a content hash on every stylesheet and script reference.

THE BUG THIS FIXES
------------------
nginx serves /assets/ with max-age 2592000 under a comment reading "long cache
for fingerprint-stable static assets". Nothing ever fingerprinted them. The
files are served at fixed names with a thirty day cache, so a returning visitor
holds whatever CSS they were given for a month, and any fix shipped in between
never reaches them. The site had been running that way since launch.

The heading spacing fix on 2026-08-23 is the case that made it visible: correct
in the repository, correct in the image, correct on a cold fetch, and invisible
to anyone who had loaded the site in the previous thirty days.

WHY QUERY STRINGS AND NOT HASHED FILENAMES
------------------------------------------
Roughly a dozen generators emit `assets/css/site.css` as a literal. Hashed
filenames would mean every one of them learning the current hash, and a
generator run out of order would emit a name with nothing behind it. A query
string leaves the path alone: nginx resolves the same file, and the browser
treats it as a new URL. The whole change lives in this one pass.

WHY IT IS SAFE TO RUN ANY TIME
------------------------------
Idempotent. It replaces an existing ?v= rather than appending to it, so running
it twice produces the same bytes as running it once. Run it after any builder
that writes HTML, and run it last.

Run:  python ops/fingerprint_assets.py
      python ops/fingerprint_assets.py --check     (fails if anything is stale)
"""
from __future__ import annotations

import glob
import hashlib
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

# Only what actually goes stale in a way a visitor notices. Images and fonts are
# effectively immutable here: they are replaced by adding a file, not by editing
# one, so a thirty day cache on them is correct rather than a bug.
VERSIONED = (".css", ".js")

# href="../assets/css/site.css"  or  src="assets/js/site.js?v=oldhash"
REF = re.compile(
    r'((?:href|src)=")((?:\.\./)*assets/[A-Za-z0-9_./-]+?'
    r'(?:' + "|".join(re.escape(e) for e in VERSIONED) + r'))(\?v=[0-9a-f]+)?(")')

_cache: dict[str, str] = {}


def digest(path: str) -> str:
    """A content hash that is the same on Windows and on Linux.

    Hashing raw bytes looked right and was not. Git converts line endings on
    checkout, so a stylesheet hashed on a Windows working copy and the same
    stylesheet hashed in CI produce different digests, and the CI gate would
    have failed on every run with nothing actually wrong. Found by reverting a
    file and watching it stay stale.

    Normalising CRLF to LF before hashing costs nothing: the digest is an
    identity token for the cache key, not a checksum of the served bytes. It
    only has to change when the content changes, and to agree everywhere.
    """
    if path not in _cache:
        raw = io.open(path, "rb").read().replace(b"\r\n", b"\n")
        _cache[path] = hashlib.sha256(raw).hexdigest()[:10]
    return _cache[path]


def main(check_only: bool) -> int:
    pages = sorted(glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True))
    changed, refs, stale, missing = 0, 0, [], []

    for page in pages:
        s = io.open(page, encoding="utf-8").read()
        out = []
        pos = 0

        for m in REF.finditer(s):
            nonlocal_ref = m.group(2)
            target = os.path.normpath(
                os.path.join(os.path.dirname(page), nonlocal_ref))
            rel = os.path.relpath(page, ROOT)

            if not os.path.exists(target):
                missing.append(f"{rel} -> {nonlocal_ref}")
                continue

            want = "?v=" + digest(target)
            refs += 1
            if m.group(3) != want:
                stale.append(f"{rel} -> {nonlocal_ref}")
                out.append(s[pos:m.start()])
                out.append(m.group(1) + nonlocal_ref + want + m.group(4))
                pos = m.end()

        if pos and not check_only:
            out.append(s[pos:])
            io.open(page, "w", encoding="utf-8", newline="").write("".join(out))
            changed += 1

    # A reference to a file that is not there is a worse problem than a stale
    # cache, and this pass is the only thing that resolves every asset path on
    # every page, so it is the right place to notice.
    if missing:
        for x in missing[:8]:
            print(f"  MISSING  {x}")
        print(f"  {len(missing)} reference(s) point at no file")
        return 1

    if check_only:
        if stale:
            for x in stale[:8]:
                print(f"  STALE  {x}")
            print(f"\n  {len(stale)} reference(s) out of date across {len(pages)} pages.")
            print("  Run: python ops/fingerprint_assets.py")
            return 1
        print(f"  {refs} asset reference(s) across {len(pages)} pages, all current")
        return 0

    print(f"  {refs} asset reference(s) across {len(pages)} pages")
    print(f"  {changed} page(s) rewritten, {len(stale)} reference(s) updated")

    # The service worker precaches by exact hashed URL, so any run that moves
    # a hash leaves sw.js pointing at an address no page requests any more and
    # an offline visitor takes a cache miss on the real stylesheet. That is not
    # hypothetical: it shipped to CI on 2026-08-31 because this was run on its
    # own after a CSS edit. Documenting the order was not enough three times
    # running, so the order is code now.
    import build_pwa
    build_pwa.main()
    for path, h in sorted(_cache.items()):
        print(f"    {os.path.relpath(path, SITE).replace(os.sep, '/'):28} {h}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--check" in sys.argv))
