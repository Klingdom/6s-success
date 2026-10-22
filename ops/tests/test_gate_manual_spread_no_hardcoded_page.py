#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_manual_spread_no_hardcoded_page() catches
ops/build_product_images.py's manual_spread() going back to a hardcoded
PDF page index.

Real shape found 2026-10-22, scheduled operator, a fresh cold-read of
build_product_images.py (369 lines, never ledgered): manual_spread()
cropped the Manual's browser-printed PDF at a hardcoded page index (22,
and separately 5) to build product-manual.jpg's sample image. Chromium's
HTML-to-PDF pagination depends on font metrics and is not portable across
rendering environments: reproduced live, the identical source printed in
this sandbox put the intended "Lower Cabinet and Cookware Zone" heading
two pages earlier than where the shipped image was built, with no gate
tied to this generator checking content, only file existence
(gate_product_images_exist). Fixed with find_page(pdf, needle), which
locates a page by its own heading text instead of trusting a number that
only held on one machine.

Run:  python ops/tests/test_gate_manual_spread_no_hardcoded_page.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

REAL_PATH = os.path.join(ROOT, "ops", "build_product_images.py")
FIXED_SRC = io.open(REAL_PATH, encoding="utf-8").read()

# The pre-fix shape: both find_page() lookups reverted to hardcoded ints,
# the exact bug this gate exists to catch.
OLD_BUG_SRC = FIXED_SRC.replace(
    'under = fit(page(m, find_page(m, "Twenty rooms")), width=760)',
    "under = fit(page(m, 5), width=760)"
).replace(
    'zone = find_page(m, "Lower Cabinet and Cookware Zone")\n'
    "        top = fit(page(m, zone, dpi=220, clip=(0, 0, 504, 470)), "
    "width=980)",
    "top = fit(page(m, 22, dpi=220, clip=(0, 0, 504, 470)), width=980)"
)

# A narrower regression: find_page() itself removed (e.g. an unrelated
# refactor dropping the helper), leaving manual_spread() with nothing to
# call even if the call sites still say find_page(...).
NO_HELPER_SRC = FIXED_SRC.replace("def find_page(pdf, needle):",
                                   "def _unused_find_page(pdf, needle):")


def _run_gate(src: str) -> list:
    tmp = tempfile.mkdtemp()
    try:
        ops_dir = os.path.join(tmp, "ops")
        os.makedirs(ops_dir, exist_ok=True)
        io.open(os.path.join(ops_dir, "build_product_images.py"), "w",
                encoding="utf-8").write(src)

        old_root = preflight.ROOT
        preflight.ROOT = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_manual_spread_no_hardcoded_page()
            return list(preflight.FAIL)
        finally:
            preflight.ROOT = old_root
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    bad = []

    real_fail = _run_gate(FIXED_SRC)
    if real_fail:
        bad.append("the real, already-fixed build_product_images.py failed "
                    "the gate: %r" % real_fail)

    bug_fail = _run_gate(OLD_BUG_SRC)
    if not bug_fail:
        bad.append("the pre-fix hardcoded-page-index shape did not fail "
                    "the gate")
    elif "find_page" not in bug_fail[0][1]:
        bad.append("the hardcoded-index failure did not mention find_page: "
                    "%r" % bug_fail)

    no_helper_fail = _run_gate(NO_HELPER_SRC)
    if not no_helper_fail:
        bad.append("removing find_page() itself did not fail the gate")

    # A missing file entirely must not be treated as a failure, matching
    # every other gate in this file that skips rather than invents a
    # defect out of absence.
    tmp = tempfile.mkdtemp()
    try:
        old_root = preflight.ROOT
        preflight.ROOT = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_manual_spread_no_hardcoded_page()
            if preflight.FAIL:
                bad.append("a missing build_product_images.py produced a "
                            "failure instead of being skipped: %r"
                            % preflight.FAIL)
        finally:
            preflight.ROOT = old_root
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if bad:
        for b in bad:
            print("  FAIL " + b)
        return 1
    print("  ok  real build_product_images.py passes; a hardcoded-page-"
          "index regression and a removed find_page() helper both fail "
          "by name; a missing file is skipped, not failed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
