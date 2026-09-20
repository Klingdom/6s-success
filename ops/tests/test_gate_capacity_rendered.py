#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_capacity_rendered() catches the defect
classes REVIEW-DISCOVERY-2026-09-07.md D3's own acceptance names: a page
carrying the capacity block the corpus never authorised, a pilot zone whose
page never got regenerated after a content.json edit, a rule sentence that
drifted from what the corpus actually says (stale or paraphrased), a
does-not-fit sentence with no link to the article's own honest-count
anchor, an anchor that does not actually exist on the target article, and
two zones shipping an identical rule (the same anti-boilerplate shape
check_variants_rendered already guards for its own block).

Also runs against the real, committed corpus and site/zones/*.html, so a
future content.json edit that is never regenerated, or a regeneration that
silently drops the block, fails this test directly rather than waiting for
someone to notice on the live page.

Run:  python ops/tests/test_gate_capacity_rendered.py
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

ANCHOR = ('<a href="../articles/zone-too-small-for-what-it-holds.html'
          '#honest-count">Run the honest count</a>')


def _block(rule, fit, link=ANCHOR):
    out = ['<section id="capacity"><h2>How much this thing can actually '
           'hold</h2>',
           "<p>%s</p>" % bzp.esc(rule)]
    if fit:
        out.append("<p>%s %s</p>" % (bzp.esc(fit), link))
    out.append("</section>")
    return "".join(out)


GOOD_RULE = "One tray, sized for keys and one phone per adult."
GOOD_FIT = "If it still will not close, the tray is undersized."


def _load_real():
    src = os.path.join(ROOT, "content", "manual", "source", "content.json")
    rooms = json.load(io.open(src, encoding="utf-8"))["rooms"]
    capacity_map = {}
    for r in rooms:
        for z in r.get("zones", []):
            cap = z.get("capacity")
            if not cap or not cap.get("rule"):
                continue
            name = bzp.display(r["room"], z["zone"])
            rs, zs = bzp.slug(r["room"]), bzp.slug(name)
            capacity_map["%s-%s.html" % (rs, zs)] = (
                cap.get("rule", ""), cap.get("does_not_fit", ""))
    return capacity_map


def main() -> int:
    fails = []

    # 1. Clean synthetic page: no problems.
    pages = {"z1.html": _block(GOOD_RULE, GOOD_FIT)}
    cmap = {"z1.html": (GOOD_RULE, GOOD_FIT)}
    problems = preflight.check_capacity_rendered(cmap, pages)
    if problems:
        fails.append("clean synthetic page wrongly flagged: %s" % problems)

    # 2. A page renders the block but the corpus never authorised it.
    problems = preflight.check_capacity_rendered({}, pages)
    if not problems:
        fails.append("un-authorised capacity block NOT caught")

    # 3. A pilot zone has capacity in the corpus but its page carries none
    #    (never regenerated).
    problems = preflight.check_capacity_rendered(cmap, {"z1.html": "<p>stale</p>"})
    if not problems:
        fails.append("missing capacity block on a pilot zone NOT caught")

    # 4. Stale/paraphrased rule: the page's text no longer matches the
    #    corpus's own words.
    stale_pages = {"z1.html": _block("Something else entirely.", GOOD_FIT)}
    problems = preflight.check_capacity_rendered(cmap, stale_pages)
    if not problems:
        fails.append("paraphrased/stale rule NOT caught")

    # 5. The does-not-fit sentence renders but with no link to the
    #    honest-count anchor at all (the exact gap D3 exists to close).
    unlinked = ('<section id="capacity"><h2>How much this thing can '
                'actually hold</h2><p>%s</p><p>%s</p></section>'
                % (bzp.esc(GOOD_RULE), bzp.esc(GOOD_FIT)))
    problems = preflight.check_capacity_rendered(cmap, {"z1.html": unlinked})
    if not problems:
        fails.append("does-not-fit text with no honest-count link NOT caught")

    # 6. The link is present in shape but the anchor does not actually
    #    exist on the target article (article_has_anchor=False).
    problems = preflight.check_capacity_rendered(cmap, pages,
                                                  article_has_anchor=False)
    if not problems:
        fails.append("missing anchor on the target article NOT caught")

    # 7. Two zones sharing an identical rule (boilerplate, not
    #    differentiated per zone).
    dup_pages = {"z1.html": _block(GOOD_RULE, "First fit text."),
                 "z2.html": _block(GOOD_RULE, "Second, different fit text.")}
    dup_map = {"z1.html": (GOOD_RULE, "First fit text."),
               "z2.html": (GOOD_RULE, "Second, different fit text.")}
    problems = preflight.check_capacity_rendered(dup_map, dup_pages)
    if not problems:
        fails.append("two zones sharing an identical rule NOT caught")

    # 8. Against the real, committed corpus and site/zones/*.html: proves
    #    the 12 pilot zones actually ship what content.json says, today,
    #    and that the article they link really carries the anchor.
    real_map = _load_real()
    if len(real_map) != 12:
        fails.append("expected 12 pilot zones with capacity in the real "
                     "corpus, found %d (has the pilot cohort changed? "
                     "update this test's expectation deliberately if so)"
                     % len(real_map))
    real_pages = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "site", "zones", "*.html"))):
        real_pages[os.path.basename(f)] = io.open(
            f, encoding="utf-8", errors="replace").read()
    article_path = os.path.join(ROOT, "site", "articles",
                                 "zone-too-small-for-what-it-holds.html")
    real_anchor = ('id="honest-count"' in io.open(
        article_path, encoding="utf-8", errors="replace").read())
    if not real_anchor:
        fails.append("real committed article has no honest-count anchor")
    problems = preflight.check_capacity_rendered(real_map, real_pages, real_anchor)
    if problems:
        fails.append("real committed site fails its own check: %s" % problems)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: %d cases" % 8)
    return 0


if __name__ == "__main__":
    sys.exit(main())
