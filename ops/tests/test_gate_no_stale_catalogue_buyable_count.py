#!/usr/bin/env python3
"""
Prove ops/preflight.py's catalogue_buyable_count_drift()/
gate_no_stale_catalogue_buyable_count() catch a "N of M catalog(ue)"
buyable claim that drifted from the live catalogue, and that the real,
fixed files (GOALS.md, STRIPE.md, RISKS.md, EXPERIMENT-PLAN.md) are clean.

Found 2026-09-22: the C6/C7 retirement (147179c6, 159 catalogue items to
138) moved the real buyable count from 158-of-159 to 137-of-138, but
GOALS.md (read first, every cycle, to decide what to work on), STRIPE.md,
RISKS.md's own RISK-0008 closing_condition and EXPERIMENT-PLAN.md all kept
stating the retired figure as present fact. This has recurred at least
four times before by grep of ops/NIGHTLY-LOG.md, always fixed by hand with
no standing check; this closes that gap.

Run:  python ops/tests/test_gate_no_stale_catalogue_buyable_count.py
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

LIVE_TOTAL = 138
LIVE_BUYABLE = 137

STALE = "The site sells 158 of 159 catalogue products with a checkout.\n"
STALE_ITEMS = ("the catalogue can take money for 158 of 159 items "
               "(`EXECUTIVE-DASHBOARD-LIVE.md`), so the shop window is fine.\n")
GOOD = "The site sells 137 of 138 catalogue products with a checkout.\n"
QUOTED_HISTORICAL = ('EXECUTIVE-DASHBOARD-LIVE.md, regenerated 2026-09-03: '
                      '"The site can take money for 158 of 159 catalog items."\n')
THEN_HISTORICAL = ("ops/state.json, reconfirmed 2026-09-03 (158 of 159 "
                    "catalog items sellable then), corrected 2026-09-22 to "
                    "137 of 138.\n")
NO_MENTION = "Nothing about a catalogue count here at all.\n"

passed = failed = 0


def check(name, got, want_empty):
    global passed, failed
    ok = (len(got) == 0) if want_empty else (len(got) > 0)
    if ok:
        passed += 1
    else:
        failed += 1
        print(f"FAIL {name}: got {got!r}, want_empty={want_empty}")


# 1. The exact regression this gate was built to catch.
check("stale 'N of M catalogue' claim",
      preflight.catalogue_buyable_count_drift(
          {"X.md": STALE}, LIVE_TOTAL, LIVE_BUYABLE), False)

# 2. The trickier "catalogue can take money for N of M items" phrasing
#    (EXPERIMENT-PLAN.md's actual shape), no trailing "catalog(ue)" word.
check("stale 'catalogue can take money for N of M items' claim",
      preflight.catalogue_buyable_count_drift(
          {"X.md": STALE_ITEMS}, LIVE_TOTAL, LIVE_BUYABLE), False)

# 3. The corrected text must be clean.
check("fixed text, clean",
      preflight.catalogue_buyable_count_drift(
          {"X.md": GOOD}, LIVE_TOTAL, LIVE_BUYABLE), True)

# 4. A quoted, dated citation of a retired figure is historical, not a
#    live claim; must not be flagged.
check("quoted historical citation not flagged",
      preflight.catalogue_buyable_count_drift(
          {"X.md": QUOTED_HISTORICAL}, LIVE_TOTAL, LIVE_BUYABLE), True)

# 5. RISKS.md's own "N of M catalog items sellable THEN, corrected..."
#    convention for keeping a superseded figure visible must not be
#    flagged either.
check("'then'-marked historical figure not flagged",
      preflight.catalogue_buyable_count_drift(
          {"X.md": THEN_HISTORICAL}, LIVE_TOTAL, LIVE_BUYABLE), True)

# 6. No matching sentence at all: nothing to check, not a failure.
check("no mention, nothing to check",
      preflight.catalogue_buyable_count_drift(
          {"X.md": NO_MENTION}, LIVE_TOTAL, LIVE_BUYABLE), True)

# 7. The real, fixed files must be clean today.
for name in ("GOALS.md", "STRIPE.md", "RISKS.md", "EXPERIMENT-PLAN.md"):
    text = io.open(os.path.join(ROOT, name), encoding="utf-8").read()
    check(f"real {name}, no drift",
          preflight.catalogue_buyable_count_drift(
              {name: text}, LIVE_TOTAL, LIVE_BUYABLE), True)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
