#!/usr/bin/env python3
"""
Prove ops/preflight.py's site_secret_key_leaks()/
gate_no_live_secret_key_in_site() catch a Stripe secret or restricted key
pattern planted under site/, and that the real, committed site is clean
today.

Found 2026-10-10: ops/stripe_check.py already carried this exact scan
(`leak_scan()`), but only reached it after confirming STRIPE_SECRET_KEY was
loaded locally, so it never actually ran in any sandboxed cycle, which is
every automated cycle this repository has ever run from. This gate runs the
same check unconditionally, with no credential needed.

Run:  python ops/tests/test_gate_no_live_secret_key_in_site.py
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

passed = failed = 0


def check(name, got, want_empty):
    global passed, failed
    ok = (len(got) == 0) if want_empty else (len(got) > 0)
    if ok:
        passed += 1
    else:
        failed += 1
        print(f"FAIL {name}: got {got!r}, want_empty={want_empty}")


# 1. The real, committed site must be clean today.
check("real committed site, no secret key pattern",
      preflight.site_secret_key_leaks(),
      True)

# 2. Plant a live secret key pattern under site/, call the real gate
#    function (not just the pure helper), confirm it fails, then clean up
#    and confirm it passes again. Proves fail-then-pass, not just "it ran".
fixture_path = os.path.join(SITE, "_secret_leak_fixture_999999999.html")
saved_fail = list(preflight.FAIL)
try:
    io.open(fixture_path, "w", encoding="utf-8").write(
        "<!-- sk_live_" + "0" * 24 + " -->\n")
    preflight.FAIL.clear()
    preflight.gate_no_live_secret_key_in_site()
    check("planted secret key pattern fails the real gate",
          preflight.FAIL, False)

    os.remove(fixture_path)
    preflight.FAIL.clear()
    preflight.gate_no_live_secret_key_in_site()
    check("gate passes again once the fixture is removed",
          preflight.FAIL, True)
finally:
    if os.path.exists(fixture_path):
        os.remove(fixture_path)
    preflight.FAIL[:] = saved_fail

# 3. A restricted key (rk_) pattern must be caught too, not only sk_.
rk_fixture = os.path.join(SITE, "_secret_leak_fixture_rk_999999999.html")
saved_fail = list(preflight.FAIL)
try:
    io.open(rk_fixture, "w", encoding="utf-8").write(
        "<!-- rk_test_" + "0" * 24 + " -->\n")
    preflight.FAIL.clear()
    preflight.gate_no_live_secret_key_in_site()
    check("restricted key pattern (rk_) fails the real gate too",
          preflight.FAIL, False)
finally:
    if os.path.exists(rk_fixture):
        os.remove(rk_fixture)
    preflight.FAIL[:] = saved_fail

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
