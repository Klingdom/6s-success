#!/usr/bin/env python3
"""
Prove wire_breadcrumbs.py's own reported count means "changed", not "looked
at and qualified".

Found 2026-09-07: main() incremented a single `done` counter for every
article whose breadcrumb trail had at least two steps, whether or not the
computed markup actually differed from what was already on disk, then
printed it under an action verb: "marked up N article breadcrumb(s)" for a
real run, "would mark up N" for --check. Against the live tree, where all 27
eligible articles already carry correct, current BreadcrumbList JSON-LD, this
printed "would mark up 27" and "marked up 27" on every run, including runs
that changed zero bytes. Multiple nightly cycles read that line and logged
wire_breadcrumbs.py as "still unrun" or "a real, unapplied SEO gap" purely
off this message; only a cycle that ran it and diffed the working tree ever
caught that the message was vacuous. Same class of defect as
ops/shrink_sample.py's page-count assert, fixed 2026-09-06: a check that
cannot distinguish "did work" from "already correct" is not reporting the
thing its own words claim.

Fixed by splitting the single counter into `changed` (bytes actually
written, or would be under --check) and `already` (qualified, computed
markup byte-identical to what is on disk), and using "changed"/"would
change" instead of "marked up"/"would mark up".

Builds two synthetic article fixtures in a temp site tree rather than
touching the real one: one with no CRUMBLD marker at all (must count as
changed), one with the exact marker main() would produce (must count as
already-correct, zero bytes touched).

Run:  python ops/tests/test_wire_breadcrumbs.py
"""
from __future__ import annotations

import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import wire_breadcrumbs as wb                                 # noqa: E402

PAGE_TEMPLATE = """<!doctype html>
<html><head><title>t</title></head>
<body>
<nav class="crumb"><a href="../index.html">Home</a> / <a href="index.html">Articles</a> / Sample Article</nav>
{extra}
</body></html>
"""


def build_site(tmp: str) -> str:
    site = os.path.join(tmp, "site")
    articles = os.path.join(site, "articles")
    os.makedirs(articles)
    # A stray index.html articles must skip regardless of shape.
    io.open(os.path.join(articles, "index.html"), "w", encoding="utf-8").write(
        PAGE_TEMPLATE.format(extra=""))
    return site


def run_main(check: bool) -> str:
    argv = sys.argv[:]
    sys.argv = ["wire_breadcrumbs.py"] + (["--check"] if check else [])
    out = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = out
    try:
        wb.main()
    finally:
        sys.stdout = old_stdout
        sys.argv = argv
    return out.getvalue()


def main() -> int:
    tmp = tempfile.mkdtemp()
    real_site = wb.SITE
    failures = []
    try:
        site = build_site(tmp)
        wb.SITE = site
        articles = os.path.join(site, "articles")

        # File A: no marker yet. main() must write it and count it as changed.
        fresh = os.path.join(articles, "unmarked.html")
        io.open(fresh, "w", encoding="utf-8").write(PAGE_TEMPLATE.format(extra=""))

        out = run_main(check=True)
        if "would change 1 article" not in out or "0 already correct" not in out:
            failures.append(f"--check on a fresh page misreported: {out!r}")

        out = run_main(check=False)
        if "changed 1 article" not in out:
            failures.append(f"real run on a fresh page misreported: {out!r}")
        after_first_run = io.open(fresh, encoding="utf-8").read()

        # File A again, now already correct. A second run must write zero
        # bytes and report it as already-correct, not as changed.
        out = run_main(check=False)
        if "changed 0 article" not in out or "1 already correct" not in out:
            failures.append(
                "the regression: a second run on an already-correct page "
                f"still reported it as changed: {out!r}")
        if io.open(fresh, encoding="utf-8").read() != after_first_run:
            failures.append("a no-op run rewrote a byte it did not need to")

        # --check on that same already-correct page must predict zero change,
        # matching what the real run just proved.
        out = run_main(check=True)
        if "would change 0 article" not in out or "1 already correct" not in out:
            failures.append(
                f"--check disagreed with the real run's own outcome: {out!r}")

    finally:
        wb.SITE = real_site
        shutil.rmtree(tmp, ignore_errors=True)

    if failures:
        print("FAIL")
        for f in failures:
            print(" -", f)
        return 1
    print("ok: wire_breadcrumbs.py's changed/already counts match reality "
          "(6 assertions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
