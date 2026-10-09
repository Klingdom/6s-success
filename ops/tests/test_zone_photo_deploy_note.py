#!/usr/bin/env python3
"""
The "Redeploy the site" owner note must not claim zone photography is
undeployed once it has actually shipped.

Found 2026-10-09, PM check-in: the note fired the same hardcoded "no zone
page carries its photograph yet" clause unconditionally, any time
deploy_verdict == "stale". That stayed true for three cycles after the
2026-10-09T05:32:43Z confirmed deploy, which had already shipped the zone
photographs (the verdict's own commit, read directly, already carried
site/assets/zones/*.jpg and the zone-hero markup); the three commits since
then (a sitemap dedup, a canonical-link fix, a cron-cadence fix) never
touched a zone page's photography at all, yet the dashboard kept telling
the owner a finished, shipped piece of customer-facing work was still
waiting on them.

dashboard.py runs its whole pipeline at import, so the function is lifted
out of the source rather than imported, matching
test_dashboard_prev_state_fallback.py's own method for the same reason.

Run:  python ops/tests/test_zone_photo_deploy_note.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "ops", "dashboard.py")

src = open(SRC, encoding="utf-8").read()
ns = {}
m = re.search(r"^def zone_photo_deploy_note.*?(?=\n\ndef _load_deploy_marker)",
              src, re.S | re.M)
exec(m.group(0), ns)
zone_photo_deploy_note = ns["zone_photo_deploy_note"]


def main() -> int:
    fails = []

    # Confirmed not touched (the 2026-10-09 regression case): must say so
    # plainly and must not claim photos are undeployed or that anyone is
    # being reached by nothing.
    clause, tail = zone_photo_deploy_note(False, 114)
    if "already matches the last confirmed deploy" not in clause:
        fails.append(f"False must state photography already matches "
                      f"the confirmed deploy, got clause={clause!r}")
    if "no zone page carries its photograph" in clause:
        fails.append("False must not keep the undeployed-photo claim")
    if tail:
        fails.append(f"False must have no 'reach nobody' tail, got {tail!r}")
    if "114" not in clause:
        fails.append(f"False must cite the real zone_pages_with_image count, "
                      f"got clause={clause!r}")

    # Confirmed touched: keep the original warning, with the real count in
    # the tail.
    clause, tail = zone_photo_deploy_note(True, 114)
    if "no zone page carries its photograph yet" not in clause:
        fails.append(f"True must keep the undeployed-photo warning, got "
                      f"clause={clause!r}")
    if "114" not in tail:
        fails.append(f"True must cite the real count in its tail, got "
                      f"tail={tail!r}")

    # Unknown (verdict commit could not be resolved): must take the
    # cautious branch, identical to True, never silently read as
    # "confirmed live" just because nobody could check.
    none_result = zone_photo_deploy_note(None, 114)
    true_result = zone_photo_deploy_note(True, 114)
    if none_result != true_result:
        fails.append(f"None must behave exactly like True (cannot tell is "
                      f"not confirmed live), got {none_result!r} vs "
                      f"{true_result!r}")

    total = 3
    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {total - len(fails)} of {total} cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
