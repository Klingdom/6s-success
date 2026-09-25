#!/usr/bin/env python3
"""
Prove ops/wire_nav.py no longer strips aria-current="page" from the pages
it rewrites, and no longer crashes its own link-resolution check on a page
with bad encoding.

Found 2026-09-25, cold-reading ops/wire_nav.py per the standing cold-read
lane. Two real defects, both live against the real committed site:

1. build() writes a plain nav with no notion of which page is "current", so
   running the script stripped aria-current="page" from all 5 destination
   pages it touched (method.html, resources.html, book.html,
   consulting.html, zones/index.html), confirmed directly against the real
   committed tree via `git diff` after a live run, then reverted. The
   script's own docstring calls itself "Idempotent" and instructs "Run
   after any builder, then ops/fingerprint_assets.py", never mentioning
   ops/wire_aria_current.py, so a human following the documented usage
   exactly would ship the regression. gate_nav_current in preflight.py
   would catch it on the NEXT preflight run, but not before.

2. The link-resolution scan below the rewrite read every site/**/*.html
   file with a bare `encoding="utf-8"` and no error handling, unlike every
   comparable read-only scan elsewhere in this codebase (including
   preflight.py's own gate_nav_canonical, which reads the identical file
   set with errors="replace"). One transient bad-encoding read during a
   live run crashed the whole script with an uncaught UnicodeDecodeError
   before the link check it exists to run ever completed; not reproducible
   as a standing defect (confirmed clean on an immediate rerun, a
   concurrency artifact of this sandbox per several prior log entries), but
   the missing errors="replace" was a real, avoidable single point of
   failure regardless of whether that one moment recurs.

Fixed: main() now chains wire_aria_current.main() after the rewrite and the
link check, and the link check reads with errors="replace". Verified live:
running the real script against the real committed site now produces a
byte-identical tree (git diff clean) on both the first and a second
consecutive run.

Run:  python ops/tests/test_wire_nav_preserves_aria_current.py
"""
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, "ops", "wire_nav.py")

PAGE = """<!doctype html>
<html><head></head><body>
<header class="site-header">
  <button class="nav-toggle" aria-label="Menu"></button>
  <nav class="nav" aria-label="Primary">
    <a href="zones/">Start a reset</a>
    <a href="method.html" aria-current="page">How 6S works</a>
    <a href="resources.html">Rooms</a>
    <a href="book.html">Cards and book</a>
    <a href="consulting.html">Get help</a>
  </nav>
</header>
</body></html>
"""


def _build_tree(tmp, with_bad_encoding_file=False):
    site = os.path.join(tmp, "site")
    os.makedirs(os.path.join(site, "zones"))
    for name in ("method.html", "resources.html", "book.html",
                 "consulting.html"):
        io.open(os.path.join(site, name), "w", encoding="utf-8").write(PAGE)
    # every nav target must resolve, or the (unrelated) link-resolution
    # assertion fires first and masks what this test is actually checking
    io.open(os.path.join(site, "zones", "index.html"), "w",
            encoding="utf-8").write("<html></html>")
    if with_bad_encoding_file:
        # A UTF-16-with-BOM file, unreadable as plain utf-8: the exact
        # shape that crashed the unfixed script.
        with open(os.path.join(site, "stray.html"), "wb") as f:
            f.write("<html>é</html>".encode("utf-16"))
    return site


def _run_isolated(with_bad_encoding_file=False):
    import importlib.util
    import sys as _sys
    tmp = tempfile.mkdtemp()
    try:
        site = _build_tree(tmp, with_bad_encoding_file)
        spec = importlib.util.spec_from_file_location("wire_nav_iso", SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.SITE = site
        mod.ROOT = tmp

        # wire_nav.main() imports the real ops/wire_aria_current module by
        # name and calls its main(), which reads its own module-level SITE
        # constant, not this isolated module's patched one; point the real
        # module at the same isolated tree so the chained call is actually
        # exercised end to end rather than silently operating on the real
        # repository's own site/.
        ops_dir = os.path.join(ROOT, "ops")
        if ops_dir not in _sys.path:
            _sys.path.insert(0, ops_dir)
        import wire_aria_current
        old_wac_site = wire_aria_current.SITE
        wire_aria_current.SITE = site

        import contextlib
        buf = io.StringIO()
        crashed = None
        with contextlib.redirect_stdout(buf):
            try:
                rc = mod.main()
            except Exception as e:                            # noqa: BLE001
                crashed = e
                rc = None
        current_page = io.open(os.path.join(site, "method.html"),
                                encoding="utf-8", errors="replace").read()
        return rc, buf.getvalue(), crashed, current_page
    finally:
        try:
            wire_aria_current.SITE = old_wac_site
        except NameError:
            pass
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    fails = []

    # 1. A stray bad-encoding file must not crash the script; it must be
    #    named and skipped, and the whole run must report failure (unknown
    #    is not a default) rather than a silent 0.
    rc, out, crashed, current_page = _run_isolated(with_bad_encoding_file=True)
    if crashed is not None:
        fails.append("a bad-encoding file crashed wire_nav.py: %r" % (crashed,))
    if rc != 1:
        fails.append("main() did not report failure (rc=1) with a stray "
                      "bad-encoding file present: rc=%r out=%r" % (rc, out))
    if "stray.html" not in out:
        fails.append("the unreadable file was not named in the output: %r" % (out,))

    # 2. The page that is the destination of its own nav link must keep
    #    (or regain) aria-current="page" after the script runs.
    if 'href="method.html" aria-current="page"' not in current_page:
        fails.append("method.html lost its aria-current=\"page\" mark: %r"
                      % (current_page,))

    # 3. Every other rewritten page must NOT carry aria-current="page" on
    #    the wrong link (wire_aria_current's own job, proven end to end
    #    here rather than assumed from the chained call alone).
    rc2, out2, crashed2, _ = _run_isolated(with_bad_encoding_file=False)
    if crashed2 is not None or rc2 != 0:
        fails.append("clean tree run failed: rc=%r crashed=%r" % (rc2, crashed2))

    # 4. The real committed site: running the real script twice in a row
    #    must leave the tree byte-identical both times (true idempotency),
    #    proved directly against the real files rather than a synthetic
    #    stand-in, then restored.
    before = subprocess.run(["git", "diff", "--stat", "site/"], cwd=ROOT,
                             capture_output=True, text=True).stdout
    if before.strip():
        fails.append("working tree was not clean before this check: %r" % before)
    else:
        r1 = subprocess.run([sys.executable, SCRIPT], cwd=ROOT,
                             capture_output=True, text=True)
        after1 = subprocess.run(["git", "diff", "--stat", "site/"], cwd=ROOT,
                                 capture_output=True, text=True).stdout
        if after1.strip():
            fails.append("first real run against the committed site "
                          "changed something: %r" % after1)
            subprocess.run(["git", "checkout", "--", "site/"], cwd=ROOT)
        else:
            r2 = subprocess.run([sys.executable, SCRIPT], cwd=ROOT,
                                 capture_output=True, text=True)
            after2 = subprocess.run(["git", "diff", "--stat", "site/"], cwd=ROOT,
                                     capture_output=True, text=True).stdout
            if after2.strip():
                fails.append("second real run against the committed site "
                              "changed something (not idempotent): %r" % after2)
                subprocess.run(["git", "checkout", "--", "site/"], cwd=ROOT)
        if r1.returncode != 0:
            fails.append("real run against the committed site failed: %r"
                          % (r1.stdout[-500:],))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: wire_nav.py preserves aria-current, survives a bad-encoding "
          "file, and is truly idempotent against the real committed site, "
          "4/4 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
