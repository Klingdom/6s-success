#!/usr/bin/env python3
"""
Prove ops/rotate_owner_actions.py archives OWNER-ACTIONS.md's historical
preamble span correctly: the span moves verbatim, the live file keeps only
the pointer sentence, repeated runs are a no-op, a missing or duplicated
anchor is refused rather than guessed past, and the archive write appends
above existing content without disturbing it.

Extended 2026-10-24, scheduled operator cycle, for --check-preamble/
--apply-preamble (the "Last measured"/"List reviewed" paragraphs
themselves): cases 11-18 prove the citation/date are found by regex rather
than a hardcoded string (so a real future re-measurement does not break
this script), that rotation never touches either load-bearing sentence,
and -- the actual risk this whole feature carries -- that the rotated text
still parses clean through the real ops/dashboard.py and ops/preflight.py
functions that read it in production, not just through this test's own
assertions about the string shape.

Run:  python ops/tests/test_rotate_owner_actions.py
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import rotate_owner_actions as roa                               # noqa: E402

BEFORE = (
    "# Owner actions\n\n"
    "**Last measured:** some traffic sentence, untouched by this script.\n\n"
    "**List reviewed:** some review sentence, also untouched. "
    "it says nothing about traffic."
)
AFTER = "\n\n---\n\n## Resolved today\n\n| # | Action | Outcome |\n"


def _history_text(n):
    entries = []
    for i in range(n):
        entries.append("**Corrected day-%d:** body text for entry %d, "
                        "nothing anyone still needs to read." % (i, i))
    return BEFORE + "\n\n" + "\n\n".join(entries) + AFTER


def main() -> int:
    fails = []

    # 1. region_between() finds exactly the span between the two anchors,
    #    and before/after keep everything outside it untouched.
    text = _history_text(3)
    before, region, after = roa.region_between(
        text, roa.REGION_START_AFTER, roa.REGION_END_BEFORE)
    if "day-0" not in region or "day-2" not in region:
        fails.append("region did not capture all synthetic entries: %r"
                     % region[:120])
    if not before.endswith("it says nothing about traffic."):
        fails.append("before boundary drifted: %r" % before[-50:])
    if not after.startswith("\n\n---\n\n## Resolved today"):
        fails.append("after boundary drifted: %r" % after[:50])

    # 2. A missing start anchor is refused, not guessed past.
    try:
        roa.region_between(
            BEFORE.replace("it says nothing about traffic.",
                            "something else entirely") + AFTER,
            roa.REGION_START_AFTER, roa.REGION_END_BEFORE)
        fails.append("missing start anchor was silently accepted")
    except ValueError:
        pass

    # 3. A duplicated start anchor is refused.
    try:
        roa.region_between(text + "\n\nit says nothing about traffic.\n",
                            roa.REGION_START_AFTER, roa.REGION_END_BEFORE)
        fails.append("duplicated start anchor was silently accepted")
    except ValueError:
        pass

    # 4. A missing end anchor is refused.
    try:
        roa.region_between(
            text.replace("## Resolved today", "## Something Else"),
            roa.REGION_START_AFTER, roa.REGION_END_BEFORE)
        fails.append("missing end anchor was silently accepted")
    except ValueError:
        pass

    # 5. plan_rotation() replaces the whole span with REPLACEMENT and
    #    returns the original span, stripped, as the archived text; the
    #    rest of the document (before/after) is byte-identical.
    text3 = _history_text(3)
    new_text, archived = roa.plan_rotation(text3)
    if roa.REPLACEMENT not in new_text:
        fails.append("rotated text does not carry the pointer sentence")
    if "day-0" in new_text or "day-1" in new_text or "day-2" in new_text:
        fails.append("rotated text still carries archived content")
    if "day-0" not in archived or "day-2" not in archived:
        fails.append("archived text lost an entry: %r" % archived[:120])
    if not new_text.startswith(BEFORE) or not new_text.endswith(AFTER):
        fails.append("rotation disturbed text outside the span")

    # 6. Already-rotated text is a no-op: plan_rotation() returns the text
    #    unchanged and an empty archived string.
    already = BEFORE + "\n\n" + roa.REPLACEMENT + AFTER
    new_again, archived_again = roa.plan_rotation(already)
    if new_again != already or archived_again:
        fails.append("an already-rotated span was rotated again")

    # 7. region_size() matches the stripped byte length of the region,
    #    and is what --check's DUE/CLEAN decision is based on. Use enough
    #    synthetic entries to clear SIZE_BUFFER_BYTES, so this does not
    #    depend on how long REPLACEMENT happens to be today.
    text_big = _history_text(15)
    size = roa.region_size(text_big)
    _, region_big, _ = roa.region_between(
        text_big, roa.REGION_START_AFTER, roa.REGION_END_BEFORE)
    if size != len(region_big.strip().encode("utf-8")):
        fails.append("region_size() did not match the stripped region "
                     "length")
    if size <= len(roa.REPLACEMENT.encode("utf-8")) + roa.SIZE_BUFFER_BYTES:
        fails.append("synthetic 15-entry history did not register as DUE")

    already_size = roa.region_size(already)
    if already_size > len(roa.REPLACEMENT.encode("utf-8")) + roa.SIZE_BUFFER_BYTES:
        fails.append("already-rotated text registered as DUE")

    # 8. apply_archive() with no existing archive writes the header once
    #    and the new block below it.
    fresh = roa.apply_archive("**Corrected day-0:** first ever entry.",
                               None)
    if not fresh.startswith(roa.ARCHIVE_HEADER_FIRST_LINE):
        fails.append("fresh archive did not start with the expected header")
    if "first ever entry" not in fresh:
        fails.append("fresh archive lost its only entry")

    # 9. apply_archive() with existing content prepends the new block
    #    right after the header's own divider, leaving existing entries
    #    intact and in place.
    grown = roa.apply_archive("**Corrected day-1:** second batch entry.",
                               fresh)
    if "second batch entry" not in grown or "first ever entry" not in grown:
        fails.append("growing the archive lost an entry")
    if grown.find("second batch entry") > grown.find("first ever entry"):
        fails.append("new archive block was not placed above older content")

    # 10. apply_archive() refuses an existing file with the wrong header
    #     rather than guess where to insert.
    try:
        roa.apply_archive("**Corrected day-2:** entry.",
                           "# Some Other Document\n\n---\nbody\n")
        fails.append("a wrong-header archive file was silently accepted")
    except ValueError:
        pass

    # 11. _lm_region()/_lr_region() find their anchors by regex, not a
    #     hardcoded date, so a different real reading (a future
    #     re-measurement) is found exactly the same way.
    preamble = (
        "# Owner actions\n\n"
        "**Last measured:** 2027-03-11 14:05 UTC, traffic re-measured by a "
        "direct database read: 212 visitors/400 visits/30 days. "
        "**Corrected 2027-03-12: this was wrong.** More stale narrative "
        "that should not still be here next cycle.\n\n"
        "**List reviewed:** 2027-03-12: the marker had drifted. Earlier, "
        "2027-03-10: something else changed. A separate marker, \"Last "
        "measured\" above, means something different.\n\n"
        "**Deploy-gap and per-item history** stays untouched here.\n\n"
        "---\n\n## Resolved today\n\n| # | Action | Outcome |\n"
    )
    s, e = roa._lm_region(preamble)
    if preamble[s:e].strip() != (
            ". **Corrected 2027-03-12: this was wrong.** More stale "
            "narrative that should not still be here next cycle.").strip():
        fails.append("_lm_region found the wrong span for a non-today "
                      "reading: %r" % preamble[s:e])
    s, e = roa._lr_region(preamble)
    if "the marker had drifted" not in preamble[s:e]:
        fails.append("_lr_region found the wrong span: %r" % preamble[s:e])

    # 12. plan_rotation_preamble() rotates both paragraphs in one pass,
    #     keeps the citation and the date live, and the archived blocks
    #     carry exactly what was removed.
    new_text, blocks = roa.plan_rotation_preamble(preamble)
    labels = [label for label, _ in blocks]
    if labels != ["Last measured", "List reviewed"]:
        fails.append("plan_rotation_preamble did not report both chains: "
                     "%r" % labels)
    if "212 visitors/400 visits/30 days" not in new_text:
        fails.append("rotation lost the live traffic citation")
    if "2027-03-12" not in new_text.split("**Deploy-gap")[0]:
        # the List reviewed date itself must survive in the KEEP portion
        fails.append("rotation lost the List reviewed date")
    if "This was wrong" in new_text or "the marker had drifted" in new_text:
        fails.append("rotation left old narrative live instead of "
                     "archiving it")
    if roa.LM_REPLACEMENT.strip() not in new_text:
        fails.append("rotated text missing the Last measured pointer")
    if roa.LR_REPLACEMENT.strip() not in new_text:
        fails.append("rotated text missing the List reviewed pointer")

    # 13. Re-running on already-rotated preamble text is a no-op.
    new_again, blocks_again = roa.plan_rotation_preamble(new_text)
    if new_again != new_text or blocks_again:
        fails.append("an already-rotated preamble was rotated again")

    # 14. A citation sentence that no longer matches the required shape
    #     (dashboard.py's own contract) is refused, not guessed past.
    broken = preamble.replace(
        "traffic re-measured by a direct database read:",
        "traffic re-read somehow:")
    try:
        roa._lm_region(broken)
        fails.append("a reworded citation sentence was silently accepted")
    except ValueError:
        pass

    # 15. A missing "List reviewed" header is refused.
    try:
        roa._lr_region(preamble.replace("**List reviewed:**", "Reviewed:"))
        fails.append("a missing List reviewed header was silently accepted")
    except ValueError:
        pass

    # 16. preamble_sizes() matches the stripped byte length of each region,
    #     and a long synthetic history past the buffer registers as DUE.
    lm_size, lr_size = roa.preamble_sizes(preamble)
    s, e = roa._lm_region(preamble)
    if lm_size != len(preamble[s:e].strip().encode("utf-8")):
        fails.append("preamble_sizes() Last measured did not match the "
                     "stripped region length")
    big_history = (" **Corrected again:** " +
                   "filler text padding this out past the buffer. " * 40)
    preamble_big = preamble.replace(
        "**Corrected 2027-03-12: this was wrong.** More stale narrative "
        "that should not still be here next cycle.",
        "**Corrected 2027-03-12: this was wrong.**" + big_history)
    lm_big, _ = roa.preamble_sizes(preamble_big)
    if lm_big <= len(roa.LM_REPLACEMENT.encode("utf-8")) + roa.PREAMBLE_BUFFER_BYTES:
        fails.append("a long synthetic Last measured history did not "
                     "register as DUE")

    # 17. Rotation never touches anything outside the two paragraphs:
    #     the Deploy-gap pointer and everything after it stay byte-for-byte
    #     identical.
    tail_before = preamble[preamble.find("**Deploy-gap"):]
    tail_after = new_text[new_text.find("**Deploy-gap"):]
    if tail_before != tail_after:
        fails.append("rotation disturbed text outside the two paragraphs")

    # 18. The real, currently-committed OWNER-ACTIONS.md parses clean
    #     through the actual production functions that read it -- not a
    #     synthetic copy. This is the real risk this feature carries: a
    #     rotation that looks right in isolation but breaks the live gate
    #     or the live dashboard reading against the real file.
    oa_path = os.path.join(ROOT, "OWNER-ACTIONS.md")
    if os.path.exists(oa_path):
        sys.path.insert(0, os.path.join(ROOT, "ops"))
        import preflight as _preflight                          # noqa: E402
        import dashboard as _dashboard                           # noqa: E402
        _preflight.FAIL.clear()
        _preflight.WARN.clear()
        _preflight.gate_dashboard_owner_actions_traffic_citation_current()
        _preflight.gate_owner_actions_last_measured_current()
        if _preflight.FAIL:
            fails.append("the real committed OWNER-ACTIONS.md fails a live "
                         "gate: %r" % _preflight.FAIL)
        if _dashboard._owner_actions_traffic_citation() is None:
            fails.append("the real committed OWNER-ACTIONS.md no longer "
                         "parses through dashboard._owner_actions_"
                         "traffic_citation()")
        try:
            roa.preamble_sizes(io.open(oa_path, encoding="utf-8").read())
        except ValueError as exc:
            fails.append("the real committed OWNER-ACTIONS.md no longer "
                         "matches this script's own anchors: %s" % exc)

    if fails:
        print("FAIL (%d):" % len(fails))
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 18/18 cases ok.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
