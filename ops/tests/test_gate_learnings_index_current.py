#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_learnings_index_current() (and its pure
check_learnings_index()) catches LEARNINGS.md's own section 31 index table
going out of step with the learnings actually recorded in the file.

Found 2026-09-18, this operator, on the standing "cold-read DECISIONS.md /
LEARNINGS.md for citation staleness" handoff several prior cycles had
deferred as hours-sized. The sibling table in DECISIONS.md (section 43) had
already gotten this exact gate (gate_decisions_index_current, 2026-09-10)
after eight decisions went missing from it; nobody had checked whether
LEARNINGS.md's own index (section 31) had the same gap. It did: the table
indexed LRN-0001 through LRN-0008 only, while the Verified Learning
Registers (section 33) had grown to LRN-0016, eight real learnings
invisible to the index, LRN-0009 among them, the learning that names this
exact defect class. Fixed by adding the eight rows; this test proves the
gate catches the same shape again in either direction.

Run:  python ops/tests/test_gate_learnings_index_current.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

GOOD = (
    "# Register\n\n"
    "## 31. Learning Index\n\n"
    "| ID | Learning | Domain | Status | Confidence |\n"
    "|---|---|---|---|---|\n"
    "| LRN-0001 | Desired function may improve relevance | DESIRED_FUNCTION | HYPOTHESIS | UNKNOWN |\n"
    "| LRN-0006 | The mailing list 500s | LIFECYCLE | SUPPORTED | HIGH |\n\n"
    "## 32. Initial Hypothesis Register\n\n"
    "### LRN-0001: Desired Function May Improve Relevance\n\ntext\n\n"
    "## 33. Verified Learning Registers\n\n"
    "#### LRN-0006: The mailing list cannot take a subscriber\n\ntext\n"
)

MISSING_FROM_INDEX = (
    "# Register\n\n"
    "## 31. Learning Index\n\n"
    "| ID | Learning | Domain | Status | Confidence |\n"
    "|---|---|---|---|---|\n"
    "| LRN-0001 | Desired function may improve relevance | DESIRED_FUNCTION | HYPOTHESIS | UNKNOWN |\n\n"
    "## 32. Initial Hypothesis Register\n\n"
    "### LRN-0001: Desired Function May Improve Relevance\n\ntext\n\n"
    "## 33. Verified Learning Registers\n\n"
    "#### LRN-0006: The mailing list cannot take a subscriber\n\ntext\n"
)

STALE_IN_INDEX = (
    "# Register\n\n"
    "## 31. Learning Index\n\n"
    "| ID | Learning | Domain | Status | Confidence |\n"
    "|---|---|---|---|---|\n"
    "| LRN-0001 | Desired function may improve relevance | DESIRED_FUNCTION | HYPOTHESIS | UNKNOWN |\n"
    "| LRN-0099 | A learning that does not exist below | GHOST | SUPPORTED | HIGH |\n\n"
    "## 32. Initial Hypothesis Register\n\n"
    "### LRN-0001: Desired Function May Improve Relevance\n\ntext\n"
)

NO_INDEX_SECTION = (
    "# Register\n\n"
    "## 32. Initial Hypothesis Register\n\n"
    "### LRN-0001: Desired Function May Improve Relevance\n\ntext\n"
)


def _run_gate(text):
    tmp_dir = tempfile.mkdtemp()
    try:
        io.open(os.path.join(tmp_dir, "LEARNINGS.md"), "w",
                encoding="utf-8").write(text)
        real_root = preflight.ROOT
        preflight.ROOT = tmp_dir
        before = len(preflight.FAIL)
        try:
            preflight.gate_learnings_index_current()
        finally:
            preflight.ROOT = real_root
        return preflight.FAIL[before:]
    finally:
        shutil.rmtree(tmp_dir)


def test_pure_check_finds_nothing_when_both_sides_agree():
    assert preflight.check_learnings_index(GOOD) == []
    print("ok  a body/index pair that agree pass clean")


def test_pure_check_catches_a_learning_missing_from_the_index():
    problems = preflight.check_learnings_index(MISSING_FROM_INDEX)
    assert any("LRN-0006" in p for p in problems), problems
    print("ok  a recorded-but-unindexed entry is caught")


def test_pure_check_catches_a_stale_index_row():
    problems = preflight.check_learnings_index(STALE_IN_INDEX)
    assert any("LRN-0099" in p for p in problems), problems
    print("ok  an indexed entry with no matching learning is caught")


def test_gate_passes_clean_on_agreement():
    fails = _run_gate(GOOD)
    assert not fails, fails
    print("ok  gate passes clean when body and index agree")


def test_gate_fails_by_name_on_missing_index_row():
    fails = _run_gate(MISSING_FROM_INDEX)
    assert len(fails) == 1, fails
    gate, msg = fails[0]
    assert gate == "learnings-index-current", fails
    assert "LRN-0006" in msg, msg
    print("ok  gate fails naming learnings-index-current and LRN-0006")


def test_gate_fails_by_name_on_stale_index_row():
    fails = _run_gate(STALE_IN_INDEX)
    assert len(fails) == 1, fails
    gate, msg = fails[0]
    assert gate == "learnings-index-current", fails
    assert "LRN-0099" in msg, msg
    print("ok  gate fails naming learnings-index-current and LRN-0099")


def test_no_index_section_is_reported_not_silently_skipped():
    problems = preflight.check_learnings_index(NO_INDEX_SECTION)
    assert problems, "a missing index section must be reported, not ignored"
    print("ok  a file with no section 31 at all is flagged, not skipped")


def test_missing_file_does_not_crash():
    tmp_dir = tempfile.mkdtemp()
    try:
        real_root = preflight.ROOT
        preflight.ROOT = tmp_dir
        before = len(preflight.FAIL)
        try:
            preflight.gate_learnings_index_current()
        finally:
            preflight.ROOT = real_root
        assert preflight.FAIL[before:] == []
        print("ok  a missing LEARNINGS.md does not crash the gate")
    finally:
        shutil.rmtree(tmp_dir)


def test_real_repository_file_passes_right_now():
    """Not a synthetic fixture: the actual committed LEARNINGS.md, run
    through the real gate exactly as preflight.py's main() calls it, so a
    passing test here means the repository is genuinely fixed, not just
    the logic.
    """
    before = len(preflight.FAIL)
    preflight.gate_learnings_index_current()
    new_fails = preflight.FAIL[before:]
    assert not new_fails, (
        "the real LEARNINGS.md index is out of step right now: %s" % new_fails)
    print("ok  the real committed LEARNINGS.md passes right now")


if __name__ == "__main__":
    test_pure_check_finds_nothing_when_both_sides_agree()
    test_pure_check_catches_a_learning_missing_from_the_index()
    test_pure_check_catches_a_stale_index_row()
    test_gate_passes_clean_on_agreement()
    test_gate_fails_by_name_on_missing_index_row()
    test_gate_fails_by_name_on_stale_index_row()
    test_no_index_section_is_reported_not_silently_skipped()
    test_missing_file_does_not_crash()
    test_real_repository_file_passes_right_now()
    print("\nall gate_learnings_index_current tests passed")
