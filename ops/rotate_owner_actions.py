#!/usr/bin/env python3
"""Move OWNER-ACTIONS.md's own superseded preamble history into
OWNER-ACTIONS-ARCHIVE.md, leaving one pointer sentence live.

Found 2026-10-23, scheduled operator cycle, the designated next cold-read
left by that day's section 30 fix (ops/rotate_checkin_log.py): the file
Phil reads directly to decide what needs him had the identical unbounded-
growth shape STATUS.md's "Production Knowledge" and "Immediate Focus"
fields had before ops/rotate_status_history.py rotated them. Between the
"List reviewed:" header and the "## Resolved today" table sat two distinct
chains, neither a standing owner action any more:

1. A deploy-gap narrative (2026-09-24/25): a sequence of bold-prefixed
   "Corrected"/"Widened"/"Reopened"/"RESOLVED"/"Added" paragraphs, each
   about a build-id/commit-count snapshot that is now tracked live by
   ops/deploy-verdict.json and STATUS.md's BLOCKER-001, not by this text.
   Unlike STATUS.md's own chain, this one is not reliably newest-first (a
   2026-09-24 entry follows a 2026-09-25 one), so "keep the newest, archive
   the rest" would risk keeping a stale paragraph live. Every entry in it
   is superseded regardless of position: the one fact worth keeping
   ("deploying is not Phil's job any more, item 0 below is") is already
   stated in the "Start here" table further down the file.
2. A one-sentence-per-item changelog ("Earlier: <date>, item N ...") going
   back to 2026-09-04, entirely narrating how individual numbered items
   changed over time. Every item it touches has its own live row in "Open,
   ranked by what they unblock" or the "Resolved today" table; this text
   adds nothing a cycle needs to read to decide what Phil should do today.

Both chains sit in the same bounded span (everything between the fixed
phrase that ends the "List reviewed" paragraph and the fixed "## Resolved
today" heading), so one rotation handles both at once: archive the whole
span verbatim, replace it with a short pointer. Nothing is deleted
(CLAUDE.md section 54); OWNER-ACTIONS-ARCHIVE.md keeps the full text.

Deliberately NOT touched: the "Last measured:" and "List reviewed:"
paragraphs above this span. Both are parsed by name for their first
sentence (ops/preflight.py's gate_goals_sessions_citations_current,
ops/dashboard.py's _owner_actions_traffic_citation), so rewriting them is a
different, higher-risk job than archiving an already-dead narrative, and is
left for a future cycle exactly as this file's own 2026-10-23 backlog entry
(section 30) deferred the "Resolved today"-style preamble work rather than
guess at it.

Extended 2026-10-24, scheduled operator cycle, to do the job this file's own
docstring above deferred: the "Last measured:" and "List reviewed:"
paragraphs it deliberately left untouched had grown the identical
unbounded-growth shape, one bold-prefixed "Corrected"/"Earlier, DATE:"
sentence at a time, exactly as section 32 of BACKLOG-2026-09-07.md predicted
when it named both as "the next candidate for this treatment." Each
paragraph's own load-bearing citation (the one sentence
ops/dashboard.py's _owner_actions_traffic_citation() or
ops/preflight.py's gate_owner_actions_last_measured_current actually reads)
sits at the very front, confirmed by reading both parsers directly rather
than guessing at the regex: the dashboard's own paragraph-capture regex and
the "list reviewed" header regex both match on the FIRST occurrence inside
the paragraph, so the real, current reading was never at risk, only hidden
inside everything appended after it. `--check-preamble`/`--apply-preamble`
rotate both paragraphs at once, the same way the two dead chains above were
rotated together: keep only the one load-bearing sentence (found fresh each
run, never a hardcoded date, because a real re-measurement is expected to
rewrite it in place), archive everything accumulated after it to
OWNER-ACTIONS-ARCHIVE.md, and replace it with a fixed, timeless pointer
sentence. The "List reviewed" marker's own standing definition (what
bumping its date does and does not mean, the real operational knowledge
behind the original closing clause) is folded permanently into that
pointer rather than kept as live prose that could grow again. Proved
against the real parsing functions before shipping: both regexes and both
gates still parse the rotated text clean (see
ops/tests/test_rotate_owner_actions.py's preamble cases, which call
ops.dashboard._owner_actions_traffic_citation and
ops.preflight.gate_owner_actions_last_measured_current directly against the
rotated text, not just against this script's own output).

Usage:
    python ops/rotate_owner_actions.py --check             report only
    python ops/rotate_owner_actions.py --apply             rotate now
    python ops/rotate_owner_actions.py --check-preamble    report only
    python ops/rotate_owner_actions.py --apply-preamble    rotate now
"""
import argparse
import datetime
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OA_PATH = os.path.join(ROOT, "OWNER-ACTIONS.md")
ARCHIVE_PATH = os.path.join(ROOT, "OWNER-ACTIONS-ARCHIVE.md")

