#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_generator_chains_avif() catches a generator
that writes a WebP <picture> source but never chains build_avif.wire().

Found 2026-10-26, this operator cycle, cold-reading ops/build_cleaning_
index.py (on the cold-read ledger after Phil's own 2026-10-26 cleaning-
content-review commit touched it). It claimed to chain "exactly as ops/
build_articles.py does" but never called build_avif.wire() or fingerprint_
assets.main(), so a standalone run (the way an operator actually reaches for
a generator, per CLAUDE.md step 5b) stripped the committed AVIF <source> off
the manual-offer picture; reproduced directly by running it and diffing
against the committed site/how-to-clean-anything.html, invisible inside a
full preflight.py --own run because build_avif.wire() runs globally, later
in the same gens list, for every page including this one. Fixed in
build_cleaning_index.py itself (now chains both calls, two consecutive
standalone runs reproduce the committed file byte for byte) and in this
gate, the sibling gate_generator_chains_fingerprint does not cover (that one
only fires once a generator ALREADY chains build_avif.wire()).

Run:  python ops/tests/test_gate_generator_chains_avif.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _run_gate(ops_files: dict) -> list:
    """ops_files: {relative ops/ filename: source}. Writes into a scratch
    ops/ directory, points preflight.ROOT at it, runs the real gate,
    restores."""
    tmp = tempfile.mkdtemp()
    ops_dir = os.path.join(tmp, "ops")
    os.makedirs(ops_dir)
    for rel, src in ops_files.items():
        io.open(os.path.join(ops_dir, rel), "w", encoding="utf-8").write(src)
    old_root = preflight.ROOT
    try:
        preflight.ROOT = tmp
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_generator_chains_avif()
        return list(preflight.FAIL)
    finally:
        preflight.ROOT = old_root
        shutil.rmtree(tmp)


def test_webp_without_avif_wire_caught():
    fails = _run_gate({
        "build_example_page.py":
            'OUT = \'<source type="image/webp" srcset="a.webp">\'\n'
    })
    assert len(fails) == 1 and fails[0][0] == "generator-chains-avif", fails
    assert "build_example_page.py" in fails[0][1], fails[0][1]


def test_webp_with_avif_wire_passes():
    fails = _run_gate({
        "build_example_page.py":
            'OUT = \'<source type="image/webp" srcset="a.webp">\'\n'
            "import build_avif\n"
            "build_avif.wire()\n"
    })
    assert fails == [], fails


def test_no_webp_at_all_passes():
    fails = _run_gate({"build_example_page.py": 'OUT = "<p>hello</p>"\n'})
    assert fails == [], fails


def test_build_avif_itself_excluded():
    # build_avif.py is wire()'s own implementation, the real file this
    # repo ships: must never flag itself.
    real = io.open(os.path.join(ROOT, "ops", "build_avif.py"),
                    encoding="utf-8").read()
    fails = _run_gate({"build_avif.py": real})
    assert fails == [], fails


def test_wire_zone_heroes_excluded_even_with_webp_and_no_avif_call():
    # Real, live shape: wire_zone_heroes.py writes a webp <source> and has
    # no build_avif.wire() call of its own, by design, because it is only
    # ever invoked from inside build_zone_pages.py's main(), which chains
    # build_avif.wire() itself afterward in the same run.
    real = io.open(os.path.join(ROOT, "ops", "wire_zone_heroes.py"),
                    encoding="utf-8").read()
    assert 'type="image/webp"' in real, "fixture assumption changed upstream"
    assert "build_avif.wire()" not in real, "fixture assumption changed upstream"
    fails = _run_gate({"wire_zone_heroes.py": real})
    assert fails == [], fails


def test_build_epub_excluded_despite_webp_mimetype_entry():
    real = io.open(os.path.join(ROOT, "ops", "build_epub.py"),
                    encoding="utf-8").read()
    assert "image/webp" in real, "fixture assumption changed upstream"
    fails = _run_gate({"build_epub.py": real})
    assert fails == [], fails


def test_real_committed_build_cleaning_index_passes():
    """Sanity check against the real, fixed file: this operator cycle's
    own fix (chaining build_avif.wire() and fingerprint_assets.main(False)
    at the end of build_cleaning_index.py's main()) must satisfy the gate
    against the real repository, not just a scratch fixture."""
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_generator_chains_avif()
    assert preflight.FAIL == [], preflight.FAIL


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    ok = 0
    for t in tests:
        t()
        ok += 1
    print(f"OK: gate_generator_chains_avif, {ok}/{len(tests)} checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
