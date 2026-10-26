#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_no_british_spellings_shipped() also catches
fix_dialect.VOCAB words, not only fix_dialect.PAIRS.

Found 2026-10-26, this operator cycle. Phil's own 2026-10-26 cleaning-content
review (ad933f9e5) added VOCAB (torch, skirting, hob, the tap, tea towel,
kitchen roll, sun cream, wellies, a fortnight, rubbish, airing cupboard...)
and fixed it in fix_dialect.py's own three TARGET source files and the deck
builders' frozen copies, but this gate's pattern was still built from PAIRS
alone, so six real, live pages kept shipping the exact words that cycle was
fixing elsewhere: site/articles/how-to-organize-a-junk-drawer.html (five
paragraphs plus its own FAQPage JSON-LD said "a torch"/"the takeaway menus",
one said "a tea towel"), site/consulting.html and the why-is-my-house-
always-messy.html generator (ops/build_messy_article.py) both said "a
fortnight", and site/deck.html's own card alt text said "a rubbish bag".
Found by direct scan against the real committed site, fixed the same cycle,
then this test was written to prove the gate itself, not just the content,
closes the gap.

Also proves the two deliberate carve-outs do not silently widen into a
blanket exemption:
  - "trainers" is excluded from the enforced pattern entirely (it has a
    live, correct American sense -- "train your trainers", people, not
    shoes -- with no room-name to disambiguate it the way "extractor" is
    disambiguated by room). A NEW word must still fail on that same page.
  - "airing cupboard" is allowed exactly once, on exactly the one zone page
    that uses it as a deliberate "Also called..." synonym heading. A
    second instance, or the same word on any other page, still fails.

Run:  python ops/tests/test_gate_no_british_spellings_shipped_vocab.py
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
    """Same scratch-tree harness as test_gate_no_british_spellings_shipped_case.py."""
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


def test_vocab_word_caught():
    # The exact live regression: "torch" is only in VOCAB, never PAIRS.
    fails = _run_gate({"articles/how-to-organize-a-junk-drawer.html":
                        "<p>Keep a torch in the drawer.</p>"})
    assert len(fails) == 1 and fails[0][0] == "no-british-spellings-shipped", fails
    assert "junk-drawer" in fails[0][1], fails[0][1]


def test_vocab_fortnight_phrase_caught():
    fails = _run_gate({"consulting.html":
                        "<p>undo itself in a fortnight.</p>"})
    assert len(fails) == 1, fails


def test_vocab_word_in_cardtext_generator_caught():
    fails = _run_gate(
        {},
        {"build_mudroom_deck.py": '"tip": "Grab a torch before dark."\n'},
    )
    assert len(fails) == 1 and "build_mudroom_deck.py" in fails[0][1], fails


def test_american_vocab_replacement_passes():
    fails = _run_gate({"articles/how-to-organize-a-junk-drawer.html":
                        "<p>Keep a flashlight in the drawer.</p>"})
    assert fails == [], fails


def test_trainers_not_enforced_people_sense():
    # Real live wording on corporate.html and what-a-5s-engagement-costs.html:
    # "trainers" means people here, not shoes, and has no room context to
    # disambiguate it the way "extractor" is. Must not fail.
    fails = _run_gate({"corporate.html":
                        "<p>Whether we train your trainers.</p>"})
    assert fails == [], fails


def test_trainers_page_still_catches_other_vocab():
    # The carve-out is scoped to "trainers" alone, not the whole page.
    fails = _run_gate({"corporate.html":
                        "<p>Whether we train your trainers, using a torch.</p>"})
    assert len(fails) == 1, fails


def test_airing_cupboard_synonym_heading_allowed_once():
    fails = _run_gate({
        "zones/guest-bathroom-the-guest-linen-zone.html":
            "<h2>Also called the airing cupboard</h2>"
    })
    assert fails == [], fails


def test_airing_cupboard_second_instance_still_fails():
    # Proves the allowance is capped at 1, not a blanket exemption for the
    # one page it is named for.
    fails = _run_gate({
        "zones/guest-bathroom-the-guest-linen-zone.html":
            "<h2>Also called the airing cupboard</h2>"
            "<p>Keep towels in the airing cupboard.</p>"
    })
    assert len(fails) == 1, fails


def test_airing_cupboard_on_a_different_page_fails():
    # The exception is keyed to the exact file, not the phrase.
    fails = _run_gate({
        "zones/primary-bathroom-the-under-sink-cabinet.html":
            "<p>Keep towels in the airing cupboard.</p>"
    })
    assert len(fails) == 1, fails


def test_real_committed_site_is_clean():
    """Sanity check against the real repository, not a scratch tree: this
    operator cycle's own fixes (junk-drawer article, consulting.html,
    deck.html, the messy-article generator regenerated) must leave the
    gate passing clean end to end."""
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_no_british_spellings_shipped()
    assert preflight.FAIL == [], preflight.FAIL


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    ok = 0
    for t in tests:
        t()
        ok += 1
    print(f"OK: gate_no_british_spellings_shipped (vocab), {ok}/{len(tests)} checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
