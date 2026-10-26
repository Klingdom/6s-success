#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_status_deploy_verdict_current() can actually
fail, and that it clears once STATUS.md's BLOCKER-001 section cites the
real, current build_id.

Found 2026-09-23, this operator: STATUS.md's BLOCKER-001 was last edited
that same day and still quoted a 2026-09-20 deploy confirmation, a full day
after ops/deploy-verdict.json had already recorded a newer one. Nothing
checked BLOCKER-001's own prose against the one file whose whole job is to
record this fact, the same "source corrected, sibling never told" shape
gate_goals_traffic_current already guards for GOALS.md's traffic figure.

Widened 2026-09-24, PM check-in: found a second STATUS.md section,
"Production Knowledge" under "Current Overall Assessment", independently
citing its own "last confirmed current" build_id, four days stale while
BLOCKER-001 (fixed by the 2026-09-23 correction above) had already moved
on. The gate only ever checked BLOCKER-001, so this second citation drifted
unnoticed. status_deploy_verdict_problem() now checks both sections.

Widened again 2026-09-30, scheduled operator: found a THIRD section,
"Immediate Focus", independently citing its own build_id one confirmation
behind "Production Knowledge" in the very same review (04167f5ad701b0e4
against the real 6f5176355eb29401), the gate having just been taught to
check "Production Knowledge" and never widened past it. Same shape, one
section further out.

Widened a third time 2026-10-15, PM check-in: found the "Public website"
and "Production traceability" table rows in STATUS.md section 1 a full
confirmation behind BLOCKER-001 and Production Knowledge, which two
earlier cycles that same day had already fixed. These two rows are the
ones that cite BLOCKER-001 as their own "Full account" and the gate still
never checked them. Same shape, a fourth and fifth section further out.

Narrowed 2026-10-23, PM check-in (10:1x slot): `ops/rotate_status_
history.py --apply-focus` (same date, scheduled operator) deliberately
stopped "Immediate Focus" from ever citing a build id again, replacing it
with a fixed pointer to Production Knowledge/BLOCKER-001. Checks 7 and 8
below now exercise that pointer instead of a build_id, the field's own new
shape.

Widened a fourth time 2026-10-26, scheduled operator cycle: found a FIFTH
section, "Currently Deployed Build (last confirmed)"/"Repository HEAD
Build" under the Technical Operations table, independently citing its own
build id. Named twice the same day as a known gap in this gate's own
section map (a 05:4x PM check-in, then this cycle) before either time
actually widening it; checks 12 and 13 below exercise it directly.

Corrected a fifth time 2026-10-26, scheduled operator cycle (later the same
day): the fifth section's check matched build_id as a substring anywhere
in the whole paragraph, so a real stale "Currently Deployed Build" value
read as clean the moment a 1-commit gap reopened, because the paragraph's
own "Repository HEAD Build" sentence named the real current build_id too,
just to say it did not match. Check 14 below exercises exactly that shape:
the current build_id present in the paragraph, but not as the "Currently
Deployed Build" field's own value.

