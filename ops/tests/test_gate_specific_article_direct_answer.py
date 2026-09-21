#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_specific_article_direct_answer() catches the
defect classes D12 (REVIEW-DISCOVERY-2026-09-07.md section 2) exists to
hold on the six specific-problem articles: a page reverted to the old
hook-first opening, an opening paragraph grown past a sane word ceiling,
a reintroduced duplicate "short answer" notice block sitting alongside the
new lede, and a missing <p class="lede"> entirely.

Also runs against the real, committed ops/specific_articles.py and
site/articles/*.html, so a future hand edit that drops or rewrites one of
the six opening paragraphs fails this test directly.

Run:  python ops/tests/test_gate_specific_article_direct_answer.py
"""
import html as _html
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import specific_articles as sa                                 # noqa: E402


def _page(lede_html, extra=""):
    return ('<div class="head"><h1>Why you always lose your keys</h1>'
            '<p class="lede">%s</p></div>%s'
            '<h2>Why this is not a memory problem</h2></main>' %
            (lede_html, extra))


def main() -> int:
    fails = []

    answer = "Give them exactly one home, in the exact spot your hand opens."
    want_html = _html.escape(answer, quote=True)

    # 1. Clean page: rendered lede matches the answer exactly. No problems.
    pages = {"p1.html": _page(want_html)}
    problems = preflight.check_specific_article_direct_answer(
        {"p1.html": answer}, pages)
    if problems:
        fails.append("clean page wrongly flagged: %s" % problems)

    # 2. Regression: the old hook-first opening, D12 reverted.
    hook = ("You pat your pockets, check the kitchen counter, and finally "
            "find them on the arm of the sofa.")
    regressed = {"p1.html": _page(_html.escape(hook, quote=True))}
    problems = preflight.check_specific_article_direct_answer(
        {"p1.html": answer}, regressed)
    if not problems:
        fails.append("hook-first regression (pre-D12 shape) NOT caught")

    # 3. No <p class="lede"> at all.
    no_lede = {"p1.html": "<h1>Why you always lose your keys</h1>"
                          "<h2>Why this is not a memory problem</h2></main>"}
    problems = preflight.check_specific_article_direct_answer(
        {"p1.html": answer}, no_lede)
    if not problems:
        fails.append("missing <p class=\"lede\"> entirely NOT caught")

    # 4. Opening paragraph has grown past the word ceiling.
    bloated_text = "Give them exactly one home. " + ("word " * 100)
    bloated = {"p1.html": _page(_html.escape(bloated_text, quote=True))}
    problems = preflight.check_specific_article_direct_answer(
        {"p1.html": bloated_text}, bloated)
    if not problems:
        fails.append("oversized opening paragraph NOT caught")

    # 5. A duplicate "short answer" notice block reintroduced alongside the
    #    new lede, the exact pre-D12 redundancy this fix removed.
    dup_notice = {"p1.html": _page(
        want_html,
        extra='<p class="notice" style="max-width:60ch"><b>The short '
              'answer.</b> Give them exactly one home.</p>')}
    problems = preflight.check_specific_article_direct_answer(
        {"p1.html": answer}, dup_notice)
    if not problems:
        fails.append("reintroduced duplicate short-answer notice NOT caught")

    # 6. An article in the corpus with no built file at all.
    problems = preflight.check_specific_article_direct_answer(
        {"p1.html": answer, "missing.html": answer}, pages)
    if not problems:
        fails.append("specific article missing from the built site NOT caught")

    # 7. Against the real, committed ops/specific_articles.py and
    #    site/articles/*.html: proves all six articles actually ship D12's
    #    opening paragraph today, with no leftover duplicate notice block.
    real_map = {"%s.html" % slug: text
                for slug, text in sa.DIRECT_ANSWERS.items()}
    if len(real_map) != 6:
        fails.append("expected 6 specific articles in the real corpus, "
                     "found %d (has the corpus changed? update this test's "
                     "expectation deliberately if so)" % len(real_map))
    real_pages = {}
    for slug in sa.DIRECT_ANSWERS:
        p = os.path.join(ROOT, "site", "articles", "%s.html" % slug)
        real_pages["%s.html" % slug] = io.open(
            p, encoding="utf-8", errors="replace").read()
    problems = preflight.check_specific_article_direct_answer(real_map, real_pages)
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
