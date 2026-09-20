#!/usr/bin/env python3
"""
Refuse a commit that changes a page without re-deriving the sitemap.

WHY THIS EXISTS
---------------
On 2026-09-20 the "Publish site image" workflow went red twice, hours apart,
for the same reason and from two different sessions: pages were committed
while site/sitemap.xml and ops/sitemap-content-hashes.json still described the
previous tree, so gate_generator_ownership in CI found them stale.

Both were discovered by CI, minutes later, on a shared runner, behind a full
suite. Nothing ran at the moment the mistake entered history. That is the
identical gap the build-id control in .githooks/pre-commit was written to
close, and this is the same control applied to the other generated file that
every page edit invalidates.

It is deliberately a CHECK and not a fix. Regenerating the sitemap silently
inside a hook would date pages behind the author's back, and lastmod is a
claim we make to search engines, not a detail to automate away unnoticed.

    python ops/check_sitemap_current.py

Exit 0 when the recorded hashes match the working tree, 1 when they do not,
naming the pages and the command that fixes it.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))


def main() -> int:
    # Imported rather than reimplemented, so there is exactly one definition
    # of "has this page's content changed". A second copy here would drift
    # from build_seo.py and this check would start disagreeing with the gate
    # it exists to pre-empt.
    import build_seo as B

    entries = []
    for fn in B.INDEXABLE:
        entries.append((B.BASE + B.PAGES[fn]["path"],
                        os.path.join(B.SITE, fn)))
    entries += [(url, fp) for url, _p, _c, fp in B.scan_extra_pages()]

    recorded = B._load_content_hashes()
    if not recorded:
        print("  sitemap hashes file is missing or empty, so this could not "
              "be checked. Unchecked is not current.")
        return 1

    stale, unknown = [], []
    for url, fp in entries:
        now = B._content_hash(fp)
        if url not in recorded:
            unknown.append(url)
        elif recorded[url] != now:
            stale.append(url)

    if not stale and not unknown:
        print("  sitemap: %d page(s) match their recorded content hash"
              % len(entries))
        return 0

    if stale:
        print("  %d page(s) changed since the sitemap was last built:"
              % len(stale))
        for u in stale[:8]:
            print("     %s" % u)
        if len(stale) > 8:
            print("     ... and %d more" % (len(stale) - 8))
    if unknown:
        print("  %d page(s) are not in the sitemap hash record at all:"
              % len(unknown))
        for u in unknown[:8]:
            print("     %s" % u)
    print("  Run: python ops/build_seo.py && git add site/sitemap.xml "
          "ops/sitemap-content-hashes.json")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
