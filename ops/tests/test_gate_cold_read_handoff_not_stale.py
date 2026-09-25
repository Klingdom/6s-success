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
    print("OK  gate_cold_read_handoff_not_stale: 8/8 cases pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
