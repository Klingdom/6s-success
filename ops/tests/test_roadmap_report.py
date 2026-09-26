#!/usr/bin/env python3
"""
Prove ops/roadmap_report.py's backlog_next() correctly flags a row as
"waiting on Phil" when it is blocked, not only when the Owner column
literally contains the word "Phil".

Found 2026-09-11, this operator, cold-reading a low-mention file per step 5d.
roadmap_report.py builds the report sent to Phil four times a day, live
(.github/workflows/roadmap-report.yml). Its "NEXT IN THE QUEUE, ordered by
dependency not appeal" section is meant to be operator-actionable work; its
"DECISIONS WAITING ON YOU" section is meant to be Phil's. The old check was
`waiting = "Phil" in cells[4]`, so a row reading "blocked on 2.1" (2.1 is
itself a Phil row), "needs 1.1", "conditional on 3.4" or "needs traffic"
never matched and printed as if the operator could do it today. Re-derived
directly against the live BACKLOG-2026-H2.md: 14 of 37 then-open rows were
misclassified this way.

Also fixed at the source, not only in the parser: BACKLOG-2026-H2.md row 1.5
(Search Console) said Owner "operator" while OWNER-ACTIONS.md item 1a shows
Search Console has never been verified and needs Phil's own paste; and three
rows (1.2, 1.4, 1.6) had six pipe-delimited cells against the section's
five-column header, an authoring mistake that also breaks the table's
rendering on GitHub, not only this parser.

Run:  python ops/tests/test_roadmap_report.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import roadmap_report as rr                                      # noqa: E402


def row(id_="9.9", item="An item", accept="Some criterion", est="1.0", owner="operator"):
    return [id_, item, accept, est, owner]


def main() -> int:
    fails = []

    # 1. The literal case the old check already handled must keep working.
    if not rr.row_is_waiting(row(owner="**Phil**")):
        fails.append("a bare Phil owner did not read as waiting")

    # 2. A row blocked on another backlog row, not literally naming Phil.
    for owner in ("**blocked on 2.1**", "operator, needs 1.1", "conditional on 3.4",
                  "needs traffic", "needs 2.1", "**blocked**, needs an Apple "
                  "Developer account", "operator, needs the VPS deploy key this "
                  "sandbox does not hold"):
        if not rr.row_is_waiting(row(owner=owner)):
            fails.append(f"dependency-blocked owner {owner!r} did not read as waiting")

    # 3. A row that says it is now a spending or owner-action decision.
    for owner in ("**Phil**, this is a spending decision",
                  "the decision is now a payment, not a design. OWNER-ACTIONS.md "
                  "1b, one upgrade click"):
        if not rr.row_is_waiting(row(owner=owner)):
            fails.append(f"decision-shaped owner {owner!r} did not read as waiting")

    # 4. Genuinely operator-actionable rows must NOT be swept into waiting.
    for owner in ("operator", "operator, see note", "automated"):
        if rr.row_is_waiting(row(owner=owner)):
            fails.append(f"plain operator owner {owner!r} was wrongly flagged as waiting")

    # 5. Done rows must still never appear at all, regardless of the owner text.
    done_row = row(item="~~Finished thing~~", owner="**Phil**")
    if not rr.is_backlog_row_done(done_row):
        fails.append("a struck-through item was not recognised as done")

    # 6. The real, live file: row 1.5 (Search Console) must read as waiting,
    # since OWNER-ACTIONS.md item 1a shows it needs Phil's own verification
    # paste, not something the operator can just go do.
    items = {i["id"]: i for i in rr.backlog_next()}
    if "1.5" in items and not items["1.5"]["waiting"]:
        fails.append("live row 1.5 (Search Console) still reads as operator-actionable")

    # 6b. Found 2026-09-26, same defect class: a status cell reading "no
    # operator credential" (row 3.10's real wording) did not match any
    # existing alternative, so a row blocked on Phil's own YouTube OAuth
    # paste printed under "NEXT IN THE QUEUE" as if unblocked.
    if not rr.row_is_waiting(row(owner="102 to go, same wall, no operator credential")):
        fails.append("'no operator credential' owner text did not read as waiting")
    if "3.10" in items and not items["3.10"]["waiting"]:
        fails.append("live row 3.10 (publish the remaining videos) still reads "
                     "as operator-actionable")

    # 7. The real, live file: every backlog row still parses to exactly the
    # header's column count. A row with an extra cell silently shifts every
    # later column (Est read as Owner, etc.), the exact shape found in 1.2,
    # 1.4 and 1.6 before this fix.
    p = os.path.join(ROOT, "BACKLOG-2026-H2.md")
    header_cols = None
    for ln in open(p, encoding="utf-8"):
        if ln.startswith("| #"):
            header_cols = ln.count("|") - 1
            continue
        if ln.startswith("| ") and ln.count("|") >= 5 and header_cols:
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if all(set(c) <= set("- ") for c in cells):
                continue
            if cells[0][:1].isdigit() and len(cells) != header_cols:
                fails.append(f"row {cells[0]} has {len(cells)} cells, "
                             f"header defines {header_cols}")

    # 8. commits_24h_text must never let an unresolved shallow clone render
    # as zero, or a genuinely quiet day render as unknown. Found 2026-09-13:
    # repo()'s commits_24h came straight from `git log --since=` with no
    # shallow check at all; `.github/workflows/roadmap-report.yml`'s own
    # `fetch-depth: 50` checkout, at this repository's real commit rate,
    # reaches back only about 8 hours, so a plain count silently returned
    # whatever the shallow boundary caught (measured: 62, not the real 143)
    # instead of erroring.
    if rr.commits_24h_text(None) == "0":
        fails.append("commits_24h_text(None) reads as zero, not unknown")
    if rr.commits_24h_text(None).strip().isdigit():
        fails.append("commits_24h_text(None) reads as a real number")
    if rr.commits_24h_text(0) != "0":
        fails.append("commits_24h_text(0) does not read as a genuine zero")
    if rr.commits_24h_text(143) != "143":
        fails.append("commits_24h_text(143) did not round-trip")

    if fails:
        print(f"FAIL ({len(fails)}):")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 18 cases (row_is_waiting x12, done-check, live-file column "
          "shape, commits_24h_text x4)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
