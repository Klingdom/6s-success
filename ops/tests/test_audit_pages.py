"""Prove ops/audit_pages.py's pages() ignores two other tools' own scratch
shells, and nothing else that happens to start with an underscore.

audit_visual.py writes site/<dir>/_visual_probe.html beside the page it is
measuring (a bare <iframe> shell with no title, lang, viewport or canonical
by design) and removes it when done. test_audit_catalog.py writes
site/_audit_catalog_fixture_<pid>.html the same way (a title but no
viewport, description, canonical, heading or analytics tag), proved live
while writing this fix: caught by hand mid-run, in the real working tree,
while a concurrent preflight pass had that test in flight. A run whose
window overlaps either write can catch the shell mid-existence and report
it as a real page missing every one of those things, a finding that
self-resolves the moment the writer's own cleanup runs. This is the exact,
self-contradicting shape a same-day cycle logged and flagged for root-cause:
one preflight run failed the "pages" gate with real, non-duplicate
findings, and every immediate rerun on the identical, unchanged tree came
back clean.

The fix is deliberately narrow, by exact filename or prefix, not "any
leading underscore": test_audit_links.py plants its own underscore-prefixed
_audit_link_fixture.html specifically so this module can be proven to scan
and flag it, a fixture the first, broader version of this fix silently made
invisible, breaking that test's own reason to exist. This file proves all
three: both scratch shells are excluded, and an underscore-prefixed fixture
shaped like a real page is not.
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import audit_pages as A                                       # noqa: E402

SITE = A.SITE

PROBE_SHELL = ('<!doctype html><meta charset="utf-8">'
               '<style>html,body{margin:0}</style>'
               '<iframe id="f" src="index.html"></iframe>')

CATALOG_FIXTURE_SHELL = ('<!doctype html><html lang="en"><head>'
                          '<meta charset="utf-8"><title>Temporary fixture'
                          '</title></head><body><main>'
                          '<a href="https://buy.stripe.com/notARealSlug">'
                          'Buy</a></main></body></html>')

REAL_SHAPED_FIXTURE = ('<!doctype html><html lang="en"><head>'
                        '<meta charset="utf-8">'
                        '<meta name="viewport" content="width=device-width">'
                        '<title>Not a real page, but page-shaped</title>'
                        '<meta name="description" content="Long enough to '
                        'clear the short-description floor this file checks '
                        'for, on purpose, so this fixture proves nothing '
                        'else trips.">'
                        '<link rel="canonical" '
                        'href="https://6s-success.com/_stand-in.html">'
                        '</head><body><main><h1>Fixture</h1></main>'
                        '</body></html>')


class Planted:
    """Write a file under site/, and always clean it up."""

    def __init__(self, rel: str, text: str):
        self.path = os.path.join(SITE, rel.replace("/", os.sep))
        self.text = text

    def __enter__(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        io.open(self.path, "w", encoding="utf-8", newline="").write(self.text)
        return self

    def __exit__(self, *a):
        if os.path.exists(self.path):
            os.remove(self.path)


def main() -> int:
    bad = []

    # The exact real-world filename, in a real site/ subdirectory: excluded.
    with Planted("zones/_visual_probe.html", PROBE_SHELL) as f:
        if f.path in A.pages():
            bad.append("pages() included a stray _visual_probe.html, the "
                       "exact file audit_visual.py writes and removes mid-run")

        findings = A.check(f.path, PROBE_SHELL)
        if not findings:
            bad.append("check() on the bare probe shell found nothing; the "
                       "test fixture no longer proves what a real probe "
                       "would trigger if pages() ever regresses")

    # The other real-world shape, PID-suffixed: excluded by prefix.
    with Planted("_audit_catalog_fixture_12345.html", CATALOG_FIXTURE_SHELL) as f:
        if f.path in A.pages():
            bad.append("pages() included a stray _audit_catalog_fixture_*, "
                       "the exact shape test_audit_catalog.py writes and "
                       "removes mid-run")

        findings = A.check(f.path, CATALOG_FIXTURE_SHELL)
        if not findings:
            bad.append("check() on the catalog-fixture shell found nothing; "
                       "the test fixture no longer proves what a real one "
                       "would trigger if pages() ever regresses")

    # A different underscore-prefixed name, page-shaped: must stay included.
    # This is what test_audit_links.py's own _audit_link_fixture.html relies
    # on; excluding every underscore name (the first version of this fix)
    # would have silently broken that test's whole reason to exist.
    with Planted("_audit_link_fixture.html", REAL_SHAPED_FIXTURE) as f:
        if f.path not in A.pages():
            bad.append("pages() excluded an underscore-prefixed fixture "
                       "that is not one of the two known scratch shells; "
                       "this would silently disable test_audit_links.py's "
                       "own check")

    # A real page in the same directory as the excluded probe must still be
    # picked up: the fix excludes specific filenames, not a directory.
    real_zone_pages = [p for p in A.pages() if "/zones/" in p.replace("\\", "/")]
    if not real_zone_pages:
        bad.append("pages() found no real zone pages at all; the fix may "
                   "have excluded too much")

    for b in bad:
        print("  FAIL " + b)
    if not bad:
        print("  ok  pages() excludes only the two known scratch shells, "
              "and still scans every other underscore-prefixed fixture and "
              "every real page")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
