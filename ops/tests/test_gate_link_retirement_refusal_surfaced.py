#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_link_retirement_refusal_surfaced() can
actually fail, and that it stays quiet on the ordinary, no-refusal case.

REVIEW-COMMERCE-2026-09-07.md C17: ops/stripe_catalog.py's ensure_link()
correctly REFUSES to retire a payment link that still charges a price the
catalogue has since retired, whenever the live site's own state cannot
confirm the old link is safe to kill (unreadable, or still serving it).
Until this fix the only trace of that refusal was a print() in a terminal
nobody re-reads after the run ends: a real customer could keep paying the
wrong price indefinitely with nothing on the dashboard or in the hourly
brief ever saying so.

No sandbox this repository has ever run in holds a Stripe credential, so
the real refusal branch has never fired here and this test cannot wait for
one to. It constructs the refusal by hand instead, the same way
test_gate_pricing_deck_ladder_current.py constructs a stale document by
hand rather than waiting for one to drift.

Run:  python ops/tests/test_gate_link_retirement_refusal_surfaced.py
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import dashboard                                               # noqa: E402
import hourly_brief                                            # noqa: E402
import preflight                                               # noqa: E402
import stripe_catalog                                          # noqa: E402


def main() -> int:
    fails = []
    refusal = [{"sku": "TEST-SKU", "reason": "the live site is still "
                "serving it. Deploy first, then rerun."}]

    # 1. status_of() must escalate to RED and name the sku, the exact defect
    #    shape this whole feature exists to close: a real refusal sitting
    #    invisible next to an otherwise-healthy dashboard.
    status, why = dashboard.status_of(True, True, "unknown", True, 0, None, refusal)
    if status != "RED" or "TEST-SKU" not in why:
        fails.append(f"status_of() with a refused retirement returned "
                     f"{status!r}/{why!r}, expected RED naming TEST-SKU")

    # 2. No refusal at all: must not fire. This is the overwhelming common
    #    case (most cycles never run stripe_catalog.py --apply).
    status, _ = dashboard.status_of(True, True, "unknown", True, 0, None, [])
    if status != "GREEN":
        fails.append(f"status_of() with no refusal at all returned "
                     f"{status!r}, expected GREEN")
    status, _ = dashboard.status_of(True, True, "unknown", True, 0, None, None)
    if status != "GREEN":
        fails.append(f"status_of() with link_retirement_refused=None "
                     f"returned {status!r}, expected GREEN")

    # 3. A confirmed dead live-links verdict must still win: the worse
    #    outage (no link works at all) has to stay the reported reason, not
    #    get quietly replaced by the milder mispriced-link case.
    status, why = dashboard.status_of(True, True, "dead", True, 0, None, refusal)
    if status != "RED" or "deactivated" not in why.lower():
        fails.append(f"a refused retirement changed the reason given for a "
                     f"confirmed dead live-links verdict to {why!r}")

    # 4. hourly_brief.link_retirement_summary() must report the problem and
    #    name the sku when state carries a refusal.
    problem, lines = hourly_brief.link_retirement_summary(
        {"link_retirement_refused": refusal,
         "link_retirement_refused_at": "2026-09-22T00:00:00+00:00"})
    joined = " ".join(lines)
    if not problem or "TEST-SKU" not in joined:
        fails.append(f"link_retirement_summary() with a refusal did not "
                     f"report it: problem={problem!r} lines={lines!r}")

    # 5. And must read OK, not UNCHECKED, when state carries none: this
    #    summary is derived from a file already on disk, unlike the sibling
    #    Stripe-read summaries in the same module that can go UNCHECKED.
    problem, lines = hourly_brief.link_retirement_summary({})
    if problem:
        fails.append(f"link_retirement_summary() with no refusal reported "
                     f"a problem: lines={lines!r}")
    if any("unchecked" in l.lower() for l in lines):
        fails.append(f"link_retirement_summary() with no refusal read as "
                     f"UNCHECKED instead of OK: lines={lines!r}")

    # 6. Round trip: stripe_catalog.persist_refusals() writes a file
    #    dashboard.py's own loader can read back, sku and reason intact,
    #    proving the two ends of this feature agree on a shape neither
    #    hard-codes the other's assumptions into.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "link-retirement-refused.json")
        stripe_catalog.persist_refusals(refused=refusal, path=path)
        with io.open(path, encoding="utf-8") as f:
            data = json.load(f)
        if data.get("refused") != refusal:
            fails.append(f"persist_refusals() round trip lost data: "
                         f"wrote {refusal!r}, read back {data.get('refused')!r}")
        if not data.get("generated"):
            fails.append("persist_refusals() did not stamp a generated time")

    # 7. The gate itself must actually run clean end to end: fail() only
    #    appends to preflight's own module-level FAIL list, it never
    #    raises, so the real proof is that list's length before and after.
    before = len(preflight.FAIL)
    preflight.gate_link_retirement_refusal_surfaced()
    after = len(preflight.FAIL)
    if after != before:
        fails.append(f"gate_link_retirement_refusal_surfaced() itself "
                     f"failed: {preflight.FAIL[before:]!r}")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 7 checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
