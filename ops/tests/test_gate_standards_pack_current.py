#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_standards_pack_current() catches
site/downloads/6S-Standards-Pack.html going stale against
build/6S-Standards-Pack.html.

ops/build_standards.py writes the build/ copy, and gate_generator_ownership
already proves that copy is correctly derived from content.json. Nothing
copies it into site/downloads/6S-Standards-Pack.html, the path a real
visitor's browser actually fetches (linked from book.html and
standards.html): that copy is a manual step. gate_downloads_noindex already
named this exact gap for one failure mode (noindex/canonical tags going
missing on the shipped copy) and said outright it "cannot do itself, only
catch if skipped." This gate closes the general case: any future content fix
that reruns the generator but skips the copy now fails preflight by name
instead of silently shipping a stale download.

Run:  python ops/tests/test_gate_standards_pack_current.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _run(build_html, live_html, omit_build=False, omit_live=False):
    tmp = tempfile.mkdtemp()
    build_dir = os.path.join(tmp, "build")
    downloads_dir = os.path.join(tmp, "site", "downloads")
    os.makedirs(build_dir, exist_ok=True)
    os.makedirs(downloads_dir, exist_ok=True)
    if not omit_build:
        io.open(os.path.join(build_dir, "6S-Standards-Pack.html"),
                "w", encoding="utf-8").write(build_html)
    if not omit_live:
        io.open(os.path.join(downloads_dir, "6S-Standards-Pack.html"),
                "w", encoding="utf-8").write(live_html)
    old_root, old_site = preflight.ROOT, preflight.SITE
    preflight.ROOT = tmp
    preflight.SITE = os.path.join(tmp, "site")
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_standards_pack_current()
        return list(preflight.FAIL)
    finally:
        preflight.ROOT, preflight.SITE = old_root, old_site
        shutil.rmtree(tmp)


GOOD = "<html><body>Sort. Straighten. Shine. Safety. Standardize. Sustain.</body></html>"
STALE = "<html><body>Sort. Straighten. Shine. Standardize. Sustain.</body></html>"


def main() -> int:
    fails = []

    # 1. Identical content: no failure.
    r = _run(GOOD, GOOD)
    if r:
        fails.append("identical files wrongly flagged: %r" % (r,))

    # 2. The real-world regression: build/ moved on, site/downloads/ did not.
    r = _run(GOOD, STALE)
    if not r or not any("standards-pack-current" in m or "does not match" in m
                         for _, m in r):
        fails.append("stale live copy not caught: %r" % (r,))

    # 3. Neither file present (fresh checkout with build/ gitignored,
    #    or the page retired): nothing to check, no failure.
    r = _run(GOOD, GOOD, omit_build=True, omit_live=True)
    if r:
        fails.append("both files absent wrongly flagged: %r" % (r,))

    # 4. Only build/ present, site/downloads/ missing: nothing to compare
    #    against, no failure (a different gate's job, not this one's).
    r = _run(GOOD, GOOD, omit_live=True)
    if r:
        fails.append("missing live copy alone wrongly flagged here: %r" % (r,))

    # 5. The real, committed pair: clean.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_standards_pack_current()
    if preflight.FAIL:
        fails.append("the real committed files failed: %r" % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_standards_pack_current, 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
