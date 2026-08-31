"""Prove ops/audit_pages.py reports the two link faults it used to miss.

The site audits clean, so a working link check and a broken one produce the
same output. Two real holes were fixed on 2026-08-31:

  root-relative links were skipped entirely, because "/" sat in the same tuple
  as http, #, mailto and tel;

  and a link to a directory with no index.html passed as good, because
  os.path.exists() answers True for a directory, while the server answers such
  a URL with 403 Forbidden.

This writes a page containing both faults, plus links that must stay clean, and
requires the audit to tell them apart.
"""
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(ROOT, "site")
TOOL = os.path.join(ROOT, "ops", "audit_pages.py")
FIXTURE = os.path.join(SITE, "_audit_link_fixture.html")

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Temporary fixture for the link audit test</title>
<meta name="description" content="Written and deleted by ops/tests/test_audit_links.py to prove the link audit can report a fault.">
<link rel="canonical" href="https://6s-success.com/_audit_link_fixture.html">
</head><body><main><h1>Fixture</h1>
<a href="/no-such-root-relative-page.html">must be reported: root relative, missing</a>
<a href="nope-relative-page.html">must be reported: relative, missing</a>
<a href="/downloads/">must be reported as 403: directory with no index</a>
<a href="/zones/">must stay clean: directory with an index</a>
<a href="/book.html">must stay clean: a real page, root relative</a>
<a href="book.html">must stay clean: a real page, relative</a>
</main></body></html>
"""


def counts(out: str) -> dict:
    """check name -> total, from the audit's summary table."""
    got = {}
    for line in out.splitlines():
        m = re.match(r"\s+([a-z0-9-]+)\s+(\d+)\s+\d+\s+", line)
        if m:
            got[m.group(1)] = int(m.group(2))
    return got


def main() -> int:
    if not os.path.exists(TOOL):
        print("  FAIL ops/audit_pages.py is missing")
        return 1

    io.open(FIXTURE, "w", encoding="utf-8", newline="").write(PAGE)
    try:
        r = subprocess.run([sys.executable, TOOL], cwd=ROOT, capture_output=True,
                           text=True, timeout=600,
                           env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        out = (r.stdout or "") + (r.stderr or "")
    finally:
        if os.path.exists(FIXTURE):
            os.remove(FIXTURE)

    got = counts(out)
    bad = []
    if got.get("link-broken", 0) < 2:
        bad.append("two missing links should be reported as link-broken, got %r"
                   % got.get("link-broken"))
    if got.get("link-403", 0) < 1:
        bad.append("a link to a directory with no index.html should be reported "
                   "as link-403, got %r" % got.get("link-403"))

    for b in bad:
        print("  FAIL " + b)
    if bad:
        print(out[:1500])
        return 1
    print("  ok  audit reports missing links and links to indexless directories")
    return 0


if __name__ == "__main__":
    sys.exit(main())
