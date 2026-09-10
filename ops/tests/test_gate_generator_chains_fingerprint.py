#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_generator_chains_fingerprint() catches a page
generator that chains build_avif.wire() without also chaining
fingerprint_assets.main(), the exact shape that let six generators
(build_articles.py, build_deck_gallery.py, build_resources.py,
build_standards_page.py, build_zone_index.py, build_zone_pages.py) silently
strip the ?v= cache-busting hash off every page on the site when run
standalone, found and fixed 2026-09-09.

Widened 2026-09-10: ops/build_sample_html.py hit the same gap through a
different door. It never calls build_avif.wire() (it degrades every <img>
to text, wiring no pictures at all), so the original trigger could not see
it, yet it writes a literal, unversioned href to fonts.css and book.css and
never chained the fingerprinter either. Reproduced live: a standalone run
diffed against the committed, shipped file (the site's primary lead magnet)
differed only in the missing ?v= on both links. Fixed the same way as the
six before it, and the gate gained a second, direct trigger: any literal
href to an unversioned .css or .js under assets/. The cases below prove both
triggers independently and together.

Run:  python ops/tests/test_gate_generator_chains_fingerprint.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

MISSING = (
    "import build_avif\n"
    "build_avif.wire()\n"
)

PRESENT = (
    "import build_avif\n"
    "build_avif.wire()\n"
    "import fingerprint_assets\n"
    "fingerprint_assets.main(False)\n"
)

NOT_APPLICABLE = (
    "print('a generator that never touches AVIF or fingerprints')\n"
)

# The build_sample_html.py shape: no build_avif.wire() call anywhere (it
# wires no pictures), just a bare href literal to a fingerprintable asset.
HREF_MISSING = (
    'html = html.replace(\'href="assets/fonts.css"\', '
    '\'href="../assets/css/fonts.css"\')\n'
)

HREF_PRESENT = HREF_MISSING + (
    "import fingerprint_assets\n"
    "fingerprint_assets.main(False)\n"
)

# Already-fingerprinted literal (a hardcoded ?v= hash baked into the
# template, the build_kitchen_deck_page.py shape) must not trigger the new
# href check, since the string does not match "unversioned".
HREF_ALREADY_VERSIONED = (
    '"<link rel=\\"stylesheet\\" href=\\"assets/css/site.css?v=326a1059ac\\">"\n'
)


def _run(files: dict):
    """files: {filename: source}. Writes them under a fake ops/, points
    preflight.ROOT at the fake tree, runs the gate, restores real ROOT."""
    tmp = tempfile.mkdtemp()
    try:
        ops_dir = os.path.join(tmp, "ops")
        os.makedirs(ops_dir)
        for name, src in files.items():
            io.open(os.path.join(ops_dir, name), "w", encoding="utf-8").write(src)
        old_root = preflight.ROOT
        preflight.ROOT = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_generator_chains_fingerprint()
            return list(preflight.FAIL)
        finally:
            preflight.ROOT = old_root
    finally:
        shutil.rmtree(tmp)


def test_missing_fingerprint_fails():
    fails = _run({"build_missing.py": MISSING})
    assert fails, "a generator chaining build_avif.wire() with no " \
        "fingerprint_assets.main() should fail, and did not"
    assert "build_missing.py" in fails[0][1], \
        "the failure should name the offending file: %r" % (fails[0],)


def test_present_fingerprint_passes():
    fails = _run({"build_present.py": PRESENT})
    assert not fails, "a generator that chains both should pass: %r" % (fails,)


def test_not_applicable_passes():
    fails = _run({"build_other.py": NOT_APPLICABLE})
    assert not fails, "a generator that touches neither should not be " \
        "flagged: %r" % (fails,)


def test_mixed_only_flags_the_offender():
    fails = _run({"build_good.py": PRESENT, "build_bad.py": MISSING,
                  "build_neutral.py": NOT_APPLICABLE})
    names = [m for _, m in fails]
    assert len(fails) == 1, "exactly one of the three files is wrong: %r" % (fails,)
    assert "build_bad.py" in names[0]
    assert "build_good.py" not in names[0]


def test_non_build_file_ignored():
    """Only build_*.py is in scope; a same-shape helper module should not be
    scanned, since it is not one of the page generators this gate protects."""
    fails = _run({"wire_something.py": MISSING})
    assert not fails, "a non build_*.py file should never be scanned: %r" % (fails,)


def test_href_trigger_missing_fingerprint_fails():
    """The build_sample_html.py shape: no build_avif.wire() call, just a
    bare href literal to a fingerprintable asset."""
    fails = _run({"build_missing.py": HREF_MISSING})
    assert fails, "a generator with a literal unversioned asset href and " \
        "no fingerprint_assets.main() should fail, and did not"
    assert "build_missing.py" in fails[0][1]
    assert "literal unversioned asset href" in fails[0][1]


def test_href_trigger_present_fingerprint_passes():
    fails = _run({"build_present.py": HREF_PRESENT})
    assert not fails, "a generator with the href but also the " \
        "fingerprint chain should pass: %r" % (fails,)


def test_already_versioned_href_not_flagged():
    """A hardcoded href that already carries a ?v= hash (the
    build_kitchen_deck_page.py shape) is a different, already-fixed
    problem (drift against a stale baked-in hash, caught by
    gate_generator_ownership instead) and must not trip this trigger."""
    fails = _run({"build_baked.py": HREF_ALREADY_VERSIONED})
    assert not fails, "an already-versioned literal href should not be " \
        "flagged by the unversioned-href trigger: %r" % (fails,)


def test_real_repository_is_clean():
    """The actual fix: run the gate against the real, committed ops/
    directory (not a synthetic fixture) and confirm every generator that
    chains build_avif.wire() now also chains fingerprint_assets.main()."""
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_generator_chains_fingerprint()
    fails = list(preflight.FAIL)
    assert not fails, "the real repository should be clean: %r" % (fails,)


TESTS = [test_missing_fingerprint_fails, test_present_fingerprint_passes,
         test_not_applicable_passes, test_mixed_only_flags_the_offender,
         test_non_build_file_ignored, test_href_trigger_missing_fingerprint_fails,
         test_href_trigger_present_fingerprint_passes,
         test_already_versioned_href_not_flagged, test_real_repository_is_clean]


def main():
    n = 0
    for t in TESTS:
        t()
        n += 1
    print("  %d of %d cases pass" % (n, len(TESTS)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
