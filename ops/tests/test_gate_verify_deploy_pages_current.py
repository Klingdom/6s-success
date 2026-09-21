#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_verify_deploy_pages_current() catches
ops/verify_deploy.py's PAGES silently dropping a critical customer path,
and catches CRITICAL_PAGES naming a page that no longer exists in site/.

Found 2026-09-21, this operator: PAGES covered every marketing page but
never quest.html (the Home Quest app), deck.html (the free lead magnet),
corporate.html (the B2B enquiry funnel) or thanks.html (the post-checkout
page). A deploy that broke any of those would have scored 10 of 10 while
the thing a customer actually clicked on was broken. Fixed by adding them,
and this gate is what stops the same page-list gap recurring unnoticed.

Run:  python ops/tests/test_gate_verify_deploy_pages_current.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import verify_deploy as VD                                     # noqa: E402


def _run():
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_verify_deploy_pages_current()
    return list(preflight.FAIL), list(preflight.WARN)


def main() -> int:
    fails = []
    orig_pages = list(VD.PAGES)
    orig_crit = set(VD.CRITICAL_PAGES)

    # 1. The real regression shape: a critical page quietly removed from
    #    PAGES (this is exactly how quest/deck/corporate/thanks were missing
    #    until this cycle).
    VD.PAGES = [p for p in orig_pages if p != "quest"]
    r, w = _run()
    if not r or r[0][0] != "verify-deploy-pages-current":
        fails.append("dropping a critical page from PAGES was not caught: %r" % (r,))
    elif "quest" not in r[0][1]:
        fails.append("failure message did not name the dropped page: %r" % (r[0][1],))
    VD.PAGES = orig_pages

    # 2. CRITICAL_PAGES naming a page that does not exist in site/: caught
    #    only once it is also present in PAGES (otherwise case 1's check
    #    fires first, which is itself correct: either gap is real).
    VD.PAGES = orig_pages + ["this-page-does-not-exist"]
    VD.CRITICAL_PAGES = orig_crit | {"this-page-does-not-exist"}
    r, w = _run()
    if not r or r[0][0] != "verify-deploy-pages-current":
        fails.append("a critical page missing from site/ was not caught: %r" % (r,))
    elif "this-page-does-not-exist" not in r[0][1]:
        fails.append("failure message did not name the missing file: %r" % (r[0][1],))
    VD.PAGES = orig_pages
    VD.CRITICAL_PAGES = orig_crit

    # 3. The real committed state: every critical page is in PAGES and
    #    exists on disk, so this must pass clean.
    r, w = _run()
    if r:
        fails.append("the real committed state failed: %r" % (r,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_verify_deploy_pages_current, 3/3 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
