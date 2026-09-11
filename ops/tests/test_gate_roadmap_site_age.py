#!/usr/bin/env python3
"""
Prove ops/preflight.py's roadmap_site_age_drift()/gate_roadmap_site_age_current()
catch ROADMAP-2026-2029.md's site-age claim drifting from its own stated
first analytics day.

Found 2026-09-11: section 2 carries "Corrected: the site is not nine days
old... eighteen days as of this review", but section 3's Horizon 1
paragraph, one screen down, still read "the site is nine days old", the
exact original claim the correction three lines above exists to retire.
Fixed by dating the Horizon 1 sentence against the same first analytics
day (2026-08-20) and adding this gate so the arithmetic is re-derived on
every run instead of trusted from prose.

Run:  python ops/tests/test_gate_roadmap_site_age.py
"""
import datetime as dt
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

GOOD = (
    "First analytics day 2026-08-20, so eighteen days as of this review.\n\n"
    "and the site is twenty-two days, 22 days as of 2026-09-11.\n"
)

STALE_ARITHMETIC = (
    "First analytics day 2026-08-20, so eighteen days as of this review.\n\n"
    "and the site is nine days, 9 days as of 2026-09-11.\n"
)

NO_DATED_CLAIM = (
    "First analytics day 2026-08-20, so eighteen days as of this review.\n\n"
    "and the site is nine days old.\n"
)

passed = failed = 0


def check(name, got, want):
    global passed, failed
    if got == want:
        passed += 1
    else:
        failed += 1
        print(f"FAIL {name}: got {got!r}, want {want!r}")


# 1. The real, fixed file must be clean today.
real_path = os.path.join(ROOT, "ROADMAP-2026-2029.md")
real_text = io.open(real_path, encoding="utf-8").read()
fails, warns = preflight.roadmap_site_age_drift(real_text, dt.date(2026, 9, 11))
check("real file, no drift", fails, [])

# 2. The exact regression this gate was built to catch: the arithmetic in
#    the claim disagrees with (as-of date minus first analytics day).
fails, warns = preflight.roadmap_site_age_drift(STALE_ARITHMETIC, dt.date(2026, 9, 11))
check("stale arithmetic caught", len(fails), 1)

# 3. A correct claim, checked on the day it was written, is clean.
fails, warns = preflight.roadmap_site_age_drift(GOOD, dt.date(2026, 9, 11))
check("good claim, no fail", fails, [])
check("good claim, not yet stale", warns, [])

# 4. The same correct claim, read 40 days later with nobody rederiving it,
#    warns rather than staying silently confident.
fails, warns = preflight.roadmap_site_age_drift(GOOD, dt.date(2026, 10, 21))
check("good claim, no fail even once stale", fails, [])
check("stale-dated claim warns", len(warns), 1)

# 5. No dated "N days as of DATE" claim at all (e.g. the original undated
#    "nine days old" prose) is unverifiable and must fail, not pass by
#    default: a claim with no date to check is exactly how this regression
#    shipped in the first place.
fails, warns = preflight.roadmap_site_age_drift(NO_DATED_CLAIM, dt.date(2026, 9, 11))
check("undated claim fails closed", len(fails), 1)

# 6. No "First analytics day" line at all: nothing to check against, so
#    this gate must stay silent rather than invent a baseline.
fails, warns = preflight.roadmap_site_age_drift("nothing relevant here", dt.date(2026, 9, 11))
check("no analytics-start line, silent", (fails, warns), ([], []))

print(f"{passed} of {passed + failed} cases pass")
sys.exit(1 if failed else 0)