# The historical span sits strictly between these two anchors. Neither
# names a date, so both stay valid after rotation and keep working as the
# ongoing gate's bounds, unlike a marker tied to the specific chain found
# today. "it says nothing about traffic." is the last sentence of the
# untouched "List reviewed:" paragraph; "## Resolved today" is the next
# heading in the file. Both are currently unique; a script that cannot
# find exactly one of each refuses rather than guesses which text to move.
REGION_START_AFTER = "it says nothing about traffic."
REGION_END_BEFORE = "\n\n---\n\n## Resolved today"

ARCHIVE_HEADER_FIRST_LINE = "# OWNER-ACTIONS.md archive"

REPLACEMENT = (
    "**Deploy-gap and per-item history, 2026-09-04 through 2026-09-25, "
    "archived 2026-10-23 by `ops/rotate_owner_actions.py`:** none of it is "
    "a standing owner action any more. Current deploy status lives in "
    "`STATUS.md`'s `BLOCKER-001`; the one still-open ask this chain ever "
    "raised is item 0 below (`VPS_DEPLOY_KEY`). Moved verbatim to "
    "`OWNER-ACTIONS-ARCHIVE.md`."
)

# A WARNING-not-FAIL buffer, same reasoning as gate_status_immediate_focus_
# not_oversized: a long region wastes a future cycle's reading time, it
# does not ship anything broken to a customer. 400 bytes comfortably fits
# REPLACEMENT itself (currently ~370 bytes) plus normal whitespace drift.
SIZE_BUFFER_BYTES = 400

# The "Last measured:" paragraph re-measures every so often (a real session
# with a VPS key edits the date and the numbers in place), so the boundary
# that matters cannot be a fixed string tied to today's reading -- it has to
# be found the same way ops/dashboard.py's _owner_actions_traffic_citation()
# finds it, every time this runs. LM_CITATION_RE matches exactly the
# sentence that function and gate_dashboard_owner_actions_traffic_citation_
# current both require; everything from the end of that match up to the
# next paragraph is pure accumulated correction history with its own live
# duplicate elsewhere (item 1, "Authorise YouTube uploads").
LM_CITATION_RE = re.compile(
    r"\*\*Last measured:\*\*\s*"
    r"(\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2})?)\s*UTC,?\s*"
    r"traffic re-measured by a direct database read:\s*"
    r"(\d+)\s*visitors?/\s*(\d+)\s*visits?/\s*30\s+days",
    re.S)
LM_END_BEFORE = "\n\n**List reviewed:**"
# Deliberately generic and evergreen: whatever accumulates here between
# rotations will not always be about the same item, so the live pointer
# names no specific topic. Nothing is lost either way; the full text,
# whatever it was about, is always in OWNER-ACTIONS-ARCHIVE.md verbatim.
LM_REPLACEMENT = (
    ". Earlier corrections accumulated here between rotations archived to "
    "`OWNER-ACTIONS-ARCHIVE.md` by `ops/rotate_owner_actions.py "
    "--apply-preamble`; each numbered item's own current status lives in "
    "its own entry below, not in this paragraph."
)

