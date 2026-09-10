#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_decisions_index_current() (and its pure
check_decisions_index()) catches DECISIONS.md's own section 43 index table
going out of step with the decisions actually recorded in the file.

Found 2026-09-10, this operator, on the standing "cold-read DECISIONS.md
for citation staleness" handoff several prior cycles today had each
deferred as hours-sized. The table indexed DEC-0001 through DEC-0037 only;
the eight later D-series decisions (D-001, D-002, D-003, D-014 to D-018),
including two of the file's most consequential strategic calls, were never
added. Fixed by adding them; this test proves the gate catches the same
shape again in either direction (a decided-but-unindexed entry, or an
indexed entry with no matching decision left in the file).

Run:  python ops/tests/test_gate_decisions_index_current.py
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
    "## DEC-0001: Entryway is initial proving ground\n\n"
    "### Decision\n\ntext\n\n"
    "## D-001 | 2026-08-22 | Standards Pack ships free\n\n"
    "text\n\n"
    "# 43. Decision Index\n\n"
    "| ID | Decision | Status | Domain |\n"
    "|---|---|---|---|\n"
    "| DEC-0001 | Entryway is initial proving ground | ACTIVE | Strategy |\n"
    "| D-001 | Standards Pack ships free, not at $12 | ACTIVE | Commerce |\n\n"
    "# 44. Maintenance Rule\n"
)

MISSING_FROM_INDEX = (
    "# Register\n\n"
    "## DEC-0001: Entryway is initial proving ground\n\n"
    "### Decision\n\ntext\n\n"
    "## D-001 | 2026-08-22 | Standards Pack ships free\n\n"
    "text\n\n"
    "# 43. Decision Index\n\n"
    "| ID | Decision | Status | Domain |\n"
    "|---|---|---|---|\n"
    "| DEC-0001 | Entryway is initial proving ground | ACTIVE | Strategy |\n\n"
    "# 44. Maintenance Rule\n"
)

STALE_IN_INDEX = (
    "# Register\n\n"
    "## DEC-0001: Entryway is initial proving ground\n\n"
    "### Decision\n\ntext\n\n"
    "# 43. Decision Index\n\n"
    "| ID | Decision | Status | Domain |\n"
    "|---|---|---|---|\n"
    "| DEC-0001 | Entryway is initial proving ground | ACTIVE | Strategy |\n"
    "| D-099 | A decision that does not exist below | ACTIVE | Ghost |\n\n"
    "# 44. Maintenance Rule\n"
)

NO_INDEX_SECTION = (
    "# Register\n\n"
    "## DEC-0001: Entryway is initial proving ground\n\n"
    "### Decision\n\ntext\n"
)


def _run_gate(text):
    tmp_dir = tempfile.mkdtemp()
    try:
        io.open(os.path.join(tmp_dir, "DECISIONS.md"), "w",
                encoding="utf-8").write(text)
        real_root = preflight.ROOT
        preflight.ROOT = tmp_dir
        before = len(preflight.FAIL)
        try:
            preflight.gate_decisions_index_current()
        finally:
            preflight.ROOT = real_root
        return preflight.FAIL[before:]
    finally:
        shutil.rmtree(tmp_dir)


def test_pure_check_finds_nothing_when_both_sides_agree():
    assert preflight.check_decisions_index(GOOD) == []
    print("ok  a body/index pair that agree pass clean")


def test_pure_check_catches_a_decision_missing_from_the_index():
    problems = preflight.check_decisions_index(MISSING_FROM_INDEX)
    assert any("D-001" in p for p in problems), problems
    print("ok  a decided-but-unindexed entry is caught")


def test_pure_check_catches_a_stale_index_row():
    problems = preflight.check_decisions_index(STALE_IN_INDEX)
    assert any("D-099" in p for p in problems), problems
    print("ok  an indexed entry with no matching decision is caught")


def test_gate_passes_clean_on_agreement():
    fails = _run_gate(GOOD)
    assert not fails, fails
    print("ok  gate passes clean when body and index agree")


def test_gate_fails_by_name_on_missing_index_row():
    fails = _run_gate(MISSING_FROM_INDEX)
    assert len(fails) == 1, fails
    gate, msg = fails[0]
    assert gate == "decisions-index-current", fails
    assert "D-001" in msg, msg
    print("ok  gate fails naming decisions-index-current and D-001")


def test_gate_fails_by_name_on_stale_index_row():
    fails = _run_gate(STALE_IN_INDEX)
    assert len(fails) == 1, fails
    gate, msg = fails[0]
    assert gate == "decisions-index-current", fails
    assert "D-099" in msg, msg
    print("ok  gate fails naming decisions-index-current and D-099")


def test_no_index_section_is_reported_not_silently_skipped():
    problems = preflight.check_decisions_index(NO_INDEX_SECTION)
    assert problems, "a missing index section must be reported, not ignored"
    print("ok  a file with no section 43 at all is flagged, not skipped")


def test_missing_file_does_not_crash():
    tmp_dir = tempfile.mkdtemp()
    try:
        real_root = preflight.ROOT
        preflight.ROOT = tmp_dir
        before = len(preflight.FAIL)
        try:
            preflight.gate_decisions_index_current()
        finally:
            preflight.ROOT = real_root
        assert preflight.FAIL[before:] == []
        print("ok  a missing DECISIONS.md does not crash the gate")
    finally:
        shutil.rmtree(tmp_dir)


def test_real_repository_file_passes_right_now():
    """Not a synthetic fixture: the actual committed DECISIONS.md, run
    through the real gate exactly as preflight.py's main() calls it, so a
    passing test here means the repository is genuinely fixed, not just
    the logic.
    """
    before = len(preflight.FAIL)
    preflight.gate_decisions_index_current()
    new_fails = preflight.FAIL[before:]
    assert not new_fails, (
        "the real DECISIONS.md index is out of step right now: %s" % new_fails)
    print("ok  the real committed DECISIONS.md passes right now")


if __name__ == "__main__":
    test_pure_check_finds_nothing_when_both_sides_agree()
    test_pure_check_catches_a_decision_missing_from_the_index()
    test_pure_check_catches_a_stale_index_row()
    test_gate_passes_clean_on_agreement()
    test_gate_fails_by_name_on_missing_index_row()
    test_gate_fails_by_name_on_stale_index_row()
    test_no_index_section_is_reported_not_silently_skipped()
    test_missing_file_does_not_crash()
    test_real_repository_file_passes_right_now()
    print("\nall gate_decisions_index_current tests passed")
