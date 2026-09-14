#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_head_scripts_non_blocking() catches a real
render-blocking regression: a <script src=...> sitting in <head> with
neither defer nor async, which stops the parser until it has fetched and
run.

Found 2026-09-14: GOALS.md lists "page speed" as unblocked O1 work, but
nothing in ops/NIGHTLY-LOG.md had ever measured it beyond one incidental
@font-face fix. The real site already carries zero blocking head scripts
(all real JS deferred or placed at the end of body), but nothing protected
that from regressing. This test proves the gate can both fail and pass.

Run:  python ops/tests/test_gate_head_scripts_non_blocking.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

CLEAN = (
    "<html><head><title>x</title>"
    '<script defer src="assets/js/measure.js"></script>'
    '<script async src="/stats/script.js"></script>'
    '<script type="application/ld+json">{"a":1}</script>'
    "</head><body>hi"
    '<script src="assets/js/site.js"></script>'
    "</body></html>"
)

BLOCKING = (
    "<html><head><title>x</title>"
    '<script src="assets/js/big-blob.js"></script>'
    "</head><body>hi</body></html>"
)

INLINE_HEAD_SCRIPT = (
    "<html><head><title>x</title>"
    "<script>document.documentElement.className='js';</script>"
    "</head><body>hi</body></html>"
)


def _run(pages: dict):
    tmp = tempfile.mkdtemp()
    for name, body in pages.items():
        io.open(os.path.join(tmp, name), "w", encoding="utf-8").write(body)
    old_site = preflight.SITE
    preflight.SITE = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_head_scripts_non_blocking()
        return list(preflight.FAIL)
    finally:
        preflight.SITE = old_site
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. Deferred/async/JSON-LD head scripts and a bare body script: clean.
    r = _run({"clean.html": CLEAN})
    if r:
        fails.append("clean page wrongly flagged: %r" % (r,))

    # 2. A real blocking head script: caught by name, with the src named.
    r = _run({"blocking.html": BLOCKING})
    if not r or "blocking.html" not in r[0][1] or "big-blob.js" not in r[0][1]:
        fails.append("blocking head script not caught: %r" % (r,))

    # 3. An inline <script> with no src= in head never blocks a fetch: not a
    #    finding here (a separate concern from this gate).
    r = _run({"inline.html": INLINE_HEAD_SCRIPT})
    if r:
        fails.append("inline head script (no src) wrongly flagged: %r" % (r,))

    # 4. The real, committed site: clean on every real page today.
    real_pages = preflight.all_pages()
    if len(real_pages) < 100:
        print("  (skipped: fewer than 100 real pages found on disk)")
    else:
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_head_scripts_non_blocking()
        if preflight.FAIL:
            fails.append("real committed pages failed: %r" % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_head_scripts_non_blocking, 4/4 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
