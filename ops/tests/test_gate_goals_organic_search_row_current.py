#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_goals_organic_search_row_current() catches a
sibling document repeating GOALS.md's retired "0 from Google" organic-search
claim after GOALS.md's own correction says otherwise.

Found 2026-09-09: GOALS.md's own row said "none from Google" three lines
above a "Corrected 2026-09-05" paragraph saying a Google referral landed.
STATUS.md repeated the retired claim too, so the gate was widened to check
it. Found again 2026-09-10: RISKS.md's RISK-0005 and RISK-0013 evidence
lists both still cited "0 from Google" and the retired 52/144 traffic
figure, seven days after GOALS.md moved on. RISKS.md was never added to
this gate's checked list, so this test proves it now is.

Run:  python ops/tests/test_gate_goals_organic_search_row_current.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

GOALS_CORRECTED = (
    "# Goals\n\n"
    "| Sessions from organic search | **2, whole life of the site, as of "
    "2026-09-05** | one visit from Bing (21 August), one from Google "
    "(4 September). |\n\n"
    "**Corrected 2026-09-05: the earlier wording here is no longer true: "
    "not one visit from Google.** A Google referral landed 4 September.\n"
)

RISKS_STALE = (
    "# Risks\n\n"
    "RISK-0013 evidence: 52 visitors/144 visits/30 days, 21 sessions/7 "
    "days, 1 organic click from Bing, 0 from Google; a live feed is still "
    "blocked.\n"
)

RISKS_CURRENT = (
    "# Risks\n\n"
    "RISK-0013 evidence: 60 visitors/161 visits/30 days, up from 52/144. "
    "Two organic referrals exist, one from Bing on 21 August and one from "
    "Google on 4 September.\n"
)

STATUS_CURRENT = "# Status\n\nTraffic: 60 visitors, 161 visits, 30 days.\n"

GOALS_LATER_READING = (
    "# Goals\n\n"
    "| Sessions from organic search | **4 visits from 3 visitors, whole "
    "life of the site, reconfirmed 2026-09-17** | one visit from Bing "
    "(21 August) and three visits from two Google visitors (4 to 12 "
    "September). Previous reading: 2 visits (Bing 1, Google 1), "
    "2026-09-05. |\n\n"
    "**Corrected 2026-09-05: the earlier wording here is no longer true: "
    "not one visit from Google.** A Google referral landed 4 September.\n"
)

STATUS_STALE_ORGANIC_ROW = (
    "# Status\n\n"
    "| Organic sessions | 2, whole life of the site, as of 2026-09-05 "
    "(1 Bing, 1 Google) | Last 30 days | stale. |\n"
)

STATUS_CURRENT_ORGANIC_ROW = (
    "# Status\n\n"
    "| Organic sessions | 4 visits from 3 visitors, whole life of the "
    "site, reconfirmed 2026-09-17 (1 Bing, 21 August; 3 Google visits "
    "from 2 visitors, 4 to 12 September) | Last 30 days | current. |\n"
)

GOALS_SELF_CONTRADICTING = (
    "# Goals\n\n"
    "| Sessions from organic search | **5 visits from 4 visitors, whole "
    "life of the site, as of 2026-09-20** | one visit from Bing "
    "(21 August) and three visits from two Google visitors (4 to 12 "
    "September). Previous reading: 2 visits (Bing 1, Google 1), "
    "2026-09-05. |\n\n"
    "**Corrected 2026-09-05: the earlier wording here is no longer true: "
    "not one visit from Google.** A Google referral landed 4 September.\n"
)

STATUS_MATCHING_BAD_READING = (
    "# Status\n\n"
    "| Organic sessions | 5 visits from 4 visitors, whole life of the "
    "site, as of 2026-09-20 | Last 30 days | current. |\n"
)

GOALS_ROW_FIXED_NARRATIVE_STALE = (
    "# Goals\n\n"
    "| Sessions from organic search | **5 visits from 4 visitors, whole "
    "life of the site, measured 2026-09-20** | one visit from Bing "
    "(21 August) and four visits from three Google visitors (4 to 18 "
    "September). |\n\n"
    # Line-wrapped like the real file's hard-wrapped prose, on purpose:
    # the first regex written for this check used literal spaces and
    # silently never matched GOALS.md's own wrapped paragraph, passing
    # this test while leaving the real file's check dead. Wrapping here
    # is what would have caught that.
    "**Why it is first, now with numbers.** In the whole life of this "
    "site exactly four visits from three visitors arrived from a search\n"
    "engine, per the row above.\n\n"
    "**Corrected 2026-09-05: the earlier wording here is no longer true: "
    "not one visit from Google.** A Google referral landed 4 September.\n"
)

GOALS_ROW_AND_NARRATIVE_CURRENT = (
    "# Goals\n\n"
    "| Sessions from organic search | **5 visits from 4 visitors, whole "
    "life of the site, measured 2026-09-20** | one visit from Bing "
    "(21 August) and four visits from three Google visitors (4 to 18 "
    "September). |\n\n"
    "**Why it is first, now with numbers.** In the whole life of this "
    "site exactly five visits from four visitors arrived from a search\n"
    "engine, per the row above.\n\n"
    "**Corrected 2026-09-05: the earlier wording here is no longer true: "
    "not one visit from Google.** A Google referral landed 4 September.\n"
)


