#!/usr/bin/env python3
"""Archive OWNER-ACTIONS.md's fully-closed numbered items, leaving a
one-line pointer per item.

Found 2026-10-24, scheduled operator cycle, picking up the handoff the
04:4x PM check-in left: ops/rotate_owner_actions.py (2026-10-23) only ever
rotated ONE fixed, already-dead preamble span, and reports CLEAN today
because that span is empty. The actual 148KB of bloat is in "Open, ranked
by what they unblock", where several numbered items are not open at all:
their own header already says DONE / WITHDRAWN / Superseded / NO LONGER
NEEDED, two (items 10 and 12) merely duplicate R4 and R2 in the "Resolved
today" table above them, and nothing downstream (no gate, no dashboard
field) parses these items by number, so removing their body is safe.

This script only ever touches items whose own header text already
declares them closed; it does not read or judge any item that is still
genuinely open (the Gemini billing, YouTube, or "Start here" sections, for
instance, are correctly left alone: each still carries a live ask mixed
into its history, and splitting that safely is a different, larger job,
left for a future cycle exactly as this one was).

Usage:
    python ops/rotate_owner_actions_closed_items.py --check
    python ops/rotate_owner_actions_closed_items.py --apply
"""
import argparse
import datetime
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OA_PATH = os.path.join(ROOT, "OWNER-ACTIONS.md")
ARCHIVE_PATH = os.path.join(ROOT, "OWNER-ACTIONS-ARCHIVE.md")

# Each group is one or more adjacent "### " header spans that belong to the
# same numbered item. A group archives as one block, under one pointer.
# The first string in each group is also the pointer's own label source.
GROUPS = [
    ["### ~~1f. The VPS disk is 79% full.~~"],
    [
        "### ~~1a. Verify the site in Google Search Console.~~",
        "### (superseded) 1a. Verify the site in Google Search Console.",
    ],
    [
        "### ~~0. Set six secrets in the Ledgerium repo.~~",
        "### 0b. Superseded",
    ],
    [
        "### ~~1. Install one SSH key.~~",
        "### 1b. Superseded",
    ],
    [
        "### ~~3. Narration decision.~~",
        "### 3b. Withdrawn item, kept for the record",
    ],
    ["### ~~10. Fix the hourly operator routine's own STEP 0.~~"],
    ["### ~~12. Regenerate the book cover.~~"],
    ["### 4b. The original framing, which was wrong"],
]

POINTERS = {
    "### ~~1f. The VPS disk is 79% full.~~":
        "~~1f. The VPS disk is 79% full.~~ NO LONGER NEEDED, re-measured "
        "2026-09-20 at 40% used. Full text archived to "
        "`OWNER-ACTIONS-ARCHIVE.md`.",
    "### ~~1a. Verify the site in Google Search Console.~~":
        "~~1a. Verify the site in Google Search Console.~~ DONE BY PHIL "
        "(Domain property, DNS TXT, recorded 2026-10-14). The superseded "
        "original ask is archived to `OWNER-ACTIONS-ARCHIVE.md`.",
    "### ~~0. Set six secrets in the Ledgerium repo.~~":
        "~~0. Set six secrets in the Ledgerium repo.~~ DONE BY ME "
        "2026-09-01. Full text and its superseded follow-up archived to "
        "`OWNER-ACTIONS-ARCHIVE.md`.",
    "### ~~1. Install one SSH key.~~":
        "~~1. Install one SSH key.~~ DONE BY ME 2026-09-01. Full text and "
        "its superseded follow-up archived to `OWNER-ACTIONS-ARCHIVE.md`.",
    "### ~~3. Narration decision.~~":
        "~~3. Narration decision.~~ WITHDRAWN, it was never Phil's to "
        "make. Full text archived to `OWNER-ACTIONS-ARCHIVE.md`.",
    "### ~~10. Fix the hourly operator routine's own STEP 0.~~":
        "~~10. Fix the hourly operator routine's own STEP 0.~~ DONE "
        "2026-09-08, see R4 in \"Resolved today\" above (this item "
        "duplicated it). Full text archived to `OWNER-ACTIONS-ARCHIVE.md`.",
    "### ~~12. Regenerate the book cover.~~":
        "~~12. Regenerate the book cover.~~ DONE BY ME 2026-09-03, no "
        "machine needed, see R2 in \"Resolved today\" above (this item "
        "duplicated it). Full text archived to `OWNER-ACTIONS-ARCHIVE.md`.",
    "### 4b. The original framing, which was wrong":
        "4b. The original framing (superseded by item 4 above, which has "
        "the current ask). Full text archived to "
        "`OWNER-ACTIONS-ARCHIVE.md`.",
}


