#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_decisions_owner_action_citations_current()
(and its pure check_decisions_owner_action_citations()) catches a DECISIONS.md
entry citing the wrong OWNER-ACTIONS.md item number.

Found 2026-09-30, this operator, cold-reading D-028 (written the same day)
for the same citation-drift class gate_decisions_index_current() already
catches for decision ids: it escalated its own MCP question as
"OWNER-ACTIONS.md item 20", but item 20 in that file is a different,
unrelated task ("Add one link to each of the 12 published video
descriptions"). The real MCP item there is 21. A pure existence check would
not have caught it, because 20 is a real item, just the wrong one; this is
why the gate also requires a shared distinctive (all-caps acronym) word
between the citing decision's own title and the cited item's text.

Run:  python ops/tests/test_gate_decisions_owner_action_citations_current.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

OWNER_ACTIONS = (
    "# Owner actions\n\n"
    "## Open, ranked by what they unblock\n\n"
    "### Start here: in this order\n\n"
    "| # | Do | Time | Why it is first |\n"
    "|---|---|---|---|\n"
    "| **0** | Add a deploy key | 2 min | Unblocks automated deploys |\n\n"
    "### 20. Add one link to each of the 12 published video descriptions. Ten minutes.\n\n"
    "Paste a link in the description of each already-published video.\n\n"
    "### 21. Decide whether 6S Success runs a public MCP endpoint. Two minutes.\n\n"
    "This is a decision about the MCP server and whether to expose it.\n"
)

DECISIONS_CORRECT = (
    "## D-028 | 2026-09-30 | The MCP server has never run\n\n"
    "**Decision.** Escalated to the owner as `OWNER-ACTIONS.md` item 21.\n"
)

DECISIONS_WRONG_EXISTING_ITEM = (
    "## D-028 | 2026-09-30 | The MCP server has never run\n\n"
    "**Decision.** Escalated to the owner as `OWNER-ACTIONS.md` item 20.\n"
)

DECISIONS_NONEXISTENT_ITEM = (
    "## D-028 | 2026-09-30 | The MCP server has never run\n\n"
    "**Decision.** Escalated to the owner as `OWNER-ACTIONS.md` item 999.\n"
)

DECISIONS_NO_ACRONYM_TITLE = (
    "## D-030 | 2026-09-30 | Keep the free sample unchanged for now\n\n"
    "**Decision.** Escalated to the owner as `OWNER-ACTIONS.md` item 20.\n"
)

DECISIONS_OLD_HEADING_SHAPE = (
    "## DEC-0050: The MCP question\n\n"
    "**Decision.** Escalated to the owner as `OWNER-ACTIONS.md` item 21.\n"
)


def _run_gate(decisions_text, owner_text):
    tmp_dir = tempfile.mkdtemp()
    try:
        io.open(os.path.join(tmp_dir, "DECISIONS.md"), "w",
                encoding="utf-8").write(decisions_text)
        io.open(os.path.join(tmp_dir, "OWNER-ACTIONS.md"), "w",
                encoding="utf-8").write(owner_text)
        real_root = preflight.ROOT
        preflight.ROOT = tmp_dir
        before = len(preflight.FAIL)
        try:
            preflight.gate_decisions_owner_action_citations_current()
        finally:
            preflight.ROOT = real_root
        return preflight.FAIL[before:]
    finally:
        shutil.rmtree(tmp_dir)


def test_pure_check_passes_on_a_correct_citation():
    assert preflight.check_decisions_owner_action_citations(
        DECISIONS_CORRECT, OWNER_ACTIONS) == []
    print("ok  a citation to the right item passes clean")


def test_pure_check_catches_the_real_d028_regression():
    problems = preflight.check_decisions_owner_action_citations(
        DECISIONS_WRONG_EXISTING_ITEM, OWNER_ACTIONS)
    assert problems, "citing item 20 instead of 21 must be caught"
    assert any("item 20" in p and "mcp" in p for p in problems), problems
    print("ok  citing an existing-but-wrong item (20 instead of 21) is caught")


def test_pure_check_catches_a_nonexistent_item():
    problems = preflight.check_decisions_owner_action_citations(
        DECISIONS_NONEXISTENT_ITEM, OWNER_ACTIONS)
    assert any("999" in p for p in problems), problems
    print("ok  citing a nonexistent item number is caught")


def test_pure_check_skips_a_title_with_no_acronym():
    """A decision whose title carries no distinctive acronym is not
    checked further: guessing off common words produced a real false
    positive during development (both texts happened to share the word
    "corpus"), so this case is deliberately left unverified rather than
    risk a false fail.
    """
    problems = preflight.check_decisions_owner_action_citations(
        DECISIONS_NO_ACRONYM_TITLE, OWNER_ACTIONS)
    assert problems == [], problems
    print("ok  a title with no acronym keyword is not falsely flagged")


def test_pure_check_handles_the_older_colon_heading_shape():
    problems = preflight.check_decisions_owner_action_citations(
        DECISIONS_OLD_HEADING_SHAPE, OWNER_ACTIONS)
    assert problems == [], problems
    print("ok  the older 'DEC-NNNN: title' heading shape is also parsed")


def test_gate_passes_clean_on_agreement():
    fails = _run_gate(DECISIONS_CORRECT, OWNER_ACTIONS)
    assert not fails, fails
    print("ok  gate passes clean when the citation is correct")


def test_gate_fails_by_name_on_the_planted_regression():
    fails = _run_gate(DECISIONS_WRONG_EXISTING_ITEM, OWNER_ACTIONS)
    assert len(fails) == 1, fails
    gate, msg = fails[0]
    assert gate == "decisions-owner-action-citations-current", fails
    assert "item 20" in msg, msg
    print("ok  gate fails naming decisions-owner-action-citations-current and item 20")


def test_missing_file_does_not_crash():
    tmp_dir = tempfile.mkdtemp()
    try:
        real_root = preflight.ROOT
        preflight.ROOT = tmp_dir
        before = len(preflight.FAIL)
        try:
            preflight.gate_decisions_owner_action_citations_current()
        finally:
            preflight.ROOT = real_root
        assert preflight.FAIL[before:] == []
        print("ok  missing DECISIONS.md/OWNER-ACTIONS.md does not crash the gate")
    finally:
        shutil.rmtree(tmp_dir)


def test_real_repository_files_pass_right_now():
    """Not a synthetic fixture: the actual committed DECISIONS.md and
    OWNER-ACTIONS.md, run through the real gate exactly as preflight.py's
    main() calls it, proving the repository's own fix, not just the logic.
    """
    before = len(preflight.FAIL)
    preflight.gate_decisions_owner_action_citations_current()
    new_fails = preflight.FAIL[before:]
    assert not new_fails, (
        "a real OWNER-ACTIONS.md citation in DECISIONS.md is wrong right "
        "now: %s" % new_fails)
    print("ok  the real committed files pass right now")


if __name__ == "__main__":
    test_pure_check_passes_on_a_correct_citation()
    test_pure_check_catches_the_real_d028_regression()
    test_pure_check_catches_a_nonexistent_item()
    test_pure_check_skips_a_title_with_no_acronym()
    test_pure_check_handles_the_older_colon_heading_shape()
    test_gate_passes_clean_on_agreement()
    test_gate_fails_by_name_on_the_planted_regression()
    test_missing_file_does_not_crash()
    test_real_repository_files_pass_right_now()
    print("\nall gate_decisions_owner_action_citations_current tests passed")
