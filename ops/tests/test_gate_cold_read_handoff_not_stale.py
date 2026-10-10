#!/usr/bin/env python3
"""
Prove ops/preflight.py's cold_read_handoff_stale_files() catches a
NIGHTLY-LOG.md handoff naming an ops/*.py cold-read candidate that
ops/cold-read-ledger.json already records as read.

Found live 2026-09-25: the newest handoff named five files as "genuinely
unread" that had all already been cold-read and cleared or fixed between
2026-09-08 and 2026-09-24 (build_feed.py, build_image_prompts.py,
build_printpack.py, canonical_links.py, room_image_variants.py). This
tests the pure logic with synthetic text, so it never touches the real
committed log or ledger.

Run:  python ops/tests/test_gate_cold_read_handoff_not_stale.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

LEDGER = {
    "build_feed.py": {"status": "clean", "date": "2026-09-10", "note": "x"},
    "canonical_links.py": {"status": "clean", "date": "2026-09-11", "note": "x"},
    "affiliate_report.py": {"status": "fixed", "date": "2026-09-24", "note": "x"},
    "videoLink.js": {"status": "clean", "date": "2026-09-27", "note": "x"},
}


def main() -> int:
    fails = []

    # 1. The real defect shape: the newest entry's own handoff names a
    #    bare and an ops/-prefixed filename, both already in the ledger.
    log = (
        "# Nightly log\n\nnewest first\n\n"
        "## 2026-09-25, cycle\n\n"
        "NEXT FOR THE OPERATOR: continue the cold-read lane, "
        "`build_feed.py`, `ops/canonical_links.py`, `crawl_report.py`.\n\n"
        "Pushed to main.\n\n"
        "## 2026-09-24, cycle\n\nolder entry, irrelevant\n"
    )
    stale = preflight.cold_read_handoff_stale_files(log, LEDGER)
    if set(stale) != {"build_feed.py", "canonical_links.py"}:
        fails.append("did not catch the two ledgered names: got %r" % stale)

    # 1b. A name inside ~~strikethrough~~ is a correction, already
    #     acknowledged as stale in the file's own established markdown,
    #     not a live handoff: it must not be flagged.
    log_struck = (
        "# Nightly log\n\nnewest first\n\n"
        "## 2026-09-25, cycle\n\n"
        "NEXT FOR THE OPERATOR: cold-read the files, "
        "~~`build_feed.py`, `canonical_links.py`~~, corrected below, "
        "and `crawl_report.py`.\n"
    )
    stale = preflight.cold_read_handoff_stale_files(log_struck, LEDGER)
    if stale:
        fails.append("a struck-through, already-corrected name was "
                      "wrongly flagged: %r" % stale)

    # 2. A clean handoff naming only genuinely un-ledgered files must not
    #    warn.
    log_clean = log.replace(
        "`build_feed.py`, `ops/canonical_links.py`, `crawl_report.py`",
        "`crawl_report.py`, `build_epub.py`")
    stale = preflight.cold_read_handoff_stale_files(log_clean, LEDGER)
    if stale:
        fails.append("a clean handoff was wrongly flagged: %r" % stale)

    # 3. "**Next:**" phrasing (the PM check-in style) must be recognised
    #    too, not only "NEXT FOR THE OPERATOR:".
    log_next_style = (
        "# Nightly log\n\nnewest first\n\n"
        "## PM check-in, 2026-09-25\n\n"
        "**Next:** cold-read `affiliate_report.py` and `crawl_report.py`.\n\n"
        "Pushed to main.\n"
    )
    stale = preflight.cold_read_handoff_stale_files(log_next_style, LEDGER)
    if stale != ["affiliate_report.py"]:
        fails.append("**Next:** phrasing not recognised: got %r" % stale)

    # 4. A stale name in the SECOND entry (still within the last-four-
    #    entries span STEP 1 reads) must be caught, matching the real
    #    2026-09-25 defect shape (the stale handoff was the third-newest
    #    entry, not the newest).
    log_second_entry = (
        "# Nightly log\n\nnewest first\n\n"
        "## 2026-09-25, cycle two\n\n"
        "**Next:** nothing new, backlog exhausted.\n\n"
        "## 2026-09-25, cycle one\n\n"
        "NEXT FOR THE OPERATOR: cold-read `build_feed.py`.\n"
    )
    stale = preflight.cold_read_handoff_stale_files(log_second_entry, LEDGER)
    if stale != ["build_feed.py"]:
        fails.append("a stale name in the second entry was not caught: %r"
                      % stale)

    # 3b. "**Handing to operator:**"/"Handing to the operator:" (bold
    #     or not) must be recognised too: 64 uses across the real log's
    #     own history, and the exact phrasing the live 2026-09-25 defect
    #     used for its genuinely fresh handoff, invisible to the gate
    #     until this case was added.
    log_handing_style = (
        "# Nightly log\n\nnewest first\n\n"
        "## PM check-in, 2026-09-25\n\n"
        "**Handing to operator:** cold-read `affiliate_report.py` and "
        "`crawl_report.py`.\n\n"
        "Pushed to main.\n"
    )
    stale = preflight.cold_read_handoff_stale_files(log_handing_style, LEDGER)
    if stale != ["affiliate_report.py"]:
        fails.append("**Handing to operator:** phrasing not recognised: "
                      "got %r" % stale)

    log_handing_the_style = (
        "# Nightly log\n\nnewest first\n\n"
        "## 2026-09-25, cycle\n\n"
        "Handing to the operator: cold-read `affiliate_report.py`.\n"
    )
    stale = preflight.cold_read_handoff_stale_files(
        log_handing_the_style, LEDGER)
    if stale != ["affiliate_report.py"]:
        fails.append("unbolded 'Handing to the operator:' phrasing not "
                      "recognised: got %r" % stale)

    # 3c. A name inside a parenthetical aside, cited as already ledgered
    #     clean right beside the live candidate, is the same shape as a
    #     ~~strikethrough~~ correction (not a live handoff) and must not
    #     be flagged. Found live 2026-09-26: this exact real log line
    #     ("...at `ops/dashboard.py` (`ship.py` and `fix_dashes.py` both
    #     ledgered clean by the concurrent cycle below)...") tripped the
    #     gate on `ship.py`/`fix_dashes.py` even though the live
    #     candidate, `dashboard.py`, is genuinely un-ledgered.
    log_paren_aside = (
        "# Nightly log\n\nnewest first\n\n"
        "## PM check-in, 2026-09-26\n\n"
        "**Next:** cold-read lane continues per `ops/cold_read_ledger.py "
        "--next` at `ops/crawl_report.py` (`build_feed.py` and "
        "`canonical_links.py` both ledgered clean by the concurrent cycle "
        "below). Standing Phil-blocked list unchanged.\n"
    )
    stale = preflight.cold_read_handoff_stale_files(log_paren_aside, LEDGER)
    if stale:
        fails.append("a parenthetical already-cleared aside was wrongly "
                      "flagged: %r" % stale)

    # 4b. But a stale name past the max_entries window (the sixth entry,
    #     with the default window of 4) must NOT be caught: that is
    #     older history, not the live handoff a fresh cycle will read.
    log_far_entry = "\n\n".join(
        ["# Nightly log\n\nnewest first"] +
        ["## 2026-09-2%d, cycle %d\n\n**Next:** nothing new." % (5 - i, i)
         for i in range(5)] +
        ["## 2026-09-19, cycle old\n\n"
         "NEXT FOR THE OPERATOR: cold-read `build_feed.py`."])
    stale = preflight.cold_read_handoff_stale_files(log_far_entry, LEDGER)
    if stale:
        fails.append("an entry outside the 4-entry window was wrongly "
                      "checked: %r" % stale)

    # 5. A stale name in an OLDER entry inside the window must NOT be
    #    flagged once a NEWER entry in the same window already names a
    #    live (non-stale) candidate: the newer handoff supersedes the
    #    older one, and a fresh cycle reading newest-first would hit the
    #    newer one first and never act on the stale mention. Found live
    #    2026-09-26: the real log had exactly this shape, a superseded
    #    "cold-read lane continues at `ops/dashboard.py`" two entries
    #    back, after `dashboard.py` was ledgered fixed and two newer
    #    entries in the same window had already moved on to a genuinely
    #    un-ledgered file.
    log_superseded = (
        "# Nightly log\n\nnewest first\n\n"
        "## 2026-09-26, cycle three\n\n"
        "**Next:** cold-read lane continues at `crawl_report.py`, the "
        "next un-ledgered file.\n\n"
        "## 2026-09-26, cycle two\n\n"
        "Some unrelated PM check-in text with no handoff line at all.\n\n"
        "## 2026-09-26, cycle one\n\n"
        "Handing to the operator: cold-read lane continues at "
        "`build_feed.py`, unchanged.\n"
    )
    stale = preflight.cold_read_handoff_stale_files(log_superseded, LEDGER)
    if stale:
        fails.append("a superseded older-entry mention was wrongly "
                      "flagged even though a newer entry in the same "
                      "window already named a live candidate: %r" % stale)

    # 6. Extended 2026-09-27 to also cover the JS lanes ops/cold_read_ledger.py
    #    tracks (site/assets/js/*.js, mobile/quest-app/lib/*.js). A handoff
    #    naming an already-ledgered .js file, with or without its lane
    #    prefix, must be caught the same way a .py one is; a *.test.js
    #    name must never be, since tests are not ledgered on their own.
    log_js = (
        "# Nightly log\n\nnewest first\n\n"
        "## 2026-09-27, cycle\n\n"
        "**Next:** cold-read `mobile/quest-app/lib/videoLink.js`, "
        "`videoLink.test.js` and `format.js`.\n"
    )
    stale = preflight.cold_read_handoff_stale_files(log_js, LEDGER)
    if stale != ["videoLink.js"]:
        fails.append("a ledgered .js file (with or without its lane "
                     "prefix) was not caught, or a .test.js/unledgered "
                     "name was wrongly caught: got %r" % stale)

    # 7. A newest entry that names a file only to explain it was already
    #    closed elsewhere ("none from this entry (the intended handoff,
    #    `X`, was closed concurrently...)") must be treated as this
    #    window's authoritative state, empty result included, and must
    #    NOT fall through to an older entry's now-stale handoff for a
    #    DIFFERENT file. Found live 2026-09-27: the real log had exactly
    #    this shape, and the old code (which conflated "handoff line
    #    present, zero names survived stripping" with "no handoff line at
    #    all") fell through past this entry and a second, similarly empty
    #    one to a third-newest entry's real but by-then-stale "site.js"/
    #    "quest.js" handoff, flagging both as if still live.
    log_explained_closed = (
        "# Nightly log\n\nnewest first\n\n"
        "## PM check-in, 2026-09-27 cycle three\n\n"
        "**Next:** none from this entry (the intended handoff, "
        "`build_feed.py`, was closed concurrently by the operator cycle "
        "below).\n\n"
        "## 2026-09-27, cycle two\n\n"
        "**Next:** the cold-read lane is closed. No unread file remains.\n\n"
        "## 2026-09-27, cycle one\n\n"
        "**Next:** `build_feed.py` and `canonical_links.py` remain in "
        "the cold-read lane.\n"
    )
    stale = preflight.cold_read_handoff_stale_files(log_explained_closed, LEDGER)
    if stale:
        fails.append("a newest entry explaining a name was already closed "
                     "elsewhere wrongly fell through to an older entry's "
                     "stale handoff: %r" % stale)

    # 8. "**Next for the operator:**" (45 uses across the real log) and
    #    its siblings ("**Next for operator:**", "**Next for the operator
    #    (:43):**", "NEXT FOR THE OPERATOR, as of this check-in:", "NEXT
    #    FOR WHOEVER PICKS THIS UP:") must be recognised the same way
    #    "**Next:**" already is. Found live 2026-09-27: the newest entry's
    #    own handoff used "**Next for operator:**" naming a genuinely
    #    fresh, un-ledgered file; the old exact-string match could not see
    #    that header at all, so the block looked file-less and the gate
    #    fell through to an older, superseded "NEXT FOR THE OPERATOR:"
    #    handoff naming a file already ledgered clean, flagging that one
    #    instead of trusting the newest entry's own live candidate.
    log_next_for_operator = (
        "# Nightly log\n\nnewest first\n\n"
        "## PM check-in, 2026-09-27 16:1x\n\n"
        "**Next for operator:** cold-read lane continues at "
        "`crawl_report.py`, the next un-ledgered file.\n\n"
        "## PM check-in, 2026-09-27 15:4x\n\n"
        "NEXT FOR THE OPERATOR: cold-read `build_feed.py`.\n"
    )
    stale = preflight.cold_read_handoff_stale_files(
        log_next_for_operator, LEDGER)
    if stale:
        fails.append("'**Next for operator:**' not recognised, fell "
                     "through to a superseded older handoff: %r" % stale)

    log_next_for_the_operator_variants = (
        "# Nightly log\n\nnewest first\n\n"
        "## PM check-in, 2026-09-27\n\n"
        "**Next for the operator (:43):** cold-read `affiliate_report.py` "
        "and `crawl_report.py`.\n"
    )
    stale = preflight.cold_read_handoff_stale_files(
        log_next_for_the_operator_variants, LEDGER)
    if stale != ["affiliate_report.py"]:
        fails.append("'**Next for the operator (:43):**' phrasing not "
                     "recognised: got %r" % stale)

    log_next_for_all_caps_variant = (
        "# Nightly log\n\nnewest first\n\n"
        "## 2026-09-27, cycle\n\n"
        "NEXT FOR THE OPERATOR, as of this check-in: cold-read "
        "`affiliate_report.py`.\n"
    )
    stale = preflight.cold_read_handoff_stale_files(
        log_next_for_all_caps_variant, LEDGER)
    if stale != ["affiliate_report.py"]:
        fails.append("'NEXT FOR THE OPERATOR, as of this check-in:' "
                     "phrasing not recognised: got %r" % stale)

    # 9. A bare (non-parenthetical) "already/just fixed/cleared/resolved
    #    in `X`" citation, naming precedent for a DIFFERENT live
    #    candidate, must not itself be flagged. Found live 2026-09-27:
    #    the real handoff line named four live candidates by line number
    #    (never matched by name_re, since a trailing `:NNN` breaks the
    #    backtick-adjacency the regex requires) and, in the same
    #    sentence but outside any parentheses, cited a fifth, already-
    #    fixed file as precedent ("...the exact bug shape the 15:1x
    #    cycle just fixed in `fill_front_matter.py`..."). Because that
    #    citation was the only name name_re could match anywhere in the
    #    block, it alone became the block's "names" list and tripped the
    #    gate on a file with nothing left to read.
    log_bare_precedent = (
        "# Nightly log\n\nnewest first\n\n"
        "## PM check-in, 2026-09-27\n\n"
        "NEXT FOR THE OPERATOR: harden `ops/prerender_shop.py:139` and "
        "`ops/wire_pwa.py:79`'s repl calls, because they share the exact "
        "bug shape the 15:1x cycle just fixed in `build_feed.py`.\n"
    )
    stale = preflight.cold_read_handoff_stale_files(
        log_bare_precedent, LEDGER)
    if stale:
        fails.append("a bare 'just fixed in `X`' precedent citation was "
                     "wrongly flagged as a live stale handoff: %r" % stale)

    # 10. A genuine handoff's own trailing advice sentence, naming a
    #     tool purely as the subject of a hypothetical "if a future
    #     cycle runs `X`..." instruction about how to invoke it later,
    #     must not itself be flagged as a stale candidate. Found live
    #     2026-09-27 (third time): the real newest entry's own "**Next:**
    #     same standing Phil-blocked list..., unchanged. If a future
    #     cycle runs `preflight.py` directly rather than through this
    #     operator's own tooling, let it run to completion in the
    #     background..." named no candidate at all, yet tripped the gate
    #     on `preflight.py`, already ledgered clean.
    log_hypothetical_advice = (
        "# Nightly log\n\nnewest first\n\n"
        "## PM check-in, 2026-09-27\n\n"
        "**Next:** same standing Phil-blocked list, unchanged. If a "
        "future cycle runs `build_feed.py` directly rather than through "
        "this operator's own tooling, let it run to completion in the "
        "background rather than a foreground `timeout` call; 300 "
        "seconds is not always enough.\n"
    )
    stale = preflight.cold_read_handoff_stale_files(
        log_hypothetical_advice, LEDGER)
    if stale:
        fails.append("a hypothetical 'if a future cycle runs `X`' advice "
                     "clause was wrongly flagged as a stale handoff: %r"
                     % stale)

    # 11. A genuine "let the still-running `X` finish" handoff, naming a
    #     file that was a mid-execution PROCESS to wait on rather than a
    #     cold-read candidate, must not itself be flagged. Found live
    #     2026-10-10: the real newest entry with a recognised handoff
    #     line said "NEXT FOR THE OPERATOR: there is no new unblocked
    #     item; let the still-running `preflight.py` (stuck at the
    #     documented `gate_tests` sandbox hang past 20 minutes) finish
    #     and act on its real exit code rather than starting a fresh
    #     sweep", naming no read candidate at all, yet tripped the gate
    #     on `preflight.py`, already ledgered clean.
    log_still_running = (
        "# Nightly log\n\nnewest first\n\n"
        "## PM check-in, 2026-10-10\n\n"
        "NEXT FOR THE OPERATOR: there is no new unblocked item; let the "
        "still-running `build_feed.py` (stuck at the documented "
        "`gate_tests` sandbox hang past 20 minutes) finish and act on "
        "its real exit code rather than starting a fresh sweep.\n"
    )
    stale = preflight.cold_read_handoff_stale_files(log_still_running, LEDGER)
    if stale:
        fails.append("a 'let the still-running `X` finish' handoff was "
                     "wrongly flagged as a stale cold-read candidate: %r"
                     % stale)

    log_backgrounded = (
        "# Nightly log\n\nnewest first\n\n"
        "## 2026-10-10, cycle\n\n"
        "**Next:** let the backgrounded `build_feed.py` finish before "
        "starting anything new.\n"
    )
    stale = preflight.cold_read_handoff_stale_files(log_backgrounded, LEDGER)
    if stale:
        fails.append("a 'backgrounded `X`' handoff was wrongly flagged: "
                     "%r" % stale)

    # 12. A genuine "standing N-file rotation cold-read tier from `X`"
    #     handoff must not be flagged, even though `X` is ledgered clean:
    #     being ledgered is the precondition for entering the rotation
    #     (every un-ledgered candidate ran out at 197 of 197), not
    #     evidence the handoff is stale. Found live 2026-10-10 (second
    #     time): "the standing 37-file rotation cold-read tier from
    #     `build_garage_deck_page.py`" tripped the plain membership check.
    log_rotation = (
        "# Nightly log\n\nnewest first\n\n"
        "## PM check-in, 2026-10-10\n\n"
        "**Handing to the operator:** the standing 37-file rotation "
        "cold-read tier from `build_feed.py`; the deliberate sweep.\n"
    )
    stale = preflight.cold_read_handoff_stale_files(log_rotation, LEDGER)
    if stale:
        fails.append("a 'standing N-file rotation cold-read tier from "
                     "`X`' handoff was wrongly flagged as stale: %r"
                     % stale)
    # And a genuinely fresh, non-rotation name in the SAME block must
    # still be caught: this strip must not blind the gate to a real
    # stale candidate sitting right next to a legitimate rotation one.
    log_rotation_plus_stale = (
        "# Nightly log\n\nnewest first\n\n"
        "## PM check-in, 2026-10-10\n\n"
        "**Handing to the operator:** the standing 37-file rotation "
        "cold-read tier from `build_feed.py`; also re-check "
        "`canonical_links.py`.\n"
    )
    stale = preflight.cold_read_handoff_stale_files(
        log_rotation_plus_stale, LEDGER)
    if set(stale) != {"canonical_links.py"}:
        fails.append("the rotation strip swallowed an adjacent real "
                     "stale candidate: %r" % stale)

    # 13. "**Handing to the operator (oversized for 30 minutes):**" must
    #     be recognised as a live handoff header, same as the plain
    #     "**Handing to the operator:**" form: a parenthetical aside
    #     between "operator" and the closing "**" must not blind the
    #     gate to the true newest block. Found live 2026-10-10 (third
    #     time): the real newest entry used this exact header and the
    #     gate, unable to match it, fell through to an older, different-
    #     worded rotation handoff two blocks back and flagged it stale.
    log_aside_header = (
        "# Nightly log\n\nnewest first\n\n"
        "## PM check-in, 2026-10-10\n\n"
        "**Handing to the operator (oversized for 30 minutes):** the "
        "standing 37-file rotation cold-read tier from "
        "`build_feed.py`; the deliberate sweep.\n\n"
        "## older entry\n\n"
        "NEXT FOR THE OPERATOR: cold-read `canonical_links.py`.\n"
    )
    stale = preflight.cold_read_handoff_stale_files(log_aside_header, LEDGER)
    if stale:
        fails.append("a 'Handing to the operator (aside):' header was not "
                     "recognised, so an older block's stale name leaked "
                     "through: %r" % stale)

    # Deliberately no "check the real committed log" case here: the log
    # gains new entries constantly (many times a day, per its own
    # history), so whether a specific past entry's handoff still sits
    # inside the 4-entry window is a fact about wall-clock repository
    # state, not this gate's logic, and asserting it in a committed
    # regression test would make the test fail on nothing but the
    # passage of time. The synthetic cases above fully exercise the
    # logic; the live preflight gate (a WARNING, not a FAIL) is what
    # watches the real, changing log.

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("OK  gate_cold_read_handoff_not_stale: 22/22 cases pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
