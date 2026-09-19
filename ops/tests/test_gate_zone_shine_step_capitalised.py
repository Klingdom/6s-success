#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_zone_shine_step_capitalised() catches a
lowercase-first Shine step name/answer, in both places it can appear: the
visible FAQPage "What do you clean first" answer, and the JSON-LD HowToStep
"name" for the Shine section's own sub-steps.

Found 2026-09-19, the narrative cold-read of site/zones/*.html's previously
untracked half. content.json's per-surface "surface" label is free text and
29 of 115 zones (all 5 Entryway zones plus a scattering elsewhere) author it
lowercase ("the wall and back edge behind the console"). The visible
"Cleaning it properly, surface by surface" list already capitalised this
field before printing it; the FAQ answer and the JSON-LD step name did not,
shipping a live sentence that opened mid-word right after a question mark.
Fixed with a shared _cap() helper in ops/build_zone_pages.py.

Run:  python ops/tests/test_gate_zone_shine_step_capitalised.py
"""
import glob
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

FAQ_GOOD = (
    '<dt>What do you clean first in the bench or console?</dt>'
    '<dd>The wall and back edge behind the console. Wipe it down.</dd>'
)
FAQ_BAD = (
    '<dt>What do you clean first in the bench or console?</dt>'
    '<dd>the wall and back edge behind the console. Wipe it down.</dd>'
)

JSONLD_GOOD = (
    '<script type="application/ld+json">'
    '[{"@type": "HowTo", "step": [{"@type": "HowToSection", "name": "Shine", '
    '"itemListElement": [{"@type": "HowToStep", "position": 1, '
    '"name": "The console top", "text": "Wipe it."}]}]}]'
    '</script>'
)
JSONLD_BAD = (
    '<script type="application/ld+json">'
    '[{"@type": "HowTo", "step": [{"@type": "HowToSection", "name": "Shine", '
    '"itemListElement": [{"@type": "HowToStep", "position": 1, '
    '"name": "the console top", "text": "Wipe it."}]}]}]'
    '</script>'
)

PASS, FAILCOUNT = 0, 0


def check(name, condition):
    global PASS, FAILCOUNT
    if condition:
        PASS += 1
    else:
        FAILCOUNT += 1
        print(f"  FAIL: {name}")


def _run(files):
    """Write files into a throwaway <tmp>/site/zones/ (the gate builds its
    own path from ROOT, not SITE) and run the real gate against it,
    restoring preflight's ROOT afterward either way."""
    tmp = tempfile.mkdtemp()
    zones = os.path.join(tmp, "site", "zones")
    os.makedirs(zones)
    for name, content in files.items():
        io.open(os.path.join(zones, name), "w", encoding="utf-8").write(content)
    real_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL.clear()
    try:
        preflight.gate_zone_shine_step_capitalised()
        return list(preflight.FAIL)
    finally:
        preflight.ROOT = real_root
        shutil.rmtree(tmp)


def main():
    # 1. Clean page (both surfaces capitalised): no failure.
    fails = _run({"clean.html": FAQ_GOOD + JSONLD_GOOD})
    check("clean page: no failure", fails == [])

    # 2. Lowercase FAQ answer: caught by name.
    fails = _run({"bad-faq.html": FAQ_BAD + JSONLD_GOOD})
    check("lowercase FAQ answer caught",
          any("bad-faq.html" in m and "FAQ answer" in m for _, m in fails))

    # 3. Lowercase JSON-LD HowToStep name: caught by name.
    fails = _run({"bad-jsonld.html": FAQ_GOOD + JSONLD_BAD})
    check("lowercase HowToStep name caught",
          any("bad-jsonld.html" in m and "HowToStep name" in m
              for _, m in fails))

    # 4. Both wrong at once on the same page: at least one failure naming it.
    fails = _run({"bad-both.html": FAQ_BAD + JSONLD_BAD})
    check("both defects on one page still fail",
          any("bad-both.html" in m for _, m in fails))

    # 5. A page with a non-alphabetic first character (e.g. a number) must
    # not false-positive: islower() is False for a digit too.
    faq_digit = FAQ_GOOD.replace("The wall", "3 wall surfaces")
    fails = _run({"digit-start.html": faq_digit + JSONLD_GOOD})
    check("a digit-first answer does not false-positive", fails == [])

    # 6. Sanity: the real committed site/zones/*.html corpus is clean today,
    # run against the real disk (not a synthetic fixture).
    preflight.FAIL.clear()
    preflight.gate_zone_shine_step_capitalised()
    check("real site/zones/ corpus clean today", preflight.FAIL == [])

    print(f"\n{PASS} of {PASS + FAILCOUNT} cases pass")
    return 1 if FAILCOUNT else 0


if __name__ == "__main__":
    sys.exit(main())