Run:  python ops/tests/test_gate_status_deploy_verdict_current.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    verdict = {"verdict": "current", "build_id": "a993020017bafe37",
               "checked_at": "2026-09-22T16:05:56Z"}

    # 1. BLOCKER-001 cites a different, stale build_id: must fire, and must
    #    name the real current build_id so the fix is obvious.
    stale = (
        "# STATUS\n\n"
        "## Some Other Section\n\nirrelevant text\n\n"
        "## BLOCKER-001: Production State Verifiable Only From a Session "
        "With Real Access\n\n"
        "the tracked verdict now reads current at 2026-09-20T17:46:50Z, "
        "build `d9fc700d0700972f`.\n\n"
        "## BLOCKER-002: something else\n\nmore text\n"
    )
    problem = preflight.status_deploy_verdict_problem(stale, verdict)
    if not problem:
        fails.append("stale build_id in BLOCKER-001: expected a problem, "
                     "got none")
    elif verdict["build_id"] not in problem:
        fails.append("problem string did not name the real build_id: %r"
                     % problem)

    # 2. BLOCKER-001 cites the real, current build_id: must not fire.
    current = stale.replace("d9fc700d0700972f", verdict["build_id"])
    problem = preflight.status_deploy_verdict_problem(current, verdict)
    if problem:
        fails.append("current build_id cited, but still flagged: %r"
                     % problem)

    # 3. No BLOCKER-001 section at all (a future rewrite, or a file this
    #    correction no longer applies to): must not fire. This gate only
    #    checks a section that exists, never invents one to complain about.
    no_section = "# STATUS\n\n## Some Other Section\n\nno blocker here.\n"
    problem = preflight.status_deploy_verdict_problem(no_section, verdict)
    if problem:
        fails.append("no BLOCKER-001 section present, but still flagged: %r"
                     % problem)

    # 4. verdict has no build_id (a malformed or half-written file): must
    #    not fire, since there is nothing real to compare against.
    problem = preflight.status_deploy_verdict_problem(stale, {})
    if problem:
        fails.append("verdict with no build_id, but still flagged: %r"
                     % problem)

    # 5. The real defect shape: BLOCKER-001 is current, but the separate
    #    "Production Knowledge" section under "Current Overall Assessment"
    #    independently cites a stale build_id. Must fire, and must name the
    #    stale section specifically, not just "BLOCKER-001" again.
    mixed = (
        "# STATUS\n\n"
        "## BLOCKER-001: Production State Verifiable Only From a Session "
        "With Real Access\n\n"
        "the tracked verdict now reads current at 2026-09-23T19:00:39Z, "
        "build `" + verdict["build_id"] + "`.\n\n"
        "# 30. Current Overall Assessment\n\n"
        "**Production Knowledge, corrected earlier:** LAST CONFIRMED "
        "CURRENT 2026-09-18T17:20:47Z (build `7c765b634045a89c`).\n\n"
        "**Business Data Knowledge:** unrelated paragraph.\n"
    )
    problem = preflight.status_deploy_verdict_problem(mixed, verdict)
    if not problem:
        fails.append("BLOCKER-001 current but Production Knowledge stale: "
                     "expected a problem, got none")
    elif "Production Knowledge" not in problem or "BLOCKER-001" in problem:
        fails.append("problem string did not correctly name only the "
                     "stale 'Production Knowledge' section: %r" % problem)

    # 6. Both sections current: must not fire.
    both_current = mixed.replace("7c765b634045a89c", verdict["build_id"])
    problem = preflight.status_deploy_verdict_problem(both_current, verdict)
    if problem:
        fails.append("both sections current, but still flagged: %r"
                     % problem)

    # 7. The real defect shape found 2026-10-23: BLOCKER-001 and Production
    #    Knowledge both current, but "Immediate Focus" (which by design,
    #    since the same-day --apply-focus rotation, never cites a build id)
    #    has lost its pointer to Production Knowledge/BLOCKER-001. Must
    #    fire, and must name only that section.
    third_stale = (
        both_current +
        "\n**Immediate Focus:** production matches HEAD exactly, see "
        "ops/deploy-verdict.json for the current build.\n\n"
        "**Correction:** unrelated paragraph.\n"
    )
    problem = preflight.status_deploy_verdict_problem(third_stale, verdict)
    if not problem:
        fails.append("Immediate Focus missing its pointer while the other "
                     "two are current: expected a problem, got none")
    elif "Immediate Focus" not in problem or "BLOCKER-001" in problem \
            or "Production Knowledge" in problem:
        fails.append("problem string did not correctly name only the "
                      "stale 'Immediate Focus' section: %r" % problem)

    # 8. All three sections current, Immediate Focus pointing at Production
    #    Knowledge as the --apply-focus rotation now writes it: must not
    #    fire, even though this field names no build id at all.
    all_current = third_stale.replace(
        "production matches HEAD exactly, see ops/deploy-verdict.json for "
        "the current build.",
        "SEE THE PRODUCTION KNOWLEDGE PARAGRAPH ABOVE AND `BLOCKER-001`, "
        "NOT THIS LINE.")
    problem = preflight.status_deploy_verdict_problem(all_current, verdict)
    if problem:
        fails.append("all three sections current, but still flagged: %r"
                     % problem)

    # 9. The real defect shape found 2026-10-15: every prose section is
    #    current, but the "Public website" status-table row independently
    #    cites a stale build_id. Must fire, and must name only that row.
    table_stale = (
        all_current +
        "\n| Area | Status | Evidence / Notes |\n"
        "|---|---|---|\n"
        "| Public website | LIVE, build `2222222222222222` | some notes |\n"
        "| Application/API | N/A BY DESIGN | static site |\n"
    )
    problem = preflight.status_deploy_verdict_problem(table_stale, verdict)
    if not problem:
        fails.append("Public website row stale while prose sections are "
                     "current: expected a problem, got none")
    elif "Public website" not in problem or "BLOCKER-001" in problem \
            or "Production Knowledge" in problem \
            or "Immediate Focus" in problem:
        fails.append("problem string did not correctly name only the "
                     "stale 'Public website' row: %r" % problem)

    # 10. Same shape, for the "Production traceability" row: must fire, and
    #     must name only that row.
    traceability_stale = (
        all_current +
        "\n| Area | Status | Notes |\n"
        "|---|---|---|\n"
        "| CI health | GREEN | fine |\n"
        "| Production traceability | Tracked, build "
        "`3333333333333333` | some notes |\n"
        "| Repository hygiene | fine | fine |\n"
    )
    problem = preflight.status_deploy_verdict_problem(
        traceability_stale, verdict)
    if not problem:
        fails.append("Production traceability row stale while prose "
                     "sections are current: expected a problem, got none")
    elif "Production traceability" not in problem \
            or "BLOCKER-001" in problem \
            or "Production Knowledge" in problem \
            or "Immediate Focus" in problem:
        fails.append("problem string did not correctly name only the "
                     "stale 'Production traceability' row: %r" % problem)

    # 11. Both table rows current: must not fire.
    both_rows_current = traceability_stale.replace(
        "3333333333333333", verdict["build_id"]).replace(
        "2222222222222222", verdict["build_id"])
    both_rows_current += (
        "\n| Public website | LIVE, build `" + verdict["build_id"] +
        "` | some notes |\n"
    )
    problem = preflight.status_deploy_verdict_problem(
        both_rows_current, verdict)
    if problem:
        fails.append("both table rows current, but still flagged: %r"
                     % problem)

    # 12. Same shape, for the fifth section found 2026-10-26: BLOCKER-001,
    #     Production Knowledge and both table rows are all current, but the
    #     "Currently Deployed Build (last confirmed)"/"Repository HEAD
    #     Build" paragraph independently cites a stale build_id. Must fire,
    #     and must name only that section.
    fifth_stale = (
        both_rows_current +
        "\n**Currently Deployed Build (last confirmed):** "
        "`4444444444444444` (resolves to commit `aaaaaaaaa`), confirmed "
        "2026-10-20T00:00:00Z\n"
        "**Confirmed At:** `2026-10-20T00:00:00Z` (`ops/deploy-verdict."
        "json`, a session with real production access)\n"
        "**Repository HEAD Build:** `4444444444444444` (`site/build-id."
        "txt`). Matches the confirmed deployed build above exactly.\n"
        "**Release / Tag:** NONE, every deploy is tracked by commit SHA\n"
    )
    problem = preflight.status_deploy_verdict_problem(fifth_stale, verdict)
    if not problem:
        fails.append("Currently Deployed Build/Repository HEAD Build "
                     "paragraph stale while every other section is "
                     "current: expected a problem, got none")
    elif "Currently Deployed Build" not in problem \
            or "BLOCKER-001" in problem \
            or "Production Knowledge" in problem \
            or "Immediate Focus" in problem \
            or "Public website" in problem \
            or "Production traceability" in problem:
        fails.append("problem string did not correctly name only the "
                     "stale 'Currently Deployed Build' section: %r"
                     % problem)

    # 13. The fifth section also current: must not fire.
    fifth_current = fifth_stale.replace(
        "4444444444444444", verdict["build_id"])
    problem = preflight.status_deploy_verdict_problem(fifth_current, verdict)
    if problem:
        fails.append("all five sections current, but still flagged: %r"
                     % problem)

    # 14. Found 2026-10-26, scheduled operator cycle (later the same day):
    #     the real current build_id appears in the paragraph, but only as
    #     the "Repository HEAD Build" value, explicitly saying it does not
    #     match the deployed build; "Currently Deployed Build" itself still
    #     cites a stale one. The old substring-anywhere check read this as
    #     current. Must fire, and must name only this section.
    sixth_stale = (
        both_rows_current +
        "\n**Currently Deployed Build (last confirmed):** "
        "`5555555555555555` (resolves to commit `bbbbbbbbb`), confirmed "
        "2026-10-20T00:00:00Z\n"
        "**Confirmed At:** `2026-10-20T00:00:00Z` (`ops/deploy-verdict."
        "json`, a session with real production access)\n"
        "**Repository HEAD Build:** `" + verdict["build_id"] + "` "
        "(`site/build-id.txt`). No longer matches the confirmed deployed "
        "build above: 1 material commit sits undeployed.\n"
        "**Release / Tag:** NONE, every deploy is tracked by commit SHA\n"
    )
    problem = preflight.status_deploy_verdict_problem(sixth_stale, verdict)
    if not problem:
        fails.append("Currently Deployed Build cites a stale build even "
                     "though the real current build_id appears elsewhere "
                     "in the same paragraph, as Repository HEAD Build: "
                     "expected a problem, got none")
    elif "Currently Deployed Build" not in problem \
            or "BLOCKER-001" in problem \
            or "Production Knowledge" in problem \
            or "Public website" in problem \
            or "Production traceability" in problem:
        fails.append("problem string did not correctly name only the "
                     "stale 'Currently Deployed Build' field: %r" % problem)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 14 checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
