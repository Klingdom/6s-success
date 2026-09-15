#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_revenue_model_cites_lrn0010()/
gate_revenue_model_checkout_caveat() catch a checkout-conversion claim in
ops/revenue_model.py or ROADMAP-2026-2029.md that has stopped citing
LEARNINGS.md's LRN-0010.

Found 2026-09-15: both files state "1 paid of 7" / "1-in-7 checkout rate"
as a MEASURED conversion figure, and both predate LRN-0010 (2026-09-14),
which traced every real checkout session since to the owner's own
household, not a stranger. Fixed by naming LRN-0010 next to each claim;
this gate keeps a future edit from silently dropping that caveat.

Run:  python ops/tests/test_gate_revenue_model_lrn0010.py
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

RM_GOOD = "CHECKOUT_PAID, CHECKOUT_TOTAL = 1, 7  # see LRN-0010\n"
RM_MISSING = "CHECKOUT_PAID, CHECKOUT_TOTAL = 1, 7  # measured\n"
RM_NO_CLAIM = "print('nothing about checkout conversion here')\n"

RD_GOOD = "the observed 1-in-7 checkout rate, see LRN-0010\n"
RD_MISSING = "the observed 1-in-7 checkout rate, a coincidence with a percent sign\n"
RD_NO_CLAIM = "nothing about checkout conversion here\n"

passed = failed = 0


def check(name, got, want):
    global passed, failed
    if got == want:
        passed += 1
    else:
        failed += 1
        print(f"FAIL {name}: got {got!r}, want {want!r}")


# 1. The real, fixed files must be clean today.
rm_path = os.path.join(ROOT, "ops", "revenue_model.py")
roadmap_path = os.path.join(ROOT, "ROADMAP-2026-2029.md")
rm_text = io.open(rm_path, encoding="utf-8").read()
roadmap_text = io.open(roadmap_path, encoding="utf-8").read()
problems = preflight.check_revenue_model_cites_lrn0010(rm_text, roadmap_text)
check("real files, no drift", problems, [])

# 2. The exact regression: revenue_model.py states the rate but drops the
#    citation.
problems = preflight.check_revenue_model_cites_lrn0010(RM_MISSING, RD_GOOD)
check("revenue_model.py missing citation caught", len(problems), 1)

# 3. The same shape in ROADMAP-2026-2029.md.
problems = preflight.check_revenue_model_cites_lrn0010(RM_GOOD, RD_MISSING)
check("ROADMAP missing citation caught", len(problems), 1)

# 4. Both missing at once: both named.
problems = preflight.check_revenue_model_cites_lrn0010(RM_MISSING, RD_MISSING)
check("both missing, both caught", len(problems), 2)

# 5. Both present and cited: clean.
problems = preflight.check_revenue_model_cites_lrn0010(RM_GOOD, RD_GOOD)
check("both cited, clean", problems, [])

# 6. A file that makes no checkout-rate claim at all has nothing to check
#    and must stay silent, not fail closed on an absent claim.
problems = preflight.check_revenue_model_cites_lrn0010(RM_NO_CLAIM, RD_NO_CLAIM)
check("no claim, silent", problems, [])

# 7. Empty/missing text (file not found) must not crash.
problems = preflight.check_revenue_model_cites_lrn0010("", "")
check("empty text, silent", problems, [])

print(f"{passed} of {passed + failed} cases pass")
sys.exit(1 if failed else 0)
