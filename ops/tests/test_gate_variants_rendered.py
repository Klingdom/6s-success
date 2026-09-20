#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_variants_rendered() catches the defect
classes REVIEW-DISCOVERY-2026-09-07.md D4's own acceptance names: a page
carrying the variants block the corpus never authorised, a pilot zone whose
page never got regenerated after a content.json edit, a guidance sentence
that drifted from what the corpus actually says (stale or paraphrased), too
few variants on a page, and two zones shipping identical guidance text (the
same anti-boilerplate shape check_diagnosis_rendered already guards for the
related-reading block).

Also runs against the real, committed corpus and site/zones/*.html, so a
future content.json edit that is never regenerated, or a regeneration that
silently drops the block, fails this test directly rather than waiting for
someone to notice on the live page.

Run:  python ops/tests/test_gate_variants_rendered.py
"""
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import build_zone_pages as bzp                                 # noqa: E402


def _block(pairs):
    out = ['<section id="variants"><h2>If your thing is not like this</h2>',
           '<p class="notice">intro</p><dl class="faq-list">']
    for cond, guide in pairs:
        out.append("<dt>%s</dt><dd>%s</dd>"
                   % (bzp.esc(cond), bzp.esc(guide)))
    out.append("</dl></section>")
    return "".join(out)


GOOD_PAIRS = [
    ("No console fits the space", "Use a wall hook instead."),
    ("Three people share it at once", "Give each their own tray."),
]


def _load_real():
    src = os.path.join(ROOT, "content", "manual", "source", "content.json")
    rooms = json.load(io.open(src, encoding="utf-8"))["rooms"]
    variant_map = {}
    for r in rooms:
        for z in r.get("zones", []):
            vs = z.get("variants")
            if not vs:
                continue
            name = bzp.display(r["room"], z["zone"])
            rs, zs = bzp.slug(r["room"]), bzp.slug(name)
            variant_map["%s-%s.html" % (rs, zs)] = [
                (v.get("condition", ""), v.get("guidance", "")) for v in vs]
    return variant_map


def main() -> int:
    fails = []

    # 1. Clean synthetic page: no problems.
    pages = {"z1.html": _block(GOOD_PAIRS)}
    vmap = {"z1.html": GOOD_PAIRS}
    problems = preflight.check_variants_rendered(vmap, pages)
    if problems:
        fails.append("clean synthetic page wrongly flagged: %s" % problems)

    # 2. A page renders the block but the corpus never authorised it.
    problems = preflight.check_variants_rendered({}, pages)
    if not problems:
        fails.append("un-authorised variants block NOT caught")

    # 3. A pilot zone has variants in the corpus but its page carries none
    #    (never regenerated).
    problems = preflight.check_variants_rendered(vmap, {"z1.html": "<p>stale</p>"})
    if not problems:
        fails.append("missing variants block on a pilot zone NOT caught")

    # 4. Stale/paraphrased guidance: the page's text no longer matches the
    #    corpus's own words.
    stale_pairs = [GOOD_PAIRS[0], ("Three people share it at once",
                                    "Something else entirely, not the real text.")]
    stale_pages = {"z1.html": _block(stale_pairs)}
    problems = preflight.check_variants_rendered(vmap, stale_pages)
    if not problems:
        fails.append("paraphrased/stale guidance NOT caught")

    # 5. Too few variants (D4 requires at least 2).
    thin_pages = {"z1.html": _block(GOOD_PAIRS[:1])}
    thin_map = {"z1.html": GOOD_PAIRS[:1]}
    problems = preflight.check_variants_rendered(thin_map, thin_pages)
    if not problems:
        fails.append("single-variant page (fewer than 2) NOT caught")

    # 6. Two zones sharing identical guidance text (boilerplate, not
    #    differentiated per zone).
    dup_pairs_a = [("Condition A1", "Shared identical guidance sentence."),
                   ("Condition A2", "Second, distinct sentence.")]
    dup_pairs_b = [("Condition B1", "Shared identical guidance sentence."),
                   ("Condition B2", "A different second sentence.")]
    dup_pages = {"z1.html": _block(dup_pairs_a), "z2.html": _block(dup_pairs_b)}
    dup_map = {"z1.html": dup_pairs_a, "z2.html": dup_pairs_b}
    problems = preflight.check_variants_rendered(dup_map, dup_pages)
    if not problems:
        fails.append("two zones sharing identical guidance text NOT caught")

    # 7. Against the real, committed corpus and site/zones/*.html: proves
    #    the 12 pilot zones actually ship what content.json says, today.
    real_map = _load_real()
    if len(real_map) != 12:
        fails.append("expected 12 pilot zones with variants in the real "
                     "corpus, found %d (has the pilot cohort changed? "
                     "update this test's expectation deliberately if so)"
                     % len(real_map))
    real_pages = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "site", "zones", "*.html"))):
        real_pages[os.path.basename(f)] = io.open(
            f, encoding="utf-8", errors="replace").read()
    problems = preflight.check_variants_rendered(real_map, real_pages)
    if problems:
        fails.append("real committed site fails its own check: %s" % problems)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: %d cases" % 7)
    return 0


if __name__ == "__main__":
    sys.exit(main())