# The "List reviewed:" header only ever needs to carry its own date
# (gate_owner_actions_last_measured_current reads nothing else from it), so
# the live KEEP text is the header and date alone; LR_END_BEFORE is the
# fixed, timeless pointer phrase ops/rotate_owner_actions.py's OTHER
# rotation (the deploy-gap/per-item-history span, section 31) already
# replaced its own neighbour with, so it never changes underneath this one.
# The real operational knowledge from the old closing clause (why this
# marker is separate from "Last measured" and must never be bumped to imply
# a fresh traffic read) is folded into LR_REPLACEMENT itself, permanently,
# rather than kept as live prose that could grow again.
LR_DATE_RE = re.compile(r"\*\*List reviewed:\*\*\s*(\d{4}-\d{2}-\d{2})")
LR_END_BEFORE = "\n\n**Deploy-gap and per-item history"
# Timeless on purpose: this restates the marker's own standing definition
# (what bumping the date does and does not mean) rather than claiming any
# particular cycle's review happened, since that claim belongs to whoever
# bumps the date, not to this mechanical rotation.
LR_REPLACEMENT = (
    ", every item below has been read as of this date. A separate marker, "
    "\"Last measured\" above (issue #38), is the exact sentence the "
    "dashboard parses for the real traffic-measurement date; bumping this "
    "marker must never imply a fresh database read. Earlier review "
    "history accumulated here between rotations archived to "
    "`OWNER-ACTIONS-ARCHIVE.md` by `ops/rotate_owner_actions.py "
    "--apply-preamble`."
)

PREAMBLE_BUFFER_BYTES = 400


def _lm_region(text: str):
    """(citation_end_index, region_end_index). Raises ValueError if the
    citation sentence or the next paragraph's header cannot be found.
    """
    m = LM_CITATION_RE.search(text)
    if not m:
        raise ValueError("'Last measured' citation sentence not found or "
                          "no longer matches the shape dashboard.py and "
                          "preflight.py both require")
    end_idx = text.find(LM_END_BEFORE, m.end())
    if end_idx == -1:
        raise ValueError("'List reviewed' header not found after the "
                          "'Last measured' citation")
    return m.end(), end_idx


def _lr_region(text: str):
    """(date_end_index, region_end_index). Raises ValueError if the header
    date or the deploy-gap pointer that follows it cannot be found.
    """
    m = LR_DATE_RE.search(text)
    if not m:
        raise ValueError("'List reviewed' header date not found")
    end_idx = text.find(LR_END_BEFORE, m.end())
    if end_idx == -1:
        raise ValueError("deploy-gap/per-item-history pointer not found "
                          "after the 'List reviewed' date")
    return m.end(), end_idx


def region_between(text: str, start_after: str, end_before: str):
    """Return (before, region, after) where region is everything strictly
    between the end of start_after and the start of end_before. Raises
    ValueError if either anchor is missing, duplicated, or end_before does
    not follow start_after -- refuse to guess rather than move the wrong
    text.
    """
    if text.count(start_after) != 1:
        raise ValueError("start anchor missing or duplicated: %r"
                          % start_after)
    if text.count(end_before) != 1:
        raise ValueError("end anchor missing or duplicated: %r" % end_before)
    start = text.find(start_after) + len(start_after)
    end = text.find(end_before, start)
    if end == -1:
        raise ValueError("end anchor does not follow start anchor")
    return text[:start], text[start:end], text[end:]


def region_size(text: str, start_after: str = REGION_START_AFTER,
                 end_before: str = REGION_END_BEFORE) -> int:
    """Pure function used by the preflight gate: bytes of live history
    still sitting in the bounded span, stripped of surrounding whitespace.
    Raises ValueError if the anchors cannot be found (same refusal as
    region_between). Defaults to the deploy-gap/per-item-history span;
    pass LM_START_AFTER/LM_END_BEFORE or LR_START_AFTER/LR_END_BEFORE for
    the two preamble paragraphs.
    """
    _, region, _ = region_between(text, start_after, end_before)
    return len(region.strip().encode("utf-8"))


