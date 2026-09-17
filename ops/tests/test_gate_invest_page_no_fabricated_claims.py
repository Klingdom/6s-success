#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_invest_page_no_fabricated_claims() catches a
return of any of the specific unsourced statistics and fabricated-capability
claims REVIEW-QA-2026-09-07.md confirmed as P0 on site/invest.html, and
passes clean on the real, fixed committed file.

Found 2026-09-07 in that review, handed to the operator again 2026-09-17
after sitting confirmed and unfixed for ten days: the page stated as present
fact several unsourced superlatives/rankings ("the number-one reason," "a
multi-billion-dollar market," "than anyone else") and described a capability
that does not exist yet as though a customer could use it today ("3 Ways to
buy: app, web, done-for-you," "the exact 15-minute method, in the app," "we
buy them in volume, hold less inventory," "kit-ready"), while the page's own
Traction section already honestly disclosed the phone app as a prototype.
Fixed 2026-09-17.

Run:  python ops/tests/test_gate_invest_page_no_fabricated_claims.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

BANNED = [
    "number-one reason",
    "multi-billion-dollar",
    "than anyone else",
    "kit-ready",
    "in the app.",
    "we buy them in volume, hold less inventory,",
    "Ways to buy: app, web, done-for-you",
]


def _run(text):
    tmp = tempfile.mkdtemp()
    try:
        io.open(os.path.join(tmp, "invest.html"), "w",
                encoding="utf-8").write(text)
        old_site = preflight.SITE
        preflight.SITE = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_invest_page_no_fabricated_claims()
            return list(preflight.FAIL)
        finally:
            preflight.SITE = old_site
    finally:
        shutil.rmtree(tmp)


def main() -> int:
    fails = []
    clean = "<p>An honest fundraising page with no banned phrase on it.</p>"

    result = _run(clean)
    if result:
        fails.append("a genuinely clean page was wrongly flagged: %s" % result)

    for phrase in BANNED:
        result = _run(clean + " " + phrase)
        if not result:
            fails.append("banned phrase NOT caught: %r" % phrase)
        elif phrase not in str(result):
            fails.append("gate fired but did not name the phrase: %r -> %s"
                         % (phrase, result))

    # The real committed file, end to end: must be clean today.
    real_page = os.path.join(ROOT, "site", "invest.html")
    if os.path.exists(real_page):
        text = io.open(real_page, encoding="utf-8", errors="replace").read()
        found = [b for b in BANNED if b in text]
        if found:
            fails.append("the real committed file still carries: %s" % found)
    else:
        fails.append("site/invest.html is missing; nothing was checked")

    if fails:
        print("FAIL:")
        for f in fails:
            print(" -", f)
        return 1
    print("%d case(s) pass: gate_invest_page_no_fabricated_claims fires on "
          "each banned phrase and the real committed file is clean." %
          (2 + len(BANNED)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
