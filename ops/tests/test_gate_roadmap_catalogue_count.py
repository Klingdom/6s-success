#!/usr/bin/env python3
"""
Prove ops/preflight.py's roadmap_catalogue_count_drift()/
gate_roadmap_catalogue_count_current() catch ROADMAP-2026-2029.md's
section 3c catalogue-size headline drifting from its own listed breakdown
or from the live catalogue.

Found 2026-09-20: section 3c's headline, "The catalogue is 164 items, not
10," sits one clause before its own breakdown, 114 zone packs + 20 room
packs + 15 situation kits + 6 area bundles, which sums to 155, not 164,
and has since 2026-08-26. gate_roadmap_prices_current already polices this
same document's section 1 price table and page count; this closes the
matching gap in section 3c.

Run:  python ops/tests/test_gate_roadmap_catalogue_count.py
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

LIVE = {"zone packs": 114, "room packs": 20, "situation kits": 15,
        "area bundles": 6}

GOOD = (
    "**The catalogue is 155 items, not 10.** The content spine supports 114 zone\n"
    "packs at $4, 20 room packs at $9, 15 curated situation kits at $14 and 6 area\n"
    "bundles at $16 (corrected 2026-09-01), all\n"
    "generated and all deliverable the moment somebody pays.\n"
)

STALE_ARITHMETIC = (
    "**The catalogue is 164 items, not 10.** The content spine supports 114 zone\n"
    "packs at $4, 20 room packs at $9, 15 curated situation kits at $14 and 6 area\n"
    "bundles at $16 (corrected 2026-09-01), all\n"
    "generated and all deliverable the moment somebody pays.\n"
)

STALE_COMPONENT = (
    "**The catalogue is 155 items, not 10.** The content spine supports 109 zone\n"
    "packs at $4, 20 room packs at $9, 15 curated situation kits at $14 and 6 area\n"
    "bundles at $16 (corrected 2026-09-01), all\n"
    "generated and all deliverable the moment somebody pays.\n"
)
# 109 + 20 + 15 + 6 = 150, so this also drifts the headline; kept as a
# separate case anyway because it exercises the live-count mismatch path
# specifically (both problems will fire, and that is fine).

MISSING_COMPONENT = (
    "**The catalogue is 155 items, not 10.** The content spine supports 114 zone\n"
    "packs at $4, 20 room packs at $9, and 6 area\n"
    "bundles at $16, all\n"
    "generated and all deliverable the moment somebody pays.\n"
)

NO_SENTENCE = "Nothing about a catalogue count here at all.\n"

passed = failed = 0


def check(name, got, want_empty):
    global passed, failed
    ok = (len(got) == 0) if want_empty else (len(got) > 0)
    if ok:
        passed += 1
    else:
        failed += 1
        print(f"FAIL {name}: got {got!r}, want_empty={want_empty}")


# 1. The real, fixed file must be clean today.
real_path = os.path.join(ROOT, "ROADMAP-2026-2029.md")
real_text = io.open(real_path, encoding="utf-8").read()
check("real file, no drift", preflight.roadmap_catalogue_count_drift(real_text, LIVE), True)

# 2. The exact regression this gate was built to catch: 164 vs. the real sum 155.
check("stale headline arithmetic",
      preflight.roadmap_catalogue_count_drift(STALE_ARITHMETIC, LIVE), False)

# 3. A clean headline but a component that no longer matches the live catalogue.
check("component drifted from live catalogue",
      preflight.roadmap_catalogue_count_drift(STALE_COMPONENT, LIVE), False)

# 4. A missing component (situation kits dropped from the sentence) must be reported,
#    not silently skipped.
check("missing component reported",
      preflight.roadmap_catalogue_count_drift(MISSING_COMPONENT, LIVE), False)

# 5. The fixed, correct text must be clean.
check("fixed text, clean", preflight.roadmap_catalogue_count_drift(GOOD, LIVE), True)

# 6. No matching sentence at all: nothing to check, not a failure.
check("no sentence present, nothing to check",
      preflight.roadmap_catalogue_count_drift(NO_SENTENCE, LIVE), True)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