def preamble_sizes(text: str):
    """(last_measured_region_bytes, list_reviewed_region_bytes), each the
    live, un-rotated history still sitting in that paragraph. Raises
    ValueError if either paragraph has been reworded away from the shape
    this script expects.
    """
    s, e = _lm_region(text)
    lm = len(text[s:e].strip().encode("utf-8"))
    s, e = _lr_region(text)
    lr = len(text[s:e].strip().encode("utf-8"))
    return lm, lr


def plan_rotation_preamble(text: str):
    """Pure function, same contract as plan_rotation() above but for both
    preamble paragraphs at once. Returns (new_text, archived_blocks) where
    archived_blocks is a list of (label, content) pairs for whichever
    paragraph(s) still carry more than their own pointer sentence; a
    paragraph already at its pointer is left out of the list entirely.
    """
    archived_blocks = []

    s, e = _lm_region(text)
    region = text[s:e]
    if region.strip() != LM_REPLACEMENT.strip():
        archived_blocks.append(("Last measured", region.strip()))
        text = text[:s] + LM_REPLACEMENT + text[e:]

    s, e = _lr_region(text)
    region = text[s:e]
    if region.strip() != LR_REPLACEMENT.strip():
        archived_blocks.append(("List reviewed", region.strip()))
        text = text[:s] + LR_REPLACEMENT + text[e:]

    return text, archived_blocks


def plan_rotation(text: str):
    """Pure function. Returns (new_text, archived_region). archived_region
    is "" if the span already equals REPLACEMENT (nothing to move).
    """
    before, region, after = region_between(
        text, REGION_START_AFTER, REGION_END_BEFORE)
    if region.strip() == REPLACEMENT.strip():
        return text, ""
    new_text = before + "\n\n" + REPLACEMENT + after
    return new_text, region.strip()


def apply_archive(archived_region: str, existing_archive_text) -> str:
    """Same prepend-above-existing-content shape as
    ops/rotate_status_history.py's apply_archive, so repeated runs keep
    extending one growing archive instead of reordering it.
    """
    block = archived_region.strip() + "\n"
    if existing_archive_text:
        if not existing_archive_text.startswith(ARCHIVE_HEADER_FIRST_LINE):
            raise ValueError("OWNER-ACTIONS-ARCHIVE.md does not start with "
                              "the expected header; refusing to guess.")
        marker = "\n---\n"
        at = existing_archive_text.find(marker)
        if at == -1:
            raise ValueError("OWNER-ACTIONS-ARCHIVE.md has no '---' "
                              "divider after its header; refusing to guess.")
        head = existing_archive_text[:at + len(marker)]
        tail = existing_archive_text[at + len(marker):]
        return head + "\n" + block + "\n" + tail.lstrip("\n")
    header = (ARCHIVE_HEADER_FIRST_LINE + "\n\n"
              "> Historical entries moved here by "
              "ops/rotate_owner_actions.py. Nothing here was edited on "
              "the way over; CLAUDE.md section 54 says the record must "
              "survive.\n\n---\n")
    return header + "\n" + block + "\n"


def format_preamble_archive_blocks(archived_blocks) -> str:
    """Render plan_rotation_preamble()'s (label, content) pairs as one
    archive-ready block, each under its own sub-heading so a later reader
    can tell which paragraph a given piece of history came from.
    """
    parts = []
    for label, content in archived_blocks:
        today = datetime.date.today().isoformat()
        parts.append("### %s, archived %s\n\n%s" % (label, today, content))
    return "\n\n".join(parts)


