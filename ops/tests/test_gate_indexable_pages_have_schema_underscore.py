"""Prove gate_indexable_pages_have_schema() ignores throwaway probe/wrapper
files an interactive test leaves in site/, instead of failing on them.

Found live 2026-09-23, twice: a full preflight.py run globs site/*.html for
this gate while, in the same container, a headless-Chromium interactive
test (test_site_js_no_runtime_error.py, then test_thanks_sku_branching.py)
was mid-write on its own _*_probe_N.html/_*_wrapper_N.html copy. Those
files carry no schema by design (they are not real pages) and were gone
again by the time anyone looked, so the failure named a file that was
never committed and no longer existed, costing a rerun both times. Every
interactive test in ops/tests/ uses a leading underscore for this exact
kind of file, and no committed site page ever has, so excluding that
prefix removes the race instead of hoping two processes never overlap
again.

This still proves the gate's real job is intact: a normal page with no
schema and no noindex is caught by name.
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402

WITH_SCHEMA = ("<html><head><title>x</title>"
               '<script type="application/ld+json">{}</script>'
               "</head><body>x</body></html>")
NO_SCHEMA = "<html><head><title>x</title></head><body>x</body></html>"
NOINDEX_NO_SCHEMA = ('<html><head><title>x</title>'
                      '<meta name="robots" content="noindex, follow">'
                      "</head><body>x</body></html>")


def _run_gate(files):
    """Write `files` (name -> html) into a throwaway site dir, point
    preflight.SITE at it, run the gate, restore state, return the FAIL
    entries recorded during this one call."""
    import tempfile
    import shutil
    tmp_site = tempfile.mkdtemp(prefix="6s-schema-gate-fixture-")
    try:
        for name, body in files.items():
            io.open(os.path.join(tmp_site, name), "w", encoding="utf-8").write(body)
        real_site = preflight.SITE
        preflight.SITE = tmp_site
        before = len(preflight.FAIL)
        try:
            preflight.gate_indexable_pages_have_schema()
        finally:
            preflight.SITE = real_site
        result = list(preflight.FAIL[before:])
        del preflight.FAIL[before:]
        return result
    finally:
        shutil.rmtree(tmp_site, ignore_errors=True)


def main() -> int:
    bad = []

    # A real page with no schema and no noindex must still fail. Proves the
    # underscore exclusion did not gut the gate's actual job.
    fails = _run_gate({"consulting.html": NO_SCHEMA})
    if not fails:
        bad.append("a real indexable page with no schema was NOT caught; "
                    "the underscore exclusion may have gutted the gate")
    elif "consulting.html" not in fails[0][1]:
        bad.append("gate fired but did not name consulting.html: %r" % (fails,))

    # A committed-looking page WITH schema, alongside a throwaway
    # underscore-prefixed probe file with none: only the real page's
    # presence should be evaluated, and the stray file must never appear
    # in the failure message.
    fails = _run_gate({
        "index.html": WITH_SCHEMA,
        "_thanks_wrapper_0.html": NO_SCHEMA,
        "_site_js_probe_3.html": NO_SCHEMA,
    })
    if fails:
        bad.append("underscore-prefixed throwaway file(s) triggered a "
                    "failure that should have been excluded: %r" % (fails,))

    # noindex pages are already exempt; confirm that still holds alongside
    # an underscore file, so the two exclusions do not interact badly.
    fails = _run_gate({
        "thanks.html": NOINDEX_NO_SCHEMA,
        "_thanks_probe_0.html": NO_SCHEMA,
    })
    if fails:
        bad.append("noindex page plus a throwaway file wrongly failed: %r"
                    % (fails,))

    if bad:
        print("  %d problem(s):" % len(bad))
        for b in bad:
            print("    - %s" % b)
        return 1
    print("  gate_indexable_pages_have_schema still catches a real "
          "schema-less indexable page, and no longer fails on throwaway "
          "underscore-prefixed probe/wrapper files interactive tests leave "
          "in site/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
