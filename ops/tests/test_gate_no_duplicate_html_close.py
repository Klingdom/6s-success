#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_no_duplicate_html_close() catches the real
defect found 2026-09-14 in site/resources.html: its generator
(ops/build_resources.py) built the page footer by slicing about.html from
<footer> to end-of-file, which already carried about.html's own closing
</body></html>, then appended the template's own copy of both after it.
Every rebuild silently shipped a page with two </html> tags; resources.html
was the only page on the whole site with the shape, found by counting
rather than by rendering (browsers ignore markup after a closed </html>).

Run:  python ops/tests/test_gate_no_duplicate_html_close.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    # 1. The exact pre-fix shape: a footer fragment that already carries a
    #    full closing pair, with the template appending its own after it.
    doubled = ("<!doctype html><html><head></head><body>"
               "<p>content</p><footer>f</footer></body></html>"
               "</body></html>")
    bad = preflight.check_no_duplicate_html_close([("site/resources.html", doubled)])
    if bad != ["site/resources.html"]:
        fails.append(f"doubled close not caught: {bad}")

    # 2. The fixed shape: exactly one close, must pass clean.
    single = ("<!doctype html><html><head></head><body>"
              "<p>content</p><footer>f</footer></body></html>")
    bad = preflight.check_no_duplicate_html_close([("site/resources.html", single)])
    if bad:
        fails.append(f"single close wrongly flagged: {bad}")

    # 3. A second, unrelated page must not be implicated by the first's defect.
    bad = preflight.check_no_duplicate_html_close([
        ("site/resources.html", doubled),
        ("site/about.html", single),
    ])
    if bad != ["site/resources.html"]:
        fails.append(f"unrelated clean page wrongly named, or the bad one missed: {bad}")

    # 4. The real, currently-committed site must be clean after the fix.
    import glob
    real_bad = []
    for f in glob.glob(os.path.join(ROOT, "site", "**", "*.html"), recursive=True):
        rel = os.path.relpath(f, ROOT)
        text = open(f, encoding="utf-8", errors="replace").read()
        real_bad += preflight.check_no_duplicate_html_close([(rel, text)])
    if real_bad:
        fails.append(f"real committed site still has doubled closes: {real_bad}")

    if fails:
        print(f"FAIL: {len(fails)} of 4 cases failed")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 4 of 4 cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