def _headers(lines):
    out = []
    for i, l in enumerate(lines):
        if l.startswith("### ") or l.startswith("## "):
            out.append((i, l.rstrip("\n")))
    out.append((len(lines), "EOF"))
    return out


def _find_span(headers, lines, label):
    matches = [i for i, (_, txt) in enumerate(headers) if txt.startswith(label)]
    if len(matches) > 1:
        raise SystemExit(
            f"refusing: expected at most one header starting with "
            f"{label!r}, found {len(matches)}"
        )
    if not matches:
        return None
    idx = matches[0]
    start_line, _ = headers[idx]
    end_line, _ = headers[idx + 1]
    return start_line, end_line


def plan(text):
    lines = text.split("\n")
    headers = _headers(lines)
    spans = []
    for group in GROUPS:
        pointer_line = "### " + POINTERS[group[0]]
        already_done = any(
            txt.rstrip() == pointer_line for _, txt in headers
        )
        if already_done:
            continue
        group_spans = [_find_span(headers, lines, label) for label in group]
        if all(s is None for s in group_spans):
            # None of this item's headers exist in this document at all
            # (e.g. a synthetic fixture that never had this item). Not
            # our concern; nothing to archive.
            continue
        if any(s is None for s in group_spans):
            missing = [
                label for label, s in zip(group, group_spans) if s is None
            ]
            raise SystemExit(
                f"refusing: group {group!r} is partially archived "
                f"(missing: {missing}); fix the anchors rather than "
                f"archive a mismatched span"
            )
        group_spans.sort()
        for a, b in zip(group_spans, group_spans[1:]):
            if a[1] != b[0]:
                raise SystemExit(
                    f"refusing: group {group!r} is not contiguous in the "
                    f"file (gap between line {a[1]} and {b[0]}); rewrite "
                    f"the anchors rather than archive a wrong span"
                )
        start = group_spans[0][0]
        end = group_spans[-1][1]
        spans.append((start, end, group[0]))
    spans.sort()
    for (s1, e1, _), (s2, e2, _) in zip(spans, spans[1:]):
        if e1 > s2:
            raise SystemExit("refusing: archive spans overlap")
    return lines, spans


def plan_rotation(text, today=None):
    """Pure function: returns (new_text, archive_entry_or_empty, due_bytes).

    archive_entry_or_empty is the full dated block ready to append to
    OWNER-ACTIONS-ARCHIVE.md, or "" if nothing is due. due_bytes is the
    size of the spans that would move, for --check's DUE/CLEAN decision.
    """
    lines, spans = plan(text)
    total = 0
    for start, end, _ in spans:
        total += len("\n".join(lines[start:end]).encode("utf-8"))
    if not spans:
        return text, "", 0

    today = today or datetime.date.today().isoformat()
    archive_chunks = []
    new_lines = list(lines)
    for start, end, label in reversed(spans):
        seg_text = "\n".join(new_lines[start:end]).rstrip("\n")
        archive_chunks.append(seg_text)
        pointer = "### " + POINTERS[label]
        new_lines[start:end] = [pointer, ""]
    archive_chunks.reverse()

    new_text = "\n".join(new_lines)
    archive_entry = (
        f"\n\n## Archived {today} by ops/rotate_owner_actions_closed_items.py\n\n"
        f"The following numbered items from \"Open, ranked by what they "
        f"unblock\" were already fully closed (DONE / WITHDRAWN / "
        f"Superseded by their own header), duplicated an entry already in "
        f"\"Resolved today\", or were explicitly labelled a wrong original "
        f"framing. None is a standing owner action. Moved verbatim.\n\n"
        + "\n\n---\n\n".join(archive_chunks)
        + "\n"
    )
    return new_text, archive_entry, total


def do_check():
    text = open(OA_PATH, encoding="utf-8").read()
    _, _, total = plan_rotation(text)
    if total == 0:
        print("CLEAN: no fully-closed numbered items left to archive.")
        return 0
    _, spans = plan(text)
    print(
        f"DUE: {total} bytes across {len(spans)} fully-closed numbered "
        f"items can be archived."
    )
    for _, _, label in spans:
        print(f"  - {label}")
    return 1


def do_apply():
    text = open(OA_PATH, encoding="utf-8").read()
    new_text, archive_entry, total = plan_rotation(text)
    if total == 0:
        print("CLEAN: nothing to do.")
        return 0

    with open(OA_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_text)
    with open(ARCHIVE_PATH, "a", encoding="utf-8", newline="\n") as f:
        f.write(archive_entry)

    _, spans = plan(text)
    print(f"APPLIED: archived {len(spans)} items.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if args.check:
        sys.exit(do_check())
    else:
        sys.exit(do_apply())


if __name__ == "__main__":
    main()