def _run(goals, status, risks):
    tmp = tempfile.mkdtemp()
    io.open(os.path.join(tmp, "GOALS.md"), "w", encoding="utf-8").write(goals)
    if status is not None:
        io.open(os.path.join(tmp, "STATUS.md"), "w", encoding="utf-8").write(status)
    if risks is not None:
        io.open(os.path.join(tmp, "RISKS.md"), "w", encoding="utf-8").write(risks)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_goals_organic_search_row_current()
        return list(preflight.FAIL)
    finally:
        preflight.ROOT = old_root
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. RISKS.md still stating "0 from Google" after GOALS.md's own
    #    correction: this is the exact 2026-09-10 regression, must be caught.
    r = _run(GOALS_CORRECTED, STATUS_CURRENT, RISKS_STALE)
    if not r or not any("RISKS.md" in f[1] for f in r):
        fails.append("stale RISKS.md 'zero from Google' claim not caught "
                      "by name: %r" % (r,))

    # 2. RISKS.md updated to match GOALS.md's correction: no failure.
    r = _run(GOALS_CORRECTED, STATUS_CURRENT, RISKS_CURRENT)
    if r:
        fails.append("a corrected RISKS.md was wrongly flagged: %r" % (r,))

    # 3. RISKS.md absent entirely: gate must not crash, and must not fail
    #    on a file that does not exist.
    r = _run(GOALS_CORRECTED, STATUS_CURRENT, None)
    if r:
        fails.append("an absent RISKS.md was wrongly flagged: %r" % (r,))

    # 4. The real, committed files: clean, since this cycle fixed both
    #    stale citations in the real RISKS.md.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_goals_organic_search_row_current()
    if preflight.FAIL:
        fails.append("the real committed GOALS.md/STATUS.md/RISKS.md "
                      "failed: %r" % (preflight.FAIL,))

    # 5. Found 2026-09-20: GOALS.md moved a second time, to 4 visits from
    #    3 visitors, and STATUS.md's own "Organic sessions" row still
    #    carried the retired 2-visit reading. The old text-only check
    #    (case 1/2 above) does not see this, since it never says "zero" or
    #    omits Google; only the numeric comparison catches it.
    r = _run(GOALS_LATER_READING, STATUS_STALE_ORGANIC_ROW, None)
    if not r or not any("STATUS.md" in f[1] and "2" in f[1] and "4" in f[1]
                         for f in r):
        fails.append("a stale STATUS.md 'Organic sessions' visit total "
                      "not caught by name: %r" % (r,))

    # 6. STATUS.md's row updated to match GOALS.md's current 4-visit
    #    reading: no failure.
    r = _run(GOALS_LATER_READING, STATUS_CURRENT_ORGANIC_ROW, None)
    if r:
        fails.append("a corrected STATUS.md 'Organic sessions' row was "
                      "wrongly flagged: %r" % (r,))

    # 7. Found 2026-09-20, second instance: GOALS.md's own bolded headline
    #    said "5 visits from 4 visitors" while its own detail sentence,
    #    one row cell later, still enumerated only one Bing visit plus
    #    three visits from two Google visitors (4 visits, 3 visitors).
    #    Even a STATUS.md "helpfully" bumped to match the bad headline
    #    must not go clean: the row disagrees with its own evidence.
    r = _run(GOALS_SELF_CONTRADICTING, STATUS_MATCHING_BAD_READING, None)
    if not r or not any("its own detail sentence" in f[1] for f in r):
        fails.append("a headline that disagrees with its own row's "
                      "detail sentence was not caught by name: %r" % (r,))

    # 8. The later, real 4-visits-from-3-visitors reading (case 5/6's
    #    GOALS_LATER_READING) is internally consistent: no failure from
    #    the new self-arithmetic check either.
    r = _run(GOALS_LATER_READING, STATUS_CURRENT_ORGANIC_ROW, None)
    if r:
        fails.append("an internally consistent GOALS.md row was wrongly "
                      "flagged by the self-arithmetic check: %r" % (r,))

    # 9. Found 2026-09-20, third instance: the row was corrected to
    #    "5 visits from 4 visitors" but the "Why it is first, now with
    #    numbers" narrative paragraph below it still said "exactly four
    #    visits from three visitors". Neither the row-self-arithmetic nor
    #    the STATUS.md comparison reads this paragraph, so this must be a
    #    dedicated check.
    r = _run(GOALS_ROW_FIXED_NARRATIVE_STALE, STATUS_MATCHING_BAD_READING, None)
    if not r or not any("now with numbers" in f[1] for f in r):
        fails.append("a narrative paragraph restating a retired visit "
                      "count was not caught by name: %r" % (r,))

    # 10. The row and its narrative paragraph both current and agreeing:
    #     no failure.
    r = _run(GOALS_ROW_AND_NARRATIVE_CURRENT, STATUS_MATCHING_BAD_READING, None)
    if r:
        fails.append("a narrative paragraph that agrees with its own "
                      "row was wrongly flagged: %r" % (r,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_goals_organic_search_row_current, 10/10 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
