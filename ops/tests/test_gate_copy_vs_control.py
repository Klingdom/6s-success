#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_copy_vs_control() is not fooled by a stray
site/**/_*.html scratch fixture, and that the real, committed site is clean.

Found 2026-10-10, scheduled operator cycle: a live preflight run reported
"1 price(s) written in prose that match nothing in the catalogue:
[('_audit_catalog_fixture_620.html', '$34')]", a real warning at the time it
fired but not a real defect: test_audit_catalog.py plants
site/_audit_catalog_fixture_<pid>.html with a deliberately fake price to test
audit_catalog.py, and gate_copy_vs_control's own all_pages() scan read that
fake price as real site copy. all_pages() deliberately does not exclude
underscore-prefixed files (three other gates' own planted-fixture tests need
them left in); the fix, matching gate_no_stale_hardcoded_stripe_link and
gate_footer_consistent, is a local filter inside this one gate.

Run:  python ops/tests/test_gate_copy_vs_control.py
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

passed = failed = 0


def check(name, ok):
    global passed, failed
    if ok:
        passed += 1
    else:
        failed += 1
        print(f"FAIL {name}")


# 1. The real, committed site must be clean today.
saved_warn = list(preflight.WARN)
try:
    preflight.WARN.clear()
    preflight.gate_copy_vs_control()
    check("real committed site, no copy-vs-control warning", preflight.WARN == [])
finally:
    preflight.WARN[:] = saved_warn

# 2. Reproduce the 2026-10-10 false positive directly: a concurrent
# test_audit_catalog.py run's own _audit_catalog_fixture_<pid>.html, planted
# in the real site/ directory with a price next to a buy word, must not make
# gate_copy_vs_control() itself report a mismatched price. Calls the real
# gate function against the real site/ tree, since the bug was in how the
# gate assembles its file list from all_pages(), not in its regex logic.
fixture_path = os.path.join(SITE, "_audit_catalog_fixture_999999999.html")
saved_warn = list(preflight.WARN)
try:
    io.open(fixture_path, "w", encoding="utf-8").write(
        "<html><body><p>Buy it now for just $34 before the sale ends."
        "</p></body></html>\n")
    preflight.WARN.clear()
    preflight.gate_copy_vs_control()
    check("stray _audit_catalog_fixture file does not false-warn the real gate",
          preflight.WARN == [])
finally:
    if os.path.exists(fixture_path):
        os.remove(fixture_path)
    preflight.WARN[:] = saved_warn

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
