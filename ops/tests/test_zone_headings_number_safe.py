#!/usr/bin/env python3
"""
Prove no zone page forces singular agreement onto a plural zone noun.

WHY THIS EXISTS
---------------
The capacity and variants sections name the zone in their headings, and the
noun comes from ops/zone-search-terms.json or from the zone name. 19 of the 114
nouns are plural: "utensil and utility drawers", "dry goods shelves", "towels",
"baby clothes", "coat hooks". The original templates were written around a
singular noun and these shipped live:

    How much this utensil and utility drawers can actually hold
    If your utensil and utility drawers is not like this
    The passes above assume a fairly ordinary dry goods shelves.

Fixed by keeping the zone noun out of the subject position. "How much THE X
CAN hold" works for both numbers because a modal verb does not inflect, and
"When THIS does not describe your X" agrees with "this" rather than with X.

This is a grammar check, so it is deliberately crude and specific: it bans the
three shapes that were actually wrong rather than attempting to parse English.

Run:  python ops/tests/test_zone_headings_number_safe.py
"""
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

ZONES = os.path.join(ROOT, "site", "zones")
CORPUS = os.path.join(ROOT, "content", "manual", "source", "content.json")

BANNED = (
    ("How much this ", 'reads "How much this drawers can hold"'),
    (" is not like this</h2>", 'reads "If your drawers is not like this"'),
    ("assume a fairly ordinary ", 'reads "a fairly ordinary drawers"'),
)


def plural_nouns():
    """Zone nouns that are plural, derived the same way the generator does."""
    import build_zone_pages as B
    data = json.loads(io.open(CORPUS, encoding="utf-8").read())
    out = []
    for r in data["rooms"]:
        for z in r["zones"]:
            name = z["zone"] if z["zone"].startswith("The ") else "The " + z["zone"]
            t = B.searchable(r["room"], z["zone"], name)
            if re.search(r"(?<!s)s$", t) and not t.endswith(("ss", "us")):
                out.append(t)
    return out


def main():
    fails = []
    pages = sorted(glob.glob(os.path.join(ZONES, "*.html")))
    if len(pages) < 100:
        fails.append("only %d zone page(s) found, so this checked almost "
                     "nothing" % len(pages))

    # 1. None of the three broken shapes may appear anywhere.
    for f in pages:
        s = io.open(f, encoding="utf-8", errors="replace").read()
        for bad, why in BANNED:
            if bad in s:
                fails.append("%s contains %r, which %s"
                             % (os.path.basename(f), bad, why))

    # 2. The sections have to actually be there, or case 1 passes on a site
    #    that simply stopped rendering them.
    withcap = [f for f in pages if "How much the " in
               io.open(f, encoding="utf-8", errors="replace").read()]
    if len(withcap) < 40:
        fails.append("only %d page(s) carry a capacity heading, so the "
                     "wording check has almost nothing to check"
                     % len(withcap))

    # 3. And at least one of them must be a PLURAL zone, which is the whole
    #    point. A site where only singular zones carry these sections would
    #    pass case 1 while the bug sat waiting for the next rollout.
    plurals = plural_nouns()
    if len(plurals) < 5:
        fails.append("only %d plural zone noun(s) derived, so the generator's "
                     "naming may have changed under this test" % len(plurals))
    covered = []
    for f in withcap:
        s = io.open(f, encoding="utf-8", errors="replace").read()
        for t in plurals:
            if "How much the %s can" % t in s:
                covered.append(t)
    if not covered:
        fails.append("no page with a capacity heading uses a plural zone "
                     "noun, so nothing here exercises the agreement problem "
                     "this test exists for")

    if fails:
        print("FAIL")
        for f in sorted(set(fails))[:10]:
            print(" -", f)
        return 1
    print("OK: %d zone page(s), %d carry these sections, %d of those name a "
          "plural zone, none forces singular agreement"
          % (len(pages), len(withcap), len(set(covered))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
