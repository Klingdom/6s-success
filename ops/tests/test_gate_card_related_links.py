#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_card_related_links() catches a next_card or
related_path reference that points at a card id which does not exist, and
prove gate_unsourced_stats() no longer misses a claim sitting in a list
field or phrased as "35,000 decisions a day" (the number not glued to the
unit word).

Found 2026-09-10, cold-reading ops/merge_cardtext.py: running it against the
real corpus printed "dangling links 34" and "CLAIMS TO VERIFY", something no
prior cycle's preflight run had ever surfaced, because nothing called this
script's own checks from preflight. Traced further: 47 next_card/related_path
references (mostly a cut "Experts" card family, EX-001 through EX-012, that
was never built) pointed nowhere, 33 of them already baked as printed text
into 20 real, shipped Entryway card back images (site/assets/cards/
entryway/*-back-lg.webp), confirmed by opening the actual rendered image, not
assumed from the JSON. Two shipped cards (EM-004, EM-012) also carried an
unsourced numeric claim in did_you_know ("People make up to 35,000 decisions
a day") that gate_unsourced_stats could not see: the number is followed by a
noun ("decisions"), not directly by a time unit, so the gate's own STAT regex
never matched it, and the same claim-detector skipped the "claims" field
entirely because it is a list, not a string, the same "certifies a claim it
never read" gap this gate's own docstring already names twice for file
coverage. Fixed the six source batches (ops/cardtext/batch-*.json): every
dangling reference dropped, one (ET-006's "EU-000 Vertical Storage", the
digits alone wrong) corrected to the real EU-008, both fabricated stats
rewritten to non-statistical, still-useful copy. The already-shipped pixel
defect on 20 cards is separate, tracked in OWNER-ACTIONS.md, since fixing
it means regenerating art, not editing text.

Run:  python ops/tests/test_gate_card_related_links.py
"""
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _card(cid, **extra):
    c = {"id": cid, "title": cid}
    c.update(extra)
    return c


def _make_tree(batch_cards, merged_cards=None):
    tmp = tempfile.mkdtemp()
    ct = os.path.join(tmp, "ops", "cardtext")
    os.makedirs(ct)
    io.open(os.path.join(ct, "batch-00.json"), "w", encoding="utf-8").write(
        json.dumps(batch_cards, ensure_ascii=False))
    if merged_cards is not None:
        bd = os.path.join(tmp, "build")
        os.makedirs(bd)
        io.open(os.path.join(bd, "entryway-cardtext.json"), "w",
                encoding="utf-8").write(
            json.dumps({"deck": "entryway", "cards": merged_cards},
                       ensure_ascii=False))
    return tmp


def _run_related_links(batch_cards, merged_cards=None):
    tmp = _make_tree(batch_cards, merged_cards)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_card_related_links()
        return list(preflight.FAIL)
    finally:
        preflight.ROOT = old_root
        shutil.rmtree(tmp)


def _run_unsourced(cards):
    tmp = tempfile.mkdtemp()
    bd = os.path.join(tmp, "build")
    os.makedirs(bd)
    io.open(os.path.join(bd, "entryway-cardtext.json"), "w",
            encoding="utf-8").write(
        json.dumps({"deck": "entryway", "cards": cards}, ensure_ascii=False))
    os.makedirs(os.path.join(tmp, "ops", "cardtext"))
    empty_site = os.path.join(tmp, "site")
    os.makedirs(empty_site)
    old_root, old_site = preflight.ROOT, preflight.SITE
    preflight.ROOT = tmp
    preflight.SITE = empty_site   # isolate from the real site's own pages
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_unsourced_stats()
        return list(preflight.WARN)
    finally:
        preflight.ROOT, preflight.SITE = old_root, old_site
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. A clean set of cards: next_card and related_path both resolve.
    clean = [
        _card("EM-001", next_card={"id": "EM-002", "title": "Next"},
              related_path={"tools": "ET-001"}),
        _card("EM-002"),
        _card("ET-001"),
    ]
    r = _run_related_links(clean)
    if r:
        fails.append("clean batch wrongly flagged: %r" % (r,))

    # 2. A dangling next_card: caught by name.
    bad_next = [
        _card("EM-001", next_card={"id": "ER-002", "title": "Living Room"}),
    ]
    r = _run_related_links(bad_next)
    if not r or "ER-002" not in r[0][1]:
        fails.append("dangling next_card not caught by id: %r" % (r,))

    # 3. A dangling related_path as a bare string: caught.
    bad_rel_str = [
        _card("EM-001", related_path={"experts": "EX-002"}),
    ]
    r = _run_related_links(bad_rel_str)
    if not r or "EX-002" not in r[0][1]:
        fails.append("dangling related_path (string) not caught: %r" % (r,))

    # 4. A dangling related_path inside a "CODE Title" list, the real shape
    #    most of the 47 defects were actually in: caught.
    bad_rel_list = [
        _card("EE-002", related_path={"experts": ["EX-002 Weather Prep"]}),
    ]
    r = _run_related_links(bad_rel_list)
    if not r or "EX-002" not in r[0][1]:
        fails.append("dangling related_path (list) not caught: %r" % (r,))

    # 5. The generator-ownership trap: the source batch is clean but the
    #    merged build file still carries the old dangling reference. Must
    #    still fail, or a hand-fixed batch with a stale merged file would
    #    read as clean.
    r = _run_related_links(clean, merged_cards=bad_next)
    if not r:
        fails.append("stale merged build file not caught: %r" % (r,))

    # 6. The real committed batches: clean, after this cycle's fix.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_card_related_links()
    if preflight.FAIL:
        fails.append("the real committed card batches failed: %r"
                     % (preflight.FAIL,))

    # 7. gate_unsourced_stats: a claim living in a list field ("claims") is
    #    now read, not skipped for not being a string.
    r = _run_unsourced([_card("EW-099", claims=[
        "The average person spends 2.5 days each year looking for lost items."])])
    if not r:
        fails.append("a claim inside a list field was not caught: %r" % (r,))

    # 8. gate_unsourced_stats: "35,000 decisions a day", the number not
    #    glued to the unit word, the real shape found on EM-012.
    r = _run_unsourced([_card("EM-099", did_you_know=(
        "People make up to 35,000 decisions a day. A visible checklist "
        "removes small, repetitive decisions."))])
    if not r:
        fails.append("'35,000 decisions a day' was not caught: %r" % (r,))

    # 9. False-positive guard: a plain spec number must stay quiet. "684
    #    cards" has no comma at that size and no CLAIMY word nearby.
    r = _run_unsourced([_card("EM-098", objective=(
        "Sort the 684 cards in the Whole House Print Pack by room."))])
    if r:
        fails.append("a plain spec number was wrongly flagged: %r" % (r,))

    # 10. The real committed corpus: clean, after this cycle's fix.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_unsourced_stats()
    if preflight.WARN:
        fails.append("the real committed corpus still trips "
                     "gate_unsourced_stats: %r" % (preflight.WARN,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_card_related_links + gate_unsourced_stats, 10/10 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
