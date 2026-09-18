#!/usr/bin/env python3
"""
Prove ops/accept_image.py's checklist derivation and scoring logic, on top
of what --self-test already replays from PLAN-MEDIA-2026-09-07.md.

--self-test proves the three real, verified-by-hand outcomes score
correctly. This file proves the derivation functions themselves handle the
shapes that matter: a card whose parenthetical must be stripped, a zone
whose own text carries a negative clause and one whose does not, a missing
answer treated as an unanswered failure rather than a silent pass, and the
114-zone dedup bug (three zone names repeat across rooms; keying by bare
name silently dropped 3 of 114) that check_all() found and this test pins
so it cannot come back.

Run:  python ops/tests/test_accept_image.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import accept_image as AI                                          # noqa: E402


def main() -> int:
    fails = []

    # 1. Parenthetical stripped from a card callout, and the whole list
    #    kept in order (order matters: item 0 is the hard-fail primary
    #    object).
    got = AI._strip_parenthetical("Key Bowl (Home Base)")
    if got != "Key Bowl":
        fails.append(f"parenthetical not stripped: {got!r}")

    cl = AI.checklist_for_card({"id": "X", "title": "T",
                                "callouts": ["A (loc)", "B (loc)"]})
    if cl["must_show"] != ["A", "B"]:
        fails.append(f"card must_show wrong: {cl['must_show']}")
    if cl["contradicts"] != []:
        fails.append("a card checklist must never carry a contradicts "
                      "list; PLAN-MEDIA-2026-09-07.md's negative-image "
                      "concept is zone-specific")

    # 2. A card with no callouts refuses rather than shipping an empty
    #    checklist that would pass anything.
    try:
        AI.checklist_for_card({"id": "X", "title": "T", "callouts": []})
        fails.append("a card with zero callouts did not raise")
    except ValueError:
        pass

    # 3. must_show phrase splitting: a comma-separated list with a
    #    leading "and" on the last item.
    phrases = AI._noun_phrases(
        "a tray, a wallet, and a phone.")
    if phrases != ["a tray", "a wallet", "a phone"]:
        fails.append(f"noun-phrase split wrong: {phrases}")

    # 4. Negative-clause extraction: present when the source text states
    #    its own negative, absent (not invented) when it does not.
    got = AI._negative_clauses("no blank silhouettes, one hammer")
    if got != ["blank silhouettes"]:
        fails.append(f"negative-clause extraction wrong: {got}")
    got = AI._negative_clauses("a tray, a wallet, and a phone")
    if got != []:
        fails.append(f"negative-clause extraction invented a phrase from "
                      f"text with none: {got}")
    got = AI._negative_clauses("the tray and the folder and nothing else")
    if got != []:
        fails.append(f"'nothing else' should reduce to no phrase, got {got}")

    # 4b. "either nothing or X": X is an acceptable alternative state, not
    # a forbidden object. The real 2026-09-10 bug: the bedroom zone's own
    # "Under the bed holds either nothing or two labelled flat bins" was
    # scored as a must-fail-if-shown item, which would reject a photograph
    # correctly showing the labelled bins.
    got = AI._negative_clauses(
        "Under the bed holds either nothing or two labelled flat bins.")
    if got != []:
        fails.append(f"'nothing or X' wrongly treated as a forbidden "
                      f"phrase: {got}")
    # A genuine two-item forbidden list joined by "or" must still work.
    got = AI._negative_clauses("no mail or coupons on the counter")
    if got != ["mail or coupons on the counter"]:
        fails.append(f"a real 'no X or Y' forbidden pair was dropped: {got}")

    # 4c. A pronoun with no noun left to check names no object. Found live
    # 2026-09-18 against six real zones: "a seat with nothing on it at
    # all" and "nothing beside it" each produced a checklist item asking a
    # vision model "Is on it at all visible in this image?" or "Is beside
    # it visible in this image?", a question about nothing. Before the fix
    # these returned ["on it at all"] and ["beside it"].
    for src in ("a seat with nothing on it at all",
                "the counter carries one liftable tray and nothing beside it"):
        got = AI._negative_clauses(src)
        if got != []:
            fails.append(f"a pronoun-only remainder should name no "
                          f"object, got {got} from {src!r}")

    # 4d. A relative clause with no noun of its own ("nothing that was
    # there yesterday") is the same shape: dropped, not emitted whole.
    got = AI._negative_clauses("a tray holding nothing that was there yesterday")
    if got != []:
        fails.append(f"a noun-free relative clause should be dropped, got {got}")

    # 4e. Filler stripped from an edge without losing real content
    # underneath it: "nothing at all sitting on either lid" must still
    # name the lid, not just the filler in front of it.
    got = AI._negative_clauses("nothing at all sitting on either lid")
    if got != ["sitting on either lid"]:
        fails.append(f"filler-edge stripping lost real content: {got}")

    # 4f. A bare comparative with nothing to compare against names no
    # object either: "filled level with the rim and no higher".
    got = AI._negative_clauses("filled level with the rim and no higher")
    if got != []:
        fails.append(f"a bare comparative should name no object, got {got}")

    # 5. A checklist item with no answer at all is a failure, not a pass:
    #    "unknown is not unused" (CLAUDE.md 0.4) applies here too.
    cl = {"must_show": ["a tray"], "must_not_show": [], "contradicts": []}
    passed, reasons = AI.score(cl, {})
    if passed or not reasons:
        fails.append("an unanswered must_show item scored as a pass")

    # 6. The 114-zone dedup regression: three zone names repeat across
    #    rooms ("Dresser Drawers", "Shower or Tub", "Toilet Area"), so a
    #    dict keyed on the bare zone name silently collapses to 111. This
    #    is the exact bug --check surfaced while building this module.
    stems = AI._zones_by_stem()
    if len(stems) != 114:
        fails.append(f"_zones_by_stem() returned {len(stems)}, expected "
                      f"114; a name collision is dropping zones again")
    dresser = [s for s in stems if "dresser-drawers" in s]
    if len(dresser) != 2:
        fails.append(f"expected 2 distinct 'Dresser Drawers' zones (one "
                      f"per room), found {len(dresser)}: {dresser}")

    # 7. question_key() round-trips through all_questions()/score() without
    #    the must_show/must_not_show/contradicts namespaces colliding, even
    #    when the same literal phrase appears in more than one section.
    cl = {"must_show": ["a mark"], "must_not_show": ["a mark"],
          "contradicts": []}
    built = AI.all_questions(cl)
    qs = dict(built)
    # Assert the INVARIANT (no key collapses) rather than a fixed count.
    # This read "!= 2" until 2026-09-11, when a third, legitimate question
    # was added: the object-only primary test. That is not a collision, and
    # a test pinned to a count reports one as though it were.
    if len(qs) != len(built):
        fails.append(f"identical phrases in two sections collided into "
                      f"one question key: {list(qs)}")
    for want in ("must_show:a mark", "must_not_show:a mark"):
        if want not in qs:
            fails.append(f"namespaced key {want!r} missing from {list(qs)}")

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("OK  test_accept_image: 7/7 cases pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
