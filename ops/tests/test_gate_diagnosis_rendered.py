#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_diagnosis_rendered() catches the defect
classes PLAN-MICROZONES-DECKS-APP.md's M4 acceptance names: a diagnosed zone
whose page never got regenerated, a related-reading block outside the 3 to 5
link range, two diagnosed zones sharing an identical reading set, and the
real grammar defect this cycle shipped once and caught by reading the
rendered page rather than any upstream check: a whole symptom sentence
lowercased before being embedded in a question, turning "how often I sort
it" into "how often i sort it" in visible text and in the FAQPage JSON-LD.

Run:  python ops/tests/test_gate_diagnosis_rendered.py
"""
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

GOOD_READING = (
    '<h2>Related reading</h2><ul>'
    '<li><a href="../articles/a.html">A</a></li>'
    '<li><a href="../articles/b.html">B</a></li>'
    '<li><a href="../articles/c.html">C</a></li>'
    '</ul>'
)
GOOD_FAQ = (
    '<dl class="faq-list">'
    '<dt>Why does the drop zone do this: The folder is never under ten '
    'sheets, no matter how often I sort it?</dt>'
    '<dd>Nothing has been given a verdict, so start at Sort.</dd>'
    '</dl>'
)


def _page(reading=GOOD_READING, faq=GOOD_FAQ, diagnosed=True):
    body = faq + reading
    if diagnosed:
        body = '<section id="diagnosis">...</section>' + body
    return body


def _load_real():
    src = os.path.join(ROOT, "content", "manual", "source", "content.json")
    rooms = json.load(io.open(src, encoding="utf-8"))["rooms"]
    diagnosed = sum(1 for r in rooms for z in r.get("zones", [])
                     if z.get("diagnosis"))
    return diagnosed


def main() -> int:
    fails = []

    # 1. Two clean synthetic pages with distinct reading sets: no problems.
    pages = {
        "z1.html": _page(),
        "z2.html": _page(reading=GOOD_READING.replace("a.html", "d.html")),
    }
    problems = preflight.check_diagnosis_rendered(2, pages)
    if problems:
        fails.append("clean synthetic pages wrongly flagged: %s" % problems)

    # 2. Count mismatch: corpus says 3 diagnosed, only 2 pages render one.
    problems = preflight.check_diagnosis_rendered(3, pages)
    if not problems:
        fails.append("count mismatch (3 diagnosed, 2 rendered) NOT caught")

    # 3. Too few related-reading links.
    thin = dict(pages)
    thin["z1.html"] = _page(reading=(
        '<h2>Related reading</h2><ul>'
        '<li><a href="../articles/a.html">A</a></li></ul>'))
    problems = preflight.check_diagnosis_rendered(2, thin)
    if not any("1 related-reading" in p for p in problems):
        fails.append("under-count related reading (1 link) NOT caught")

    # 4. Too many related-reading links.
    fat = dict(pages)
    fat["z1.html"] = _page(reading=(
        '<h2>Related reading</h2><ul>' +
        "".join('<li><a href="../articles/%d.html">%d</a></li>' % (i, i)
                for i in range(6)) + '</ul>'))
    problems = preflight.check_diagnosis_rendered(2, fat)
    if not any("6 related-reading" in p for p in problems):
        fails.append("over-count related reading (6 links) NOT caught")

    # 5. Two diagnosed zones with an identical reading set.
    dupe = {"z1.html": _page(), "z2.html": _page()}
    problems = preflight.check_diagnosis_rendered(2, dupe)
    if not any("identical related-reading set" in p for p in problems):
        fails.append("duplicate related-reading set NOT caught")

    # 6. The real grammar defect: a lowercased "I" inside the diagnosis FAQ.
    bad_faq = GOOD_FAQ.replace("how often I sort it", "how often i sort it")
    lowered = dict(pages)
    lowered["z1.html"] = _page(faq=bad_faq)
    problems = preflight.check_diagnosis_rendered(2, lowered)
    if not any("standalone lowercase" in p for p in problems):
        fails.append("lowercased pronoun in diagnosis FAQ text NOT caught")

    # 7. No false positive: "i" as part of a real word (e.g. "with") must
    #    not trip the word-boundary check.
    ok_faq = GOOD_FAQ.replace(
        "Nothing has been given a verdict",
        "Fixing it means giving it a home")
    clean = dict(pages)
    clean["z1.html"] = _page(faq=ok_faq)
    problems = preflight.check_diagnosis_rendered(2, clean)
    if problems:
        fails.append("false positive on ordinary word containing 'i': %s"
                      % problems)

    # 8. The real, live site (if built) passes clean today.
    diagnosed = _load_real()
    if diagnosed:
        real_pages = {}
        for f in sorted(glob.glob(os.path.join(ROOT, "site", "zones", "*.html"))):
            real_pages[os.path.basename(f)] = io.open(
                f, encoding="utf-8", errors="replace").read()
        if real_pages:
            problems = preflight.check_diagnosis_rendered(diagnosed, real_pages)
            if problems:
                fails.append("real, built site wrongly flagged: %s" % problems)
        else:
            print("  note: site/zones/ not built in this environment, "
                  "skipping the live-site case")

    if fails:
        print("FAILED %d case(s):" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("PASSED 8 cases (clean pages pass, all five defect classes "
          "caught, no false positive, real site clean if built)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
