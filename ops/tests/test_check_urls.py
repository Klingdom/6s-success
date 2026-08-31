"""Prove ops/check_urls.py can return every verdict, not just "ok".

The sitemap currently resolves completely, so a working resolver and a broken
one produce identical output. This drives the resolver directly with cases it
must get right, including the one that started all this: a directory with no
index.html, which nginx answers with 403 Forbidden rather than 404.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import check_urls as C                                        # noqa: E402

ROOT = C.ROOT
SITE = C.SITE


def main() -> int:
    bad = []

    def want(path, verdict, why):
        got, detail = C.resolve(path)
        if got != verdict:
            bad.append("%s should be %s, got %s (%s)  -- %s"
                       % (path, verdict, got, detail, why))

    # Real pages, by each of the three try_files steps in turn.
    want("/", "ok", "the root is served by index.html")
    want("/index.html", "ok", "a file that exists")
    want("/resources", "ok", "extensionless, resolved by $uri.html")
    want("/zones/", "ok", "a directory that does have an index.html")

    # The defect this tool exists for.
    want("/downloads/", "directory-403",
         "a directory with no index.html answers 403, not 404")

    # Plainly absent.
    want("/no-such-page-at-all", "missing", "nothing on disk")
    want("/nope/nothing/here.html", "missing", "nothing on disk")

    # Paths nginx answers itself must not be reported as missing files.
    want("/subscribe", "ok", "proxied to Listmonk, no file on disk")
    want("/rooms/", "ok", "redirected in the nginx config")

    # A URL is parsed to its path whether it is absolute or relative.
    if C.path_of("https://6s-success.com/book.html") != "/book.html":
        bad.append("path_of did not strip the scheme and host")
    if C.path_of("/book.html") != "/book.html":
        bad.append("path_of mangled an already-relative path")

    # An empty or unreadable sitemap must fail, never pass quietly. This is the
    # "could not look reported as found nothing" failure that has cost this
    # project repeatedly.
    real = C.SITEMAP
    try:
        C.SITEMAP = os.path.join(ROOT, "build", "_no_such_sitemap.xml")
        if C.check_static() == 0:
            bad.append("a missing sitemap was reported as a pass")
    finally:
        C.SITEMAP = real

    for b in bad:
        print("  FAIL " + b)
    if not bad:
        print("  ok  resolver handles files, extensionless URLs, directories "
              "with and without an index, proxied paths, and a missing sitemap")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