def _write_rotated(new_text: str, archived_region: str) -> None:
    existing_archive_text = None
    if os.path.exists(ARCHIVE_PATH):
        existing_archive_text = io.open(ARCHIVE_PATH, encoding="utf-8").read()
    new_archive_text = apply_archive(archived_region, existing_archive_text)

    archive_tmp = ARCHIVE_PATH + ".tmp"
    io.open(archive_tmp, "w", encoding="utf-8").write(new_archive_text)
    os.replace(archive_tmp, ARCHIVE_PATH)

    oa_tmp = OA_PATH + ".tmp"
    io.open(oa_tmp, "w", encoding="utf-8").write(new_text)
    os.replace(oa_tmp, OA_PATH)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true",
                     help="report whether rotation is due; makes no "
                          "changes.")
    ap.add_argument("--apply", action="store_true",
                     help="rotate now: archive the historical span, leave "
                          "the pointer sentence live.")
    ap.add_argument("--check-preamble", action="store_true",
                     help="report whether the 'Last measured'/'List "
                          "reviewed' paragraphs have regrown; makes no "
                          "changes.")
    ap.add_argument("--apply-preamble", action="store_true",
                     help="rotate the 'Last measured'/'List reviewed' "
                          "paragraphs now.")
    args = ap.parse_args()
    if sum([args.check, args.apply, args.check_preamble,
            args.apply_preamble]) != 1:
        ap.error("pass exactly one of --check, --apply, --check-preamble, "
                  "--apply-preamble")

    text = io.open(OA_PATH, encoding="utf-8").read()

    if args.check_preamble or args.apply_preamble:
        try:
            lm_size, lr_size = preamble_sizes(text)
        except ValueError as exc:
            print("REFUSING: %s" % exc)
            return 2
        lm_replacement_size = len(LM_REPLACEMENT.encode("utf-8"))
        lr_replacement_size = len(LR_REPLACEMENT.encode("utf-8"))
        due = (lm_size > lm_replacement_size + PREAMBLE_BUFFER_BYTES or
               lr_size > lr_replacement_size + PREAMBLE_BUFFER_BYTES)

        if args.check_preamble:
            if due:
                print("DUE: Last measured %d bytes (pointer %d), List "
                      "reviewed %d bytes (pointer %d); would move the "
                      "excess to %s on --apply-preamble."
                      % (lm_size, lm_replacement_size, lr_size,
                         lr_replacement_size, ARCHIVE_PATH))
                return 1
            print("CLEAN: Last measured %d bytes, List reviewed %d bytes, "
                  "both at or near their own pointer sentence's size."
                  % (lm_size, lr_size))
            return 0

        # --apply-preamble
        new_text, archived_blocks = plan_rotation_preamble(text)
        if not archived_blocks:
            print("Already rotated; no change made.")
            return 0
        combined = format_preamble_archive_blocks(archived_blocks)
        _write_rotated(new_text, combined)
        print("Moved %d bytes (%s) to %s."
              % (len(combined.encode("utf-8")),
                 ", ".join(label for label, _ in archived_blocks),
                 ARCHIVE_PATH))
        return 0

    try:
        size = region_size(text)
    except ValueError as exc:
        print("REFUSING: %s" % exc)
        return 2

    replacement_size = len(REPLACEMENT.encode("utf-8"))
    due = size > replacement_size + SIZE_BUFFER_BYTES

    if args.check:
        if due:
            print("DUE: %d bytes of preamble history live (pointer alone "
                  "is %d); would move to %s on --apply."
                  % (size, replacement_size, ARCHIVE_PATH))
            return 1
        print("CLEAN: %d bytes live, at or near the pointer sentence's own "
              "size. Nothing to rotate." % size)
        return 0

    # --apply
    new_text, archived_region = plan_rotation(text)
    if not archived_region:
        print("Already rotated; no change made.")
        return 0
    _write_rotated(new_text, archived_region)
    print("Moved %d bytes of preamble history to %s."
          % (len(archived_region.encode("utf-8")), ARCHIVE_PATH))
    return 0


if __name__ == "__main__":
    sys.exit(main())
