#!/usr/bin/env python3
"""
Prove ops/preflight.py's owner_actions_untracked_items()/
gate_owner_actions_items_tracked() actually flags an open, numbered
OWNER-ACTIONS.md item that cites no GitHub issue, and stays silent once one
does.

WHY THIS EXISTS
---------------
Found 2026-11-01, scheduled operator cycle. Issues #43 through #48 were
filed 2026-10-31 for OWNER-ACTIONS.md items 14, 15, 1, 1b, 5 and 6, but only
items 14 and 15 ever got the backlink text written into their own section;
items 1, 1b, 5 and 6 had a real issue filed for them that nobody could find
starting from the item itself. The same read also found seven more items
(8, 11, 16, 17, 18, 21, 22) and one CRITICAL risk split across two items
(1g, 13, RISK-0011) that had never been filed as a GitHub issue at all. This
is the second time this exact defect class has been found by hand; this
gate exists so a third time is not needed.

Run:  python ops/tests/test_gate_owner_actions_items_tracked.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402


def case_open_item_with_no_issue_is_flagged():
    text = (
        "# Owner actions\n\n"
        "### 7. Listmonk cannot send.\n\n"
        "What: the shared Listmonk SMTP login belongs to another business.\n"
    )
    problems = preflight.owner_actions_untracked_items(text)
    assert problems == ["7. Listmonk cannot send."], problems


def case_open_item_with_issue_is_silent():
    text = (
        "# Owner actions\n\n"
        "### 7. Listmonk cannot send.\n\n"
        "**Tracked as GitHub issue #15**, `P0`/`decision`.\n\n"
        "What: the shared Listmonk SMTP login belongs to another business.\n"
    )
    assert preflight.owner_actions_untracked_items(text) == []


def case_struck_through_heading_is_skipped():
    text = (
        "# Owner actions\n\n"
        "### ~~12. Regenerate the book cover.~~ DONE BY ME 2026-09-03.\n\n"
        "No issue needed, already closed.\n"
    )
    assert preflight.owner_actions_untracked_items(text) == []


def case_done_by_heading_is_skipped():
    text = (
        "# Owner actions\n\n"
        "### 9. HTTP/2 and HSTS. (www to apex: done by me 2026-09-17, no "
        "longer needs you.)\n\n"
        "Nothing left to do.\n"
    )
    assert preflight.owner_actions_untracked_items(text) == []


def case_narrative_heading_is_never_flagged():
    text = (
        "# Owner actions\n\n"
        "### New 2026-10-22: two commits on your PC never reached GitHub.\n\n"
        "No numbered-item shape, so this gate has no business judging it.\n"
    )
    assert preflight.owner_actions_untracked_items(text) == []


def case_issue_cited_anywhere_in_the_section_counts():
    text = (
        "# Owner actions\n\n"
        "### 22. Turn on the photos API.\n\n"
        "Some preamble text here.\n\n"
        "A later paragraph says: Tracked 2026-11-01 as GitHub issue #56.\n\n"
        "### 23. Next item.\n\n"
        "Unrelated body, no issue here on purpose, but a different test "
        "case covers that.\n"
    )
    # Only item 22 is asserted on; item 23's own lack of a citation would
    # also be flagged, which is correct and exercised by the first case.
    problems = preflight.owner_actions_untracked_items(text)
    assert "22. Turn on the photos API." not in problems, problems


def case_real_committed_file_has_no_item_14_or_15_problem():
    """The real file, read live: items 14 and 15 (the first ones this
    gate's own history fixed) must never regress back onto the list, even
    though several older low-urgency items (2, 4, 4b, 19, 20 and the
    "deploy it yourself" 1b) are expected to stay on it until a future
    cycle files issues for them too."""
    path = os.path.join(ROOT, "OWNER-ACTIONS.md")
    text = open(path, encoding="utf-8").read()
    problems = preflight.owner_actions_untracked_items(text)
    flat = " | ".join(problems)
    for must_be_clean in ("14. Create the Amazon KDP", "15. Create the Etsy",
                           "1. Authorise YouTube", "6. Accounts layer",
                           "8. Close two public ports",
                           "16. Create Pinterest"):
        assert must_be_clean not in flat, (must_be_clean, problems)


CASES = [
    case_open_item_with_no_issue_is_flagged,
    case_open_item_with_issue_is_silent,
    case_struck_through_heading_is_skipped,
    case_done_by_heading_is_skipped,
    case_narrative_heading_is_never_flagged,
    case_issue_cited_anywhere_in_the_section_counts,
    case_real_committed_file_has_no_item_14_or_15_problem,
]


def main() -> int:
    passed = 0
    for case in CASES:
        try:
            case()
        except AssertionError as e:
            print(f"  FAIL  {case.__name__}  {e}")
            continue
        print(f"  ok  {case.__name__}")
        passed += 1
    print(f"{passed}/{len(CASES)} cases passed")
    return 0 if passed == len(CASES) else 1


if __name__ == "__main__":
    sys.exit(main())
