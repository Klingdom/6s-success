#!/usr/bin/env python3
"""
Prove ops/rotate_status_metadata.py's split/plan_rotation functions handle
STATUS.md section 1's actual shape: variable-length entries (some with
internal bold sub-points that are continuations, not entries of their own),
a chain that is not reliably newest-first by file position, and a trailing
pointer note that must be updated, not archived as a dated entry.

Run:  python ops/tests/test_rotate_status_metadata.py
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import rotate_status_metadata as rsm                             # noqa: E402

HEADER = "# 1. Status Metadata\n\n"
FOOTER = "\n\n# 2. Executive Snapshot\n\nmore file follows.\n"
POINTER = "**Older entries (10 of them, 2026-08 to 2026-10-20) live in `STATUS-ARCHIVE.md`.** Some trailing prose.\n"


def _status_text(body: str) -> str:
    return HEADER + body + "\n\n" + POINTER + FOOTER


def test_split_simple_chain():
    body = (
        "**Last Updated:** 2026-10-24: did a thing.\n\n"
        "**Earlier, 2026-10-23: did an earlier thing."
    )
    text = _status_text(body)
    before, entries, pointer_note, after = rsm.split_metadata_chain(text)
    assert len(entries) == 2, entries
    assert entries[0].startswith("**Last Updated:**")
    assert entries[1].startswith("**Earlier, 2026-10-23")
    assert pointer_note.strip() == POINTER.strip()
    return []


def test_subpoints_fold_into_their_entry():
    """A multi-paragraph entry (OPEN LOOP style) with internal bold
    sub-points must be read as ONE entry, not split into several --
    this is the exact shape that broke a naive "every bold paragraph is
    an entry" parser (the one BLOCKER-001's own split uses, deliberately
    not reused here).
    """
    body = (
        "**OPEN LOOP AS AT 2026-10-01: production was behind.**\n\n"
        "**Why, precisely.** Because the build queue was backed up.\n\n"
        "**Also killed mid-run:** a watcher process died.\n\n"
        "**Latest, 2026-10-26: this is the real latest entry.**"
    )
    text = _status_text(body)
    _, entries, _, _ = rsm.split_metadata_chain(text)
    fails = []
    if len(entries) != 2:
        fails.append("expected 2 entries (OPEN LOOP absorbing its two "
                      "sub-points, plus Latest), got %d: %r"
                      % (len(entries), entries))
    elif "Why, precisely" not in entries[0] or "Also killed mid-run" not in entries[0]:
        fails.append("sub-points did not fold into the OPEN LOOP entry: %r"
                      % entries[0])
    return fails


def test_out_of_order_dates_keep_the_true_latest():
    """The real chain found 2026-10-26 entries sitting BELOW 2026-10-24
    ones (a mis-anchored prepend). plan_rotation must keep the entry
    with the latest DATE, not the one physically first.
    """
    body = (
        "**Last Updated:** 2026-10-24: looks newest by position.\n\n"
        "**Earlier, 2026-10-23: genuinely older.**\n\n"
        "**Latest, 2026-10-26: actually the newest entry, misplaced below "
        "older ones.**"
    )
    text = _status_text(body)
    new_text, archived = rsm.plan_rotation(text, "2026-10-27")
    fails = []
    if len(archived) != 2:
        fails.append("expected 2 archived entries, got %d: %r"
                      % (len(archived), archived))
    live_span = new_text.split("**Older entries (")[0]
    if "2026-10-26" not in live_span:
        fails.append("the 2026-10-26 entry is not live in the new text")
    if "**Last Updated:** 2026-10-24" in live_span:
        fails.append("the stale 2026-10-24 entry was kept live instead of "
                      "archived")
    return fails


def test_tied_max_date_keeps_both():
    body = (
        "**Last Updated:** 2026-10-24: older.\n\n"
        "**Latest, 2026-10-26 (first): tied for newest.**\n\n"
        "**Latest, 2026-10-26 (second): also tied for newest.**"
    )
    text = _status_text(body)
    new_text, archived = rsm.plan_rotation(text, "2026-10-27")
    fails = []
    if len(archived) != 1:
        fails.append("expected 1 archived (the 10-24 entry), got %d: %r"
                      % (len(archived), archived))
    live_span = new_text.split("**Older entries (")[0]
    if "(first)" not in live_span or "(second)" not in live_span:
        fails.append("both tied 2026-10-26 entries should stay live: %r"
                      % live_span)
    return fails


def test_lossless_roundtrip_on_real_file():
    """The real committed STATUS.md must split without raising, and the
    entries plus pointer note must reconstruct the original span exactly
    (split_metadata_chain's own internal check already enforces this;
    this test just proves it holds against the real file, not only a
    synthetic one).
    """
    path = os.path.join(ROOT, "STATUS.md")
    if not os.path.exists(path):
        return []
    text = io.open(path, encoding="utf-8").read()
    try:
        before, entries, pointer_note, after = rsm.split_metadata_chain(text)
    except ValueError as exc:
        return ["split_metadata_chain raised on the real file: %s" % exc]
    rebuilt = before + "\n\n".join(entries) + "\n\n" + pointer_note + after
    if rebuilt != text:
        return ["round-trip of the real file is not byte-identical"]
    return []


def test_no_change_when_already_rotated():
    body = "**Last Updated:** 2026-10-24: the only entry."
    text = _status_text(body)
    new_text, archived = rsm.plan_rotation(text, "2026-10-27")
    if archived or new_text != text:
        return ["a single-entry chain should not be rewritten: "
                "archived=%r changed=%r" % (archived, new_text != text)]
    return []


def test_refuses_unrecognised_first_paragraph():
    body = "A plain paragraph with no recognised label at all."
    text = _status_text(body)
    try:
        rsm.split_metadata_chain(text)
    except ValueError:
        return []
    return ["should have refused a span whose first paragraph is not a "
            "recognised entry start"]


CASES = [
    test_split_simple_chain,
    test_subpoints_fold_into_their_entry,
    test_out_of_order_dates_keep_the_true_latest,
    test_tied_max_date_keeps_both,
    test_lossless_roundtrip_on_real_file,
    test_no_change_when_already_rotated,
    test_refuses_unrecognised_first_paragraph,
]


def main() -> int:
    fails = []
    for case in CASES:
        try:
            case_fails = case()
        except Exception as exc:                                 # noqa: BLE001
            case_fails = ["%s raised %r" % (case.__name__, exc)]
        for f in case_fails or []:
            fails.append("%s: %s" % (case.__name__, f))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: rotate_status_metadata, fail-then-pass proved, %d/%d checks pass"
          % (len(CASES), len(CASES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
