#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_no_british_spellings_shipped() catches an
UPPER CASE British spelling, not just a lower case one.

Found 2026-10-02, this operator, the same cycle this gate itself was added
to close A12. The gate's pattern was built straight from fix_dialect.PAIRS
(all lower case) with no re.IGNORECASE, so it never matched a word shipped
in capitals. Three real deck pages did exactly that: card titles and
taglines are authored upper case ("LABELLED", "COLOURS", "THE NEIGHBOUR'S
ROOF-LEAK SCARE" in ops/cardtext/build_garage_deck.py, build_workshop_deck.py
and build_living_room_deck.py), each sitting one line from the correctly
spelled American word in the same card's own body text, and the gate passed
clean the entire time it existed. Fixed by adding re.IGNORECASE.

Run:  python ops/tests/test_gate_no_british_spellings_shipped_case.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _run_gate(html_files: dict, py_files: dict | None = None) -> list:
    """html_files: {relative site/ path: html}. py_files: {relative
    ops/cardtext/ path: source}. Writes both into a scratch tree, points
    preflight.ROOT at it, runs the real gate, restores."""
    tmp = tempfile.mkdtemp()
    scratch_site = os.path.join(tmp, "site")
    os.makedirs(scratch_site)
    for rel, html in html_files.items():
        full = os.path.join(scratch_site, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        io.open(full, "w", encoding="utf-8").write(html)
    cardtext_dir = os.path.join(tmp, "ops", "cardtext")
    os.makedirs(cardtext_dir)
    for rel, src in (py_files or {}).items():
        io.open(os.path.join(cardtext_dir, rel), "w", encoding="utf-8").write(src)
    old_site, old_root = preflight.SITE, preflight.ROOT
    try:
        preflight.SITE = scratch_site
        preflight.ROOT = tmp
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_no_british_spellings_shipped()
        return list(preflight.FAIL)
    finally:
        preflight.SITE, preflight.ROOT = old_site, old_root
        shutil.rmtree(tmp)


def test_lower_case_british_spelling_caught():
    fails = _run_gate({"garage-deck.html": "<p>labelled</p>"})
    assert len(fails) == 1 and fails[0][0] == "no-british-spellings-shipped", fails


def test_upper_case_british_spelling_caught():
    # The exact live regression: a card title shipped in capitals.
    fails = _run_gate({
        "garage-deck.html": "<h3>NAME THE UNLABELLED BOTTLE</h3>"
    })
    assert len(fails) == 1 and fails[0][0] == "no-british-spellings-shipped", fails
    assert "garage-deck.html" in fails[0][1], fails[0][1]


def test_mixed_case_british_spelling_caught():
    fails = _run_gate({"workshop-deck.html": "<h3>Keep Only The Colours</h3>"})
    assert len(fails) == 1, fails


def test_american_spelling_passes():
    fails = _run_gate({
        "garage-deck.html": "<h3>NAME THE UNLABELED BOTTLE</h3><p>labeled</p>"
    })
    assert fails == [], fails


def test_upper_case_hit_in_cardtext_generator_caught():
    fails = _run_gate(
        {},
        {"build_garage_deck.py": '"tagline": "LABELLED. DATED."\n'},
    )
    assert len(fails) == 1 and "build_garage_deck.py" in fails[0][1], fails


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    ok = 0
    for t in tests:
        t()
        ok += 1
    print(f"OK: gate_no_british_spellings_shipped (case), {ok}/{len(tests)} checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
