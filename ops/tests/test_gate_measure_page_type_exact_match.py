#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_measure_page_type_exact_match() catches
site/assets/js/measure.js's page() going back to substring matching for
"quest" and "shop".

Real shape found 2026-10-03, this operator, a fresh cold-read of
measure.js (last ledgered clean 2026-09-27): page() used
`p.indexOf("quest") >= 0` and `p.indexOf("shop") >= 0` to label the page
type carried on every buy-click, outbound-click, quote-click, service-cta
and free-download event. site/workshop-deck.html contains "shop" inside
"workshop", the one collision among all twenty room decks, so every one
of those events fired from that page was silently folded into the online
store's own "shop" numbers instead of getting the "workshop-deck" label
page()'s own fallback gives every other deck. Fixed to exact equality
(`p === "/quest.html"`, `p === "/shop.html"`), which cannot be fooled by a
filename that merely contains either word.

Run:  python ops/tests/test_gate_measure_page_type_exact_match.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

REAL_PATH = os.path.join(ROOT, "site", "assets", "js", "measure.js")
FIXED_SRC = io.open(REAL_PATH, encoding="utf-8").read()

OLD_BUG_SRC = FIXED_SRC.replace(
    'p === "/quest.html"', 'p.indexOf("quest") >= 0'
).replace('p === "/shop.html"', 'p.indexOf("shop") >= 0')

# A different regression shape: exact-equal but against the wrong literal
# (a typo'd leading slash), which should still be caught since the real
# marker strings are gone.
TYPO_SRC = FIXED_SRC.replace('p === "/quest.html"', 'p === "quest.html"')


def _run_gate(src: str) -> list:
    tmp = tempfile.mkdtemp()
    try:
        site_dir = os.path.join(tmp, "site", "assets", "js")
        os.makedirs(site_dir, exist_ok=True)
        io.open(os.path.join(site_dir, "measure.js"), "w",
                encoding="utf-8").write(src)

        old_site = preflight.SITE
        preflight.SITE = os.path.join(tmp, "site")
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_measure_page_type_exact_match()
            return list(preflight.FAIL)
        finally:
            preflight.SITE = old_site
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    bad = []

    real_fail = _run_gate(FIXED_SRC)
    if real_fail:
        bad.append("the real, already-fixed measure.js failed the gate: %r"
                    % real_fail)

    bug_fail = _run_gate(OLD_BUG_SRC)
    if not bug_fail:
        bad.append("the pre-fix substring-matching shape (indexOf) did not "
                    "fail the gate")
    elif "workshop-deck" not in bug_fail[0][1]:
        bad.append("the substring-matching failure did not name the real "
                    "collision (workshop-deck.html): %r" % bug_fail)

    typo_fail = _run_gate(TYPO_SRC)
    if not typo_fail:
        bad.append("a typo'd exact-match literal (missing leading slash) "
                    "did not fail the gate")

    # A missing file entirely must not be treated as a failure: plenty of
    # gates in this file return early when their target does not exist,
    # and this one should behave the same way rather than inventing a
    # defect out of absence.
    tmp = tempfile.mkdtemp()
    try:
        old_site = preflight.SITE
        preflight.SITE = os.path.join(tmp, "site")
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_measure_page_type_exact_match()
            if preflight.FAIL:
                bad.append("a missing measure.js produced a failure instead "
                            "of being skipped: %r" % preflight.FAIL)
        finally:
            preflight.SITE = old_site
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if bad:
        for b in bad:
            print("  FAIL " + b)
        return 1
    print("  ok  real measure.js passes; substring-matching regression and "
          "a typo'd literal both fail by name; a missing file is skipped, "
          "not failed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
